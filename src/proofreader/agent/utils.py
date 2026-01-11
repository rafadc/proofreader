from typing import Any
import yaml
from pathlib import Path
from openai import OpenAI
from proofreader.config.settings import settings

client = OpenAI(api_key=settings.openai_api_key)

def load_prompts() -> dict[str, str]:
    prompts_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
    with open(prompts_path, "r") as f:
        return yaml.safe_load(f)

def get_llm_response(system_prompt: str, user_prompt: str, response_model=None) -> Any:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    kwargs = {
        "model": "gpt-5.2",
        "messages": messages,
    }
    if response_model:
        kwargs["response_format"] = response_model

    response = client.beta.chat.completions.parse(**kwargs)
    return response.choices[0].message.parsed
