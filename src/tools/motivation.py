import re
from pathlib import Path
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt, Cm
from database import save_letter
from prompt_loader import load_prompt

from .utils import charger_cv

load_dotenv()
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "lettres"

def _sauvegarder_docx(contenu: str, nom_entreprise: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    nom_fichier = re.sub(r"[^\w\-]", "_", nom_entreprise or "entreprise").strip("_")
    chemin = OUTPUT_DIR / f"lettre_{nom_fichier}.docx"

    doc = Document()

    # Marges
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # Contenu paragraphe par paragraphe
    for ligne in contenu.split("\n"):
        p = doc.add_paragraph(ligne)
        p.paragraph_format.space_after = Pt(0)
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = "Calibri"

    doc.save(chemin)
    return chemin

def _rechercher_entreprise(nom_entreprise: str) -> str:
    
    return f"Informations sur {nom_entreprise} : ... (fonction à implémenter)"

@tool
def rediger_lettre_motivation(description_offre: str, nom_entreprise: str = "") -> str:
    """
    Rédige une lettre de motivation personnalisée à partir du CV et de la description de l'offre,
    et la sauvegarde dans un fichier Word (.docx).
    Utilise cet outil quand l'utilisateur veut postuler à une offre.

    Args:
        description_offre: texte de l'offre ou description du poste
        nom_entreprise: nom de l'entreprise (optionnel)
    """
    cv = charger_cv()
    prompt_data = load_prompt("motivation")
    prompt = prompt_data["template"].format(cv=cv, nom_entreprise=nom_entreprise or 'Non précisée', description_offre=description_offre)

    lettre = llm.invoke(prompt).content
    chemin = _sauvegarder_docx(lettre, nom_entreprise)
    nb_mots = len(lettre.split())
    company_is_present = nom_entreprise.strip().lower() in lettre.lower() if nom_entreprise else False
    save_letter(nom_entreprise, chemin, nb_mots, company_is_present)
    return f"{lettre}\n\n---\nLettre sauvegardée : {chemin}"