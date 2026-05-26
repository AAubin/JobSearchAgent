import yaml
from pathlib import Path

def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).parent / "prompts" / f"{name}.yaml"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt '{name}' not found at {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
