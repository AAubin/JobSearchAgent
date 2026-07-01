import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
import pdfplumber
import yaml
from pathlib import Path
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from tools.search_offers import get_offer_details
from database import get_offer_by_id, get_last_letter_id, update_letter_rating
from config.llm_base_models import AGENT_MODEL, LETTER_MODEL, AGENT_MODEL_COST, LETTER_MODEL_COST

def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).parent / "prompts" / f"{name}.yaml"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt '{name}' not found at {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_profile(file="user_profile.yaml"):
    if file == "user_profile.yaml":
        path = Path(file)
    else:
        path = Path(__file__).parent / "config" / file
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}
    
def save_profile(data, file="user_profile.yaml"):
    with open(file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def load_resume() -> str:
    cv_name = get_saved_cv_name()
    p = Path(__file__).parent.parent / "CVs" / f"{cv_name}.pdf"
    if not p.exists():
        return "CV non trouvé."
    with pdfplumber.open(p) as pdf:
        return "\n".join(
            page.extract_text() or "" for page in pdf.pages
        ).strip()


def get_saved_cv_name() -> str:
    path = Path(__file__).parent.parent / "cv_config.yaml"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        cv_config = yaml.safe_load(f) or {}
    cv_name = cv_config.get("selected_cv_name", "")
    return cv_name

def save_selected_cv_name(cv_name: str):
    path = Path(__file__).parent.parent / "cv_config.yaml"
    cv_config = {"selected_cv_name": cv_name}
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(cv_config, f, allow_unicode=True, sort_keys=False)

def get_resume_lists() -> list:
    cv_dir = Path(__file__).parent.parent / "CVs"
    if not cv_dir.exists():
        return []
    return [f.stem for f in cv_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]

def rate_letter(rating):
    last_letter_id = get_last_letter_id()
    if last_letter_id is not None:
        update_letter_rating(last_letter_id, rating)

def application(offer_id, details=None):
    if details is None:
        offer = get_offer_by_id(offer_id)
        if offer and offer.get("source") == "france_travail":
            details = get_offer_details(offer_id)
            if not details:
                details = offer
        else:
            details = offer
    entreprise_raw = details.get("entreprise", "")
    entreprise = entreprise_raw.get("nom", "N/A") if isinstance(entreprise_raw, dict) else (entreprise_raw or "Entreprise N/A")
    position = details.get("intitule") or details.get("position", "Poste N/A")
    description = details.get("description", "")
    prompt_data = load_prompt("application")
    prompt = prompt_data["template"].format(
        entreprise=entreprise,
        poste=position,
        description=description,
        offer_id=offer_id
    )
    return prompt

def to_markdown(text):
    return text.replace("\n", "  \n")

PRICING = {
    AGENT_MODEL: AGENT_MODEL_COST,
    LETTER_MODEL: LETTER_MODEL_COST
}

class TokenCounterCallback(BaseCallbackHandler):
    def __init__(self):
        self.tokens_by_model = {}

    def on_llm_end(self, response: LLMResult, **kwargs):
        llm_output = response.llm_output or {}
        model = llm_output.get('model', 'unknown')
        usage = llm_output.get('usage', {})
        if model not in self.tokens_by_model:
            self.tokens_by_model[model] = {'input': 0, 'output': 0}
        self.tokens_by_model[model]['input'] += usage.get('input_tokens', 0)
        self.tokens_by_model[model]['output'] += usage.get('output_tokens', 0)

    @property
    def cost(self):
        total = 0.0
        for model, tokens in self.tokens_by_model.items():
            cost_in, cost_out = PRICING.get(model, (3.0, 15.0))
            total += (tokens['input']*cost_in + tokens['output']*cost_out)/1000000
        return total

    @property
    def input_tokens(self):
        return sum(t['input'] for t in self.tokens_by_model.values())
    
    @property
    def output_tokens(self):
        return sum(t['output'] for t in self.tokens_by_model.values())
    
    def to_dict(self):
        return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}
    