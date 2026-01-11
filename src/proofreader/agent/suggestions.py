from enum import Enum
from pydantic import BaseModel, Field

class SuggestionType(str, Enum):
    TYPO = "typo"
    STRUCTURE = "structure"
    COHERENCE = "coherence"

class Suggestion(BaseModel):
    type: SuggestionType
    location: str = Field(description="Description of where the issue was found, e.g. 'Paragraph 2, sentence 1'")
    original_text: str = Field(description="The exact text snippet that needs changing")
    proposed_text: str = Field(description="The proposed replacement text")
    reasoning: str = Field(description="Explanation of why this change is suggested")

class SuggestionList(BaseModel):
    suggestions: list[Suggestion]
