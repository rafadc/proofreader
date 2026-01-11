from proofreader.agent.state import AgentState
from proofreader.agent.utils import load_prompts, get_llm_response
from proofreader.ghost.client import GhostClient
from proofreader.config.settings import settings
from pydantic import BaseModel

class StyleAnalysis(BaseModel):
    guidelines: str

async def analyze_style(state: AgentState) -> dict:
    prompts = load_prompts()
    client = GhostClient(settings.ghost_url, settings.ghost_api_key)
    
    past_posts_text = ""
    try:
        # Retrieve the last 15 published posts to understand the blog's style
        past_posts = await client.get_posts(limit=15, status="published")
        if past_posts:
            # Concatenate the content of past posts. 
            # We prefer HTML, but fallback to mobiledoc or raw text if needed.
            # Truncate each post to avoid exploding context if they are huge? 
            # For now, let's assume they fit.
            past_posts_text = "\n\n---\n\n".join(
                [f"Title: {p.title}\nContent:\n{p.html or p.mobiledoc or p.lexical or ''}" for p in past_posts]
            )
    except Exception as e:
        print(f"Failed to retrieve past posts: {e}")

    system_prompt = prompts["style_analysis_system"]
    
    if past_posts_text:
        user_prompt = (
            f"Here are the last {len(past_posts)} published posts from the blog:\n\n"
            f"{past_posts_text}\n\n"
            "Analyze these posts to create a comprehensive style guide for this blog."
        )
    else:
        # Fallback to analyzing the current draft if no past posts are available
        print("No past posts available for style analysis. Using current draft.")
        user_prompt = (
            f"Analyze the style of this text:\n\n"
            f"{state['post'].html or state['post'].mobiledoc or ''}"
        )

    try:
        response = get_llm_response(system_prompt, user_prompt, StyleAnalysis)
        return {"style_guidelines": response.guidelines}
    except Exception as e:
        print(f"Style analysis failed: {e}")
        return {"style_guidelines": "Standard professional blog style."}
