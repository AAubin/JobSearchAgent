from langchain_core.tools import tool
import uuid
from database import save_offer

@tool
def add_manual_offer(intitule: str, entreprise: str, lieu: str, lien: str, description: str) -> str:
    """
    Permet à l'utilisateur d'ajouter manuellement une offre d'emploi à la base de données.
    Utilise cet outil quand l'utilisateur veut ajouter une offre qu'il a trouvée lui-même.

    Args:
        intitule: intitulé du poste (ex: "data scientist")
        entreprise: nom de l'entreprise (ex: "Google")
        lieu: localisation du poste (ex: "Paris")
        lien: URL vers l'offre d'emploi
        description: description de l'offre d'emploi
    """
    offer_id = uuid.uuid4().hex[:8].upper()
    save_offer(offer_id, 'manual', intitule, entreprise, lieu, lien, description, 1)
    return f"Offre ajoutée : {intitule} chez {entreprise} à {lieu}."