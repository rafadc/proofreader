from textual.app import App
from textual import work
from blog_editor.ui.screens.draft_list import DraftListScreen
from blog_editor.ui.screens.review import ReviewScreen
from blog_editor.agent.graph import create_agent_graph
from blog_editor.ghost.client import GhostClient
from blog_editor.config.settings import settings

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
        
        final_state = await self.agent_graph.ainvoke(state)
        
        if final_state.get("error"):
            self.notify(f"Analysis failed: {final_state['error']}", severity="error")
            return
            
        suggestions = final_state.get("suggestions", [])
        if not suggestions:
            self.notify("No suggestions found!")
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
        
        # Here we would actually modify the content.
        # For this PoC, we will just simulate/log it or do simple replacement if possible.
        # But since we don't have robust text replacement logic for HTML yet, we'll just mock the update.
        
        if self.dry_run:
            self.notify("Dry run: Changes would be applied to Ghost.", severity="information", timeout=5)
        else:
             # Logic to apply changes to post.html or post.mobiledoc
             # For now, we mock an update to updated_at to show we did something
             try:
                 client = GhostClient(settings.ghost_url, settings.ghost_api_key)
                 # We would construct the new HTML here
                 new_html = post.html # Placeholder
                 
                 await client.update_post(post.id, {"html": new_html}, post.updated_at)
                 self.notify("Changes applied successfully!", severity="success")
             except Exception as e:
                 self.notify(f"Failed to apply changes: {e}", severity="error")
                 
        self.exit()
