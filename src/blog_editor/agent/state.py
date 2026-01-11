from typing import TypedDict, Optional
from blog_editor.ghost.models import Post
from blog_editor.agent.suggestions import Suggestion

class AgentState(TypedDict):
    post: Post
    style_guidelines: str
    suggestions: list[Suggestion]
    error: Optional[str]
