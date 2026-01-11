from blog_editor.agent.nodes.style import analyze_style
from blog_editor.agent.nodes.typos import correct_typos
from blog_editor.agent.suggestions import Suggestion, SuggestionType

def test_analyze_style(sample_post, mock_openai):
    # Mocking the parsed response
    mock_choice = mock_openai.beta.chat.completions.parse.return_value.choices[0]
    mock_choice.message.parsed.guidelines = "Use active voice."
    
    state = {"post": sample_post, "style_guidelines": "", "suggestions": []}
    result = analyze_style(state)
    
    assert result["style_guidelines"] == "Use active voice."

def test_correct_typos(sample_post, mock_openai):
    # Mocking suggestions
    mock_choice = mock_openai.beta.chat.completions.parse.return_value.choices[0]
    mock_choice.message.parsed.suggestions = [
        Suggestion(
            type=SuggestionType.TYPO,
            location="Para 1",
            original_text="typo",
            proposed_text="typographical error",
            reasoning="Spelling"
        )
    ]
    
    state = {"post": sample_post, "style_guidelines": "Style", "suggestions": []}
    result = correct_typos(state)
    
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0].original_text == "typo"
