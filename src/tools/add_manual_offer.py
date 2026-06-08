from langchain_core.tools import tool
from tavily import TavilyClient
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from utils import load_prompt
import uuid
import json
import os
from database import save_offer
from dotenv import load_dotenv
load_dotenv()

@tool
def add_manual_offer(lien: str, intitule: str = "", entreprise: str = "", lieu: str = "", description: str = "", config: RunnableConfig = None) -> str:
    """
    Permet à l'utilisateur d'ajouter manuellement une offre d'emploi à la base de données.
    Utilise cet outil quand l'utilisateur veut ajouter une offre qu'il a trouvée lui-même.
    Si toutes les informations ne sont pas fournies, TavilyExtract tentera d'extraire les informations manquantes de l'offre d'emploi à partir du lien (intitulé, entreprise, lieu et description).

    Args:
        lien: URL vers l'offre d'emploi
        intitule: intitulé du poste (ex: "data scientist")
        entreprise: nom de l'entreprise (ex: "Google")
        lieu: localisation du poste (ex: "Paris")
        description: description de l'offre d'emploi
    """
    try:
        if not lien:
            return "Le lien de l'offre d'emploi est requis pour ajouter une offre manuellement."
        if not intitule or not entreprise or not lieu or not description:
            tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            offer_extract = tavily.extract(urls=[lien], query="job title, company, location and description of a job offer")
            if offer_extract['results']:
                offer_content = offer_extract['results'][0]['raw_content']
                llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.0)
                prompt_data = load_prompt('manual_offer')
                prompt = prompt_data['template'].format(raw_content=offer_content)
                content = llm.invoke(prompt, config=config).content
                if "```" in content:
                    content = content.split("```")[1].lstrip("json").strip()
                offer_data = json.loads(content)
                intitule = offer_data.get("intitule", "")
                entreprise = offer_data.get("entreprise", "")
                lieu = offer_data.get("lieu", "")
                description = offer_data.get("description", "")
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'offre : {str(e)}")
    
    offer_id = uuid.uuid4().hex[:8].upper()
    save_offer(offer_id, 'manual', intitule, entreprise, lieu, lien, description, 1)
    return f"Offre ajoutée avec l'id {offer_id}: {intitule} chez {entreprise} à {lieu}."
