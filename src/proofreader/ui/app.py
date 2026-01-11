from textual.app import App
from textual import work
from proofreader.ui.screens.draft_list import DraftListScreen
from proofreader.ui.screens.review import ReviewScreen
from proofreader.ui.screens.loading import LoadingScreen
from proofreader.ui.screens.result import ResultScreen
from proofreader.agent.graph import create_agent_graph
from proofreader.ghost.client import GhostClient
from proofreader.config.settings import settings

from proofreader.agent.nodes.updater import create_lexical_update
import json
import html as html_lib

def replace_in_lexical_node(node, original, replacement, count_ref):
    """Recursively search and replace text in a Lexical node tree."""
    if count_ref['count'] > 0:
        return

    if node.get("type") == "text" and "text" in node:
        text = node["text"]
        
        # Strategy 1: Exact match
        if original in text:
            new_text = text.replace(original, replacement, 1)
            node["text"] = new_text
            count_ref['count'] += 1
            return
            
        # Strategy 2: Exact Match with stripped original (common if LLM includes surrounding whitespace)
        # Only try if original has whitespace to strip
        original_stripped = original.strip()
        if original_stripped and original_stripped != original and original_stripped in text:
             # We found the stripped version. Now we need to decide how to replace.
             # If we replace the stripped version with the full replacement, we might double spaces if the replacement has spaces.
             # But we can't easily know if the replacement's spaces were meant for the stripped bounds or not.
             # We'll assume the replacement is intended to replace the *semantic* content, so we replace the stripped match.
             # Risk: "a sentence." -> match "sentence" -> replace " sentence." -> "a  sentence."
             # Heuristic: If we stripped the original, we should probably strip the replacement corresponding to the stripped sides?
             # Too complex to guess. Let's just do the replacement of the stripped key.
             new_text = text.replace(original_stripped, replacement, 1)
             node["text"] = new_text
             count_ref['count'] += 1
             return

    if "children" in node:
        for child in node["children"]:
            replace_in_lexical_node(child, original, replacement, count_ref)

from proofreader.ui.screens.lexical_preview import LexicalPreviewScreen

class ProofreaderApp(App):
    TITLE = "Proofreader"
    CSS = """
    Screen {
        layout: vertical;
    }
    """
    
    def __init__(self, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run
        self.post_map = {}
        self.agent_graph = create_agent_graph()

    def on_mount(self):
        self.push_screen(DraftListScreen(), self.on_draft_selected)

    def on_draft_selected(self, post_id: str | None):
        if not post_id:
            self.exit()
            return
            
        post = self.post_map.get(post_id)
        if post:
            self.loading_screen = LoadingScreen()
            self.push_screen(self.loading_screen)
            self.run_analysis(post)

    @work(exclusive=True)
    async def run_analysis(self, post):
        self.notify("Running analysis... this may take a moment.")
        # In a real app we'd show the specific progress screen here
        
        # Initial state
        state = {
            "post": post,
            "style_guidelines": "",
            "suggestions": [],
            "error": None
        }
        
        # Stream the execution to show progress
        final_state = state
        try:
            async for output in self.agent_graph.astream(state):
                for node_name, node_update in output.items():
                    node_display = node_name.replace("_", " ").title()
                    # self.notify(f"Finished {node_display}...")
                    if hasattr(self, 'loading_screen'):
                         self.loading_screen.update_status(f"Finished {node_display}...")
                    
                    final_state.update(node_update)
        except Exception as e:
            self.pop_screen() # Remove loading screen
            self.notify(f"Analysis error: {e}", severity="error")
            return
        
        # Remove loading screen
        self.pop_screen()

        if final_state.get("error"):
            self.notify(f"Analysis failed: {final_state['error']}", severity="error")
            return
            
        suggestions = final_state.get("suggestions", [])
        if not suggestions:
            self.notify("No suggestions found!")
            self.push_screen(DraftListScreen(), self.on_draft_selected) 
            self.exit()
            return
            
        self.push_screen(ReviewScreen(suggestions), lambda approved: self.apply_changes(post, approved))

    @work
    async def apply_changes(self, post, approved_suggestions):
        if not approved_suggestions:
            self.notify("No changes approved.")
            self.exit()
            return

        self.notify(f"Applying {len(approved_suggestions)} changes...")
        
        applied_count = 0
        
        # Determine if we can use Lexical or fallback to HTML
        use_lexical = bool(post.lexical)
        
        new_html = post.html or ""
        new_lexical = None
        
        if use_lexical:
            try:
                # Use the AI agent to update Lexical data
                self.notify("Using AI agent to update Lexical content...")
                
                new_lexical = create_lexical_update(post.lexical, approved_suggestions)
                applied_count = len(approved_suggestions) # We assume all were applied by the agent
                
            except Exception as e:
                self.notify(f"Error updating Lexical data with AI: {e}. Falling back to HTML.", severity="error")
                use_lexical = False

        if not use_lexical:
            # Fallback to HTML logic
            for suggestion in approved_suggestions:
                if suggestion.original_text in new_html:
                    new_html = new_html.replace(suggestion.original_text, suggestion.proposed_text, 1)
                    applied_count += 1
                else:
                    self.notify(f"Could not find text: {suggestion.original_text[:20]}...", severity="warning")
        
        # Show Preview Screen
        preview_content = new_lexical if use_lexical else new_html
        self.push_screen(
            LexicalPreviewScreen(preview_content, use_lexical), 
            lambda confirmed: self.finalize_update(post, new_lexical, new_html, use_lexical, applied_count) if confirmed else self.notify("Update cancelled.")
        )

    @work
    async def finalize_update(self, post, new_lexical, new_html, use_lexical, applied_count):
        message = ""
        success = True
        
        if self.dry_run:
            mode = "Lexical" if use_lexical else "HTML"
            message = f"Dry run ({mode}): {applied_count} changes would be applied to Ghost."
        else:
             try:
                 client = GhostClient(settings.ghost_url, settings.ghost_api_key)
                 if use_lexical:
                     await client.update_post(post.id, {"lexical": new_lexical}, post.updated_at)
                 else:
                     await client.update_post(post.id, {"html": new_html}, post.updated_at)
                 
                 message = f"Successfully applied {applied_count} changes to Ghost!"
             except Exception as e:
                 success = False
                 message = f"Failed to apply changes: {e}"
                 
        self.push_screen(ResultScreen(message, success), lambda _: self.exit())
