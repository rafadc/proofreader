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
        
        # Strategy 1: Exact match
        if original in text:
            new_text = text.replace(original, replacement, 1)
            node["text"] = new_text
            count_ref['count'] += 1
            return
            
        # Strategy 2: Exact Match with stripped original (common if LLM includes surrounding whitespace)
        # Only try if original has whitespace to strip
        original_stripped = original.strip()
        if original_stripped and original_stripped != original and original_stripped in text:
             # We found the stripped version. Now we need to decide how to replace.
             # If we replace the stripped version with the full replacement, we might double spaces if the replacement has spaces.
             # But we can't easily know if the replacement's spaces were meant for the stripped bounds or not.
             # We'll assume the replacement is intended to replace the *semantic* content, so we replace the stripped match.
             # Risk: "a sentence." -> match "sentence" -> replace " sentence." -> "a  sentence."
             # Heuristic: If we stripped the original, we should probably strip the replacement corresponding to the stripped sides?
             # Too complex to guess. Let's just do the replacement of the stripped key.
             new_text = text.replace(original_stripped, replacement, 1)
             node["text"] = new_text
             count_ref['count'] += 1
             return

    if "children" in node:
        for child in node["children"]:
            replace_in_lexical_node(child, original, replacement, count_ref)

# ... inside apply_changes ...

        if use_lexical:
            try:
                lexical_data = json.loads(post.lexical)
                for suggestion in approved_suggestions:
                    count_ref = {'count': 0}
                    # Unescape original text as the agent sees HTML which might be escaped
                    original_clean = html_lib.unescape(suggestion.original_text)
                    
                    if "root" in lexical_data:
                        # Attempt 1: Standard unescaped
                        replace_in_lexical_node(lexical_data["root"], original_clean, suggestion.proposed_text, count_ref)
                    
                    if count_ref['count'] == 0:
                         # Attempt 2: Try with original raw (just in case)
                        replace_in_lexical_node(lexical_data["root"], suggestion.original_text, suggestion.proposed_text, count_ref)
                    
                    if count_ref['count'] == 0:
                        self.notify(f"Could not find text in Lexical: {suggestion.original_text[:20]}...", severity="warning")
                    else:
                        applied_count += 1
                
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
