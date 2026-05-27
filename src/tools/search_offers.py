import requests
from langchain_core.tools import tool
import os
from database import get_existing_offer_ids, save_offer
from dotenv import load_dotenv
load_dotenv()

VILLES_DEPARTEMENTS = {
    "paris": "75", "lyon": "69", "marseille": "13", "toulouse": "31",
    "bordeaux": "33", "nantes": "44", "strasbourg": "67", "montpellier": "34",
    "rennes": "35", "lille": "59", "nice": "06", "grenoble": "38",
    "reims": "51", "saint-etienne": "42", "toulon": "83", "le havre": "76",
    "dijon": "21", "angers": "49", "nimes": "30", "villeurbanne": "69",
}

def _get_token_france_travail() -> str:
    url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    params = {"realm": "/partenaire"}
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("FRANCE_TRAVAIL_CLIENT_ID"),
        "client_secret": os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET"),
        "scope": "api_offresdemploiv2 o2dsoffre",
    }
    r = requests.post(url, params=params, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def _search_offers_by_department(token: str, poste: str, departement: str, nb_resultats: int) -> list:
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"motsCles": poste, "range": f"0-{nb_resultats - 1}"}
    if departement:
        params["departement"] = departement
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    if not r.text:
        return []
    return [o for o in r.json().get("resultats", []) if not o.get("alternance", False)]

def _get_offer_link(offre: dict) -> str:
    if "lienOffre" in offre and offre["lienOffre"]:
        return offre["lienOffre"]
    elif "id" in offre and offre["id"]:
        return f"https://candidat.francetravail.fr/offres/recherche/detail/{offre['id']}"
    return ""

@tool
def search_offer(poste: str, localisation: str = "", nb_resultats: int = 5) -> str:
    """
    Cherche des offres d'emploi sur France Travail.
    Utilise cet outil quand l'utilisateur veut voir des offres pour un poste.

    Args:
        poste: intitulé du poste recherché (ex: "data scientist")
        localisation: une ou plusieurs villes/départements séparés par des virgules
                      (ex: "Bordeaux", "Bordeaux,Toulouse", "33,31")
        nb_resultats: nombre d'offres à retourner par localisation (défaut: 5)
    """
    try:
        token = _get_token_france_travail()

        localisations = [l.strip() for l in localisation.split(",") if l.strip()] if localisation else [""]

        toutes_offres = []
        vus = set()
        for loc in localisations:
            dept = VILLES_DEPARTEMENTS.get(loc.lower(), loc)
            offres = _search_offers_by_department(token, poste, dept, nb_resultats)
            for o in offres:
                if o["id"] not in vus:
                    vus.add(o["id"])
                    toutes_offres.append(o)

        if not toutes_offres:
            return f"Aucune offre trouvée pour '{poste}'" + (f" à '{localisation}'" if localisation else "") + "."
        
        existing_ids = get_existing_offer_ids([o['id'] for o in toutes_offres])
        nouvelles_offres = [o for o in toutes_offres if o['id'] not in existing_ids]

        if not nouvelles_offres:
            return f"Toutes les offres trouvées pour '{poste}' ont déjà été proposées précédemment."

        zones = ", ".join(localisations) if localisations != [""] else "France"
        lignes = [f"**{len(nouvelles_offres)} nouvelles offres trouvées pour '{poste}' ({zones}) :**\n"]
        for o in nouvelles_offres:
            lien = _get_offer_link(o)
            lignes.append(
                f"- {o['intitule']} | {o.get('entreprise', {}).get('nom', 'Entreprise N/A')}"
                f" | {o.get('lieuTravail', {}).get('libelle', '')} | ID:{o['id']} | [Lien]({lien})"
            )
            save_offer(o['id'], 'france_travail', o['intitule'], o.get('entreprise', {}).get('nom', ''),
                        o.get('lieuTravail', {}).get('libelle', ''), lien)
        return "\n".join(lignes)

    except Exception as e:
        return f"Erreur lors de la recherche : {e}"
    
def get_offer_details(france_travail_id: str) -> dict:
    token = _get_token_france_travail()
    url = f"https://api.francetravail.io/partenaire/offresdemploi/v2/offres/{france_travail_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()