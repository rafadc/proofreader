from pydantic import BaseModel
from blog_editor.agent.utils import load_prompts, get_llm_response
from blog_editor.agent.suggestions import Suggestion
import json

class LexicalUpdateResponse(BaseModel):
    lexical_json: str

def create_lexical_update(original_lexical: str, suggestions: list[Suggestion]) -> str:
    prompts = load_prompts()
    system_prompt = prompts["lexical_update_system"]
    
    # Format suggestions for the prompt
    changes_text = "\n".join([
        f"- Change '{s.original_text}' to '{s.proposed_text}' (Reason: {s.reasoning})"
        for s in suggestions
    ])
    
    user_prompt = f"""
Original Lexical JSON:
{original_lexical}

Approved Changes:
{changes_text}

Return the full, valid, updated Lexical JSON string.
"""
    
    try:
        # We expect a structured response containing the JSON string
        # Using a wrapper model to ensure we get a string field containing the JSON
        # rather than the LLM trying to return raw JSON as the message body which might get parsed by OpenAI lib weirdly
        # or we could ask for raw text, but structured output is safer for extraction.
        # However, lexical JSON is complex and recursive. Pydantic models for the full tree are hard.
        # So we ask for a string field 'lexical_json' that contains the dumped JSON.
        
        response = get_llm_response(system_prompt, user_prompt, LexicalUpdateResponse)
        return response.lexical_json
    except Exception as e:
        print(f"Lexical update failed: {e}")
        raise e
