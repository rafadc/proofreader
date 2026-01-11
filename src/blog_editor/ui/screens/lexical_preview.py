from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, TextArea
from textual.containers import Container, Horizontal
from textual.binding import Binding
import json

class LexicalPreviewScreen(Screen):
    BINDINGS = [
        Binding("y", "confirm", "Confirm"),
        Binding("n", "cancel", "Cancel"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    LexicalPreviewScreen {
        layout: vertical;
    }

    .preview-container {
        height: 1fr;
        border: solid $accent;
    }

    .buttons {
        height: auto;
        dock: bottom;
        padding: 1;
        align: center middle;
    }

    Button {
        margin: 0 2;
    }
    """

    def __init__(self, content: str, is_lexical: bool, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_lexical = is_lexical

    def compose(self):
        yield Header()
        yield Static("Preview of the Final Content to be sent to Ghost:", classes="header-text")
        
        # Pretty print JSON if it is lexical
        display_content = self.content
        if self.is_lexical:
            try:
                parsed = json.loads(self.content)
                display_content = json.dumps(parsed, indent=2)
            except:
                pass
        
        yield TextArea(display_content, language="json" if self.is_lexical else "html", read_only=True, classes="preview-container")
        
        yield Horizontal(
            Button("Confirm Update (y)", variant="success", id="confirm"),
            Button("Cancel (n)", variant="error", id="cancel"),
            classes="buttons"
        )
        yield Footer()

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.action_confirm()
        elif event.button.id == "cancel":
            self.action_cancel()
