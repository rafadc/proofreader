from blog_editor.agent.state import AgentState
from blog_editor.agent.utils import load_prompts, get_llm_response
from blog_editor.agent.suggestions import SuggestionList

def correct_typos(state: AgentState) -> dict:
    prompts = load_prompts()
    system_prompt = prompts["typo_correction_system"].format(style_guidelines=state.get("style_guidelines", ""))
    
    # We need to process the content. The post might be HTML or Mobiledoc.
    # For simplicity, assuming we can extract text or pass the raw content.
    # Validating/Parsing Mobiledoc is complex. 
    # Let's assume we are working with HTML/text representation for analysis.
    content = state['post'].html or ""
    
    user_prompt = f"Check this content for typos:\n\n{content}"
    
    try:
        response = get_llm_response(system_prompt, user_prompt, SuggestionList)
        return {"suggestions": state.get("suggestions", []) + response.suggestions}
    except Exception as e:
        print(f"Typo correction failed: {e}")
        return {}
