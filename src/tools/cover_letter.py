import re
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from database import save_letter, save_application, get_last_letter_id
from utils import load_prompt, load_resume

load_dotenv()
llm_letter = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3)
llm_profile = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.0)

OUTPUT_DIR = Path(__file__).parent.parent.parent  / "lettres"

def _save_docx(contenu: str, nom_entreprise: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    nom_fichier = re.sub(r"[^\w\-]", "_", nom_entreprise or "entreprise").strip("_")
    chemin = OUTPUT_DIR / f"lettre_motivation_{nom_fichier}.docx"

    doc = Document()

    # Marges
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # Contenu paragraphe par paragraphe
    for ligne in contenu.split("\n"):
        if ligne.startswith(">>"):
            ligne_propre = ligne.lstrip(">>").strip()
        elif ligne.startswith("**"):
            ligne_propre = ligne.lstrip("**").rstrip("**").strip()
        else:
            ligne_propre = ligne
        p = doc.add_paragraph(ligne_propre)
        if ligne.startswith(">>"):
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if ligne.startswith("**"):
            for run in p.runs:
                run.font.bold = True
        p.paragraph_format.space_after = Pt(0)
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = "Calibri"

    doc.save(chemin)
    return chemin

def _extract_content(results) -> str:
    if isinstance(results, list):
        return "\n\n".join([
            r.get("content", r) if isinstance(r, dict) else str(r)
            for r in results
        ])
    return str(results)

def _search_company(nom_entreprise: str, config: RunnableConfig = None) -> str:
    if not nom_entreprise:
        return ""
    try:
        search = TavilySearch(max_results=5)
        official_website = search.invoke(f"{nom_entreprise} site officiel activité produit valeurs")
        press_articles = search.invoke(f"{nom_entreprise} actualités récentes")
        search_results = _extract_content(official_website) + "\n\n" + _extract_content(press_articles)
        prompt_data = load_prompt("company_research")
        prompt = prompt_data["template"].format(nom_entreprise=nom_entreprise, search_results=search_results)
        profil = llm_profile.invoke(prompt, config=config).content
        return profil
    except Exception as e:
        print(f"Erreur lors de la recherche pour {nom_entreprise} : {e}")
        return ""

def _escape_braces(text: str) -> str:
    return text.replace("{", "{{").replace("}", "}}")    

@tool
def write_cover_letter(description_offre: str, nom_entreprise: str = "", offer_id: str = "", config: RunnableConfig = None) -> str:
    """
    Rédige une lettre de motivation personnalisée à partir du CV et de la description de l'offre,
    et la sauvegarde dans un fichier Word (.docx).
    Utilise cet outil quand l'utilisateur veut postuler à une offre.

    Args:
        description_offre: texte de l'offre ou description du poste
        nom_entreprise: nom de l'entreprise (optionnel)
        offer_id: ID de l'offre (optionnel)
    """
    date = datetime.now().strftime("%d %B %Y")
    cv = load_resume()
    prompt_data = load_prompt("cover_letter")
    prompt = prompt_data["template"].format(
        cv=cv, 
        nom_entreprise=nom_entreprise or 'Non précisée', 
        description_offre=_escape_braces(description_offre), 
        informations_entreprise=_escape_braces(_search_company(nom_entreprise, config=config)),
        date=date
    )

    lettre = llm_letter.invoke(prompt, config=config).content
    chemin = _save_docx(lettre, nom_entreprise)
    nb_mots = len(lettre.split())
    company_is_present = nom_entreprise.strip().lower() in lettre.lower() if nom_entreprise else False
    save_letter(nom_entreprise, str(chemin), nb_mots, company_is_present)
    if offer_id:
        save_application(offer_id, id_letter=get_last_letter_id())
    return f"{lettre}\n\n---\nLettre sauvegardée : {chemin}"
