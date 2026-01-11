from textual.widgets import ProgressBar, Static
from textual.containers import Vertical

class AgentProgress(Vertical):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_bar = ProgressBar(total=4, show_eta=False)
        self.status_label = Static("Waiting to start...")
        
    def compose(self):
        yield self.status_label
        yield self.progress_bar
        
    def update_step(self, step_name: str, step_index: int):
        self.status_label.update(f"Running: {step_name}")
        self.progress_bar.progress = step_index
