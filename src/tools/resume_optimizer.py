from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from utils import load_prompt, load_resume

load_dotenv()
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3)

@tool
def resume_optimizer(description_offre: str, nom_entreprise: str = "") -> str:
    """
    Analyse le CV par rapport à une offre et propose des modifications concrètes.
    Utilise cet outil quand l'utilisateur veut améliorer son CV pour un poste précis.

    Args:
        description_offre: texte de l'offre ou description du poste
        nom_entreprise: nom de l'entreprise (optionnel)
    """
    cv = load_resume()
    prompt_data = load_prompt("resume_optimizer")
    prompt = prompt_data["template"].format(cv=cv, nom_entreprise=nom_entreprise or 'Non précisée', description_offre=description_offre)

    return llm.invoke(prompt).content