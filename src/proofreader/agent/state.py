from typing import TypedDict, Optional
from proofreader.ghost.models import Post
from proofreader.agent.suggestions import Suggestion

class AgentState(TypedDict):
    post: Post
    style_guidelines: str
    suggestions: list[Suggestion]
    error: Optional[str]
