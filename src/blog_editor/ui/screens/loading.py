from textual.screen import Screen
from textual.widgets import LoadingIndicator, Label
from textual.containers import Container, Vertical

class LoadingScreen(Screen):
    CSS = """
    LoadingScreen {
        align: center middle;
    }
    
    Container {
        width: auto;
        height: auto;
        border: solid green;
        padding: 1 2;
        background: $surface;
    }
    
    LoadingIndicator {
        height: 1;
        margin-bottom: 1;
        color: $accent;
    }
    
    Label {
        width: 100%;
        text-align: center;
    }
    """
    
    def compose(self):
        with Container():
            yield LoadingIndicator()
            yield Label("Initializing analysis...", id="loading-label")
            
    def update_status(self, message: str):
        self.query_one("#loading-label", Label).update(message)
