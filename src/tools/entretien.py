from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from .utils import charger_cv

load_dotenv()
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.5)

@tool
def preparer_entretien(description_poste: str, type_entretien: str = "général") -> str:
    """
    Génère des questions d'entretien probables et des conseils de préparation.
    Utilise cet outil quand l'utilisateur prépare un entretien.
    
    Args:
        description_poste: description du poste ou de l'entreprise
        type_entretien: "général", "technique", "RH" ou "cas pratique"
    """
    cv = charger_cv()
    prompt = f"""Tu es un coach en entretien d'embauche expert du marché français.

CV du candidat :
{cv}

Poste visé : {description_poste}
Type d'entretien : {type_entretien}

Génère :
1. 5 questions très probables pour ce profil/poste, avec la logique derrière chaque question
2. Pour chaque question, une piste de réponse personnalisée basée sur le CV
3. 3 questions à poser au recruteur (démarche proactive)
4. Un point de vigilance spécifique à ce profil

Sois concret et adapté au contexte français (codes culturels, formulations RH françaises)."""

    response = llm.invoke(prompt)
    return response.content