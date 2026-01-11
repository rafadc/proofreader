from blog_editor.agent.state import AgentState
from blog_editor.agent.utils import load_prompts, get_llm_response
from pydantic import BaseModel

class StyleAnalysis(BaseModel):
    guidelines: str

def analyze_style(state: AgentState) -> dict:
    prompts = load_prompts()
    # In a real scenario, we would retrieve past posts. 
    # For now, we'll just analyze the current text as a starting point 
    # or assume we have some context. 
    # The spec mentions retrieving last 10-15 posts. 
    # TODO: Implement retrieval of past posts context
    
    # Just setting a placeholder analysis if we have no past posts
    # Or we can ask the LLM to infer style from the draft itself if it's long enough
    
    system_prompt = prompts["style_analysis_system"]
    user_prompt = f"Analyze the style of this text:\n\n{state['post'].html or state['post'].mobiledoc or ''}"
    
    # We expect a string or a structured object? Spec says "Extract blog style guidelines"
    # Let's just get any text for now to put in the guidelines string
    
    # Note: get_llm_response with response_model requires a pydantic model.
    # We can define a simple one.
    
    try:
        response = get_llm_response(system_prompt, user_prompt, StyleAnalysis)
        return {"style_guidelines": response.guidelines}
    except Exception as e:
        print(f"Style analysis failed: {e}")
        return {"style_guidelines": "Standard professional blog style."}
