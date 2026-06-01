from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from utils import load_prompt, load_resume

load_dotenv()
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.5)

@tool
def interview_advice(description_poste: str, type_entretien: str = "général") -> str:
    """
    Génère des questions d'entretien probables et des conseils de préparation.
    Utilise cet outil quand l'utilisateur prépare un entretien.
    
    Args:
        description_poste: description du poste ou de l'entreprise
        type_entretien: "général", "technique", "RH" ou "cas pratique"
    """
    cv = load_resume()

    prompt_data = load_prompt("interview")
    prompt = prompt_data["template"].format(cv=cv, description_poste=description_poste, type_entretien=type_entretien)

    response = llm.invoke(prompt)
    return response.content