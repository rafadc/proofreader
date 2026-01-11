from textual.widgets import Static
from rich.text import Text
import difflib

class DiffViewer(Static):
    def update_diff(self, original: str, proposed: str):
        # Using difflib to generate a diff
        # This is a basic implementation. Ideally we want character-level highlighting.
        # Rich doesn't fully support git-style diff highlighting out of the box for text blocks 
        # in the way `git diff` does mostly line based, but we can do a simple visualization.
        
        # A simple approach is to show original and proposed side-by-side or stacked.
        # Ore use ndiff.
        
        diff = difflib.ndiff(original.splitlines(keepends=True), proposed.splitlines(keepends=True))
        
        result = Text()
        for line in diff:
            if line.startswith('-'):
                result.append(line, style="bold red")
            elif line.startswith('+'):
                result.append(line, style="bold green")
            elif line.startswith('?'):
                 pass # Skip the indicator lines for now
            else:
                result.append(line)
        
        self.update(result)
