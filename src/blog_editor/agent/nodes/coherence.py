from blog_editor.agent.state import AgentState
from blog_editor.agent.utils import load_prompts, get_llm_response
from blog_editor.agent.suggestions import SuggestionList

def check_coherence(state: AgentState) -> dict:
    prompts = load_prompts()
    system_prompt = prompts["coherence_check_system"].format(style_guidelines=state.get("style_guidelines", ""))
    content = state['post'].html or ""
    
    user_prompt = f"Check coherence:\n\n{content}"
    
    try:
        response = get_llm_response(system_prompt, user_prompt, SuggestionList)
        return {"suggestions": state.get("suggestions", []) + response.suggestions}
    except Exception as e:
        print(f"Coherence check failed: {e}")
        return {}
