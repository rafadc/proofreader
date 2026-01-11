from textual.app import App
from textual import work
from blog_editor.ui.screens.draft_list import DraftListScreen
from blog_editor.ui.screens.review import ReviewScreen
from blog_editor.ui.screens.loading import LoadingScreen
from blog_editor.ui.screens.result import ResultScreen
from blog_editor.agent.graph import create_agent_graph
from blog_editor.ghost.client import GhostClient
from blog_editor.config.settings import settings

import json
import html as html_lib

def replace_in_lexical_node(node, original, replacement, count_ref):
    """Recursively search and replace text in a Lexical node tree."""
    if count_ref['count'] > 0:
        return

    if node.get("type") == "text" and "text" in node:
        text = node["text"]
        if original in text:
            # Replace first occurrence
            new_text = text.replace(original, replacement, 1)
            node["text"] = new_text
            count_ref['count'] += 1
            return
    
    if "children" in node:
        for child in node["children"]:
            replace_in_lexical_node(child, original, replacement, count_ref)

class BlogEditorApp(App):
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
        
        message = ""
        success = True
        applied_count = 0
        
        # Determine if we can use Lexical or fallback to HTML
        use_lexical = bool(post.lexical)
        
        new_html = post.html or ""
        new_lexical = None
        
        if use_lexical:
            try:
                lexical_data = json.loads(post.lexical)
                for suggestion in approved_suggestions:
                    count_ref = {'count': 0}
                    # Unescape original text as the agent sees HTML which might be escaped
                    original_clean = html_lib.unescape(suggestion.original_text)
                    
                    if "root" in lexical_data:
                        replace_in_lexical_node(lexical_data["root"], original_clean, suggestion.proposed_text, count_ref)
                    
                    if count_ref['count'] > 0:
                        applied_count += 1
                    else:
                         # Try with the raw string just in case
                        count_ref['count'] = 0
                        replace_in_lexical_node(lexical_data["root"], suggestion.original_text, suggestion.proposed_text, count_ref)
                        if count_ref['count'] > 0:
                             applied_count += 1
                        else:
                             self.notify(f"Could not find text in Lexical: {suggestion.original_text[:20]}...", severity="warning")
                
                new_lexical = json.dumps(lexical_data)
                
            except Exception as e:
                self.notify(f"Error parsing Lexical data: {e}. Falling back to HTML.", severity="error")
                use_lexical = False

        if not use_lexical:
            # Fallback to HTML logic
            for suggestion in approved_suggestions:
                if suggestion.original_text in new_html:
                    new_html = new_html.replace(suggestion.original_text, suggestion.proposed_text, 1)
                    applied_count += 1
                else:
                    self.notify(f"Could not find text: {suggestion.original_text[:20]}...", severity="warning")
        
        if self.dry_run:
            mode = "Lexical" if use_lexical else "HTML"
            message = f"Dry run ({mode}): {applied_count} changes would be applied to Ghost (out of {len(approved_suggestions)} approved)."
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
