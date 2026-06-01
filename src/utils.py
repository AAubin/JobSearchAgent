import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
import pdfplumber
import yaml
from pathlib import Path
from tools.search_offers import get_offer_details
from database import get_offer_by_id, get_last_letter_id, update_letter_rating


def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).parent / "prompts" / f"{name}.yaml"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt '{name}' not found at {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_resume(chemin: str = "cv.pdf") -> str:
    p = Path(chemin)
    if not p.exists():
        return "CV non trouvé."
    if p.suffix.lower() == ".pdf":
        with pdfplumber.open(p) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            ).strip()
    return p.read_text(encoding="utf-8")

def calculate_session_cost(token_count):
    inputs_tokens = token_count["input_tokens"]
    output_tokens = token_count["output_tokens"]
    cost_input_tokens_by_million = 3.0 #USD
    cost_output_tokens_by_million = 15.0 #USD
    return (inputs_tokens * cost_input_tokens_by_million + output_tokens * cost_output_tokens_by_million) / 1000000

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

