from textual.widgets import Static
from rich.text import Text
from rich.table import Table
import difflib

class DiffViewer(Static):
    def update_diff(self, original: str, proposed: str):
        diff = difflib.ndiff(original.splitlines(), proposed.splitlines())
        
        table = Table(show_header=True, header_style="bold magenta", expand=True, show_lines=False)
        table.add_column("Original", ratio=1)
        table.add_column("Proposed", ratio=1)

        for line in diff:
            code = line[:2]
            content = line[2:]
            
            if code == '- ':
                table.add_row(Text(content, style="bold red on #330000"), "")
            elif code == '+ ':
                table.add_row("", Text(content, style="bold green on #003300"))
            elif code == '  ':
                table.add_row(Text(content), Text(content))
            # Ignore '?' lines
            
        self.update(table)
