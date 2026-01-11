from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable
from textual.binding import Binding
from blog_editor.ghost.client import GhostClient
from blog_editor.config.settings import settings

class DraftListTable(DataTable):
    BINDINGS = [Binding("q", "quit", "Quit")]

    def action_quit(self):
        self.app.exit()

class DraftListScreen(Screen):
    BINDINGS = [Binding("q", "quit", "Quit")]

    def compose(self):
        yield Header()
        yield DraftListTable()
        yield Footer()

    async def on_mount(self):
        table = self.query_one(DraftListTable)
        table.cursor_type = "row"
        table.add_columns("Title", "Updated At", "Status")
        
        try:
            client = GhostClient(settings.ghost_url, settings.ghost_api_key)
            posts = await client.get_posts(status="draft")
            # Sort by updated_at desc
            posts.sort(key=lambda p: p.updated_at, reverse=True)
            
            for post in posts:
                table.add_row(post.title, str(post.updated_at), post.status, key=post.id)
                self.app.post_map[post.id] = post
                
        except Exception as e:
            self.notify(f"Error fetching drafts: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        post_id = event.row_key.value
        if post_id:
             self.dismiss(post_id)
