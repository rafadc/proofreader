from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Container, Horizontal
from textual.binding import Binding
from proofreader.ui.widgets.diff import DiffViewer

class ReviewScreen(Screen):
    BINDINGS = [
        Binding("y", "approve", "Approve"),
        Binding("n", "reject", "Reject"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, suggestions: list, **kwargs):
        super().__init__(**kwargs)
        self.suggestions = suggestions
        self.current_index = 0
        self.approved_suggestions = []

    def compose(self):
        yield Header()
        yield Container(
            Static(id="suggestion_info"),
            DiffViewer(id="diff_viewer"),
            Static(id="reasoning"),
            Horizontal(
                Button("Approve (y)", variant="success", id="approve"),
                Button("Reject (n)", variant="error", id="reject"),
                classes="buttons"
            )
        )
        yield Footer()

    def on_mount(self):
        self.show_current_suggestion()

    def show_current_suggestion(self):
        if self.current_index < len(self.suggestions):
            s = self.suggestions[self.current_index]
            self.query_one("#suggestion_info", Static).update(
                f"Suggestion {self.current_index + 1}/{len(self.suggestions)} - Type: {s.type.value} - Location: {s.location}"
            )
            self.query_one("#diff_viewer", DiffViewer).update_diff(s.original_text, s.proposed_text)
            self.query_one("#reasoning", Static).update(f"Reasoning: {s.reasoning}")
        else:
             self.dismiss(self.approved_suggestions)

    def action_approve(self):
        if self.current_index < len(self.suggestions):
            self.approved_suggestions.append(self.suggestions[self.current_index])
            self.current_index += 1
            self.show_current_suggestion()

    def action_reject(self):
        if self.current_index < len(self.suggestions):
            self.current_index += 1
            self.show_current_suggestion()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "approve":
            self.action_approve()
        elif event.button.id == "reject":
            self.action_reject()
