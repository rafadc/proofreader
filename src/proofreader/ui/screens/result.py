from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Container, Vertical
from textual.binding import Binding

class ResultScreen(Screen):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    ResultScreen {
        align: center middle;
    }

    Container {
        width: 60%;
        height: auto;
        border: solid $accent;
        padding: 2;
        background: $surface;
        align: center middle;
    }

    .result-message {
        text-align: center;
        margin-bottom: 2;
        width: 100%;
    }

    .success {
        color: $success;
        text-style: bold;
    }

    .error {
        color: $error;
        text-style: bold;
    }
    
    Button {
        width: 100%;
    }
    """

    def __init__(self, message: str, success: bool, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.success = success

    def compose(self):
        yield Header()
        with Container():
            yield Static(self.message, classes="result-message " + ("success" if self.success else "error"))
            yield Button("Exit", variant="primary", id="exit_btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "exit_btn":
            self.dismiss()
