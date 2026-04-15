import re
from pathlib import Path
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt, Cm

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
    prompt = f"""Tu es un expert en recrutement français.
Rédige une lettre de motivation professionnelle en français (300-400 mots).

CV du candidat :
{cv}

Offre visée :
Entreprise : {nom_entreprise or 'Non précisée'}
Description : {description_offre}

Consignes :
- Ton professionnel mais naturel
- Mets en avant les compétences du CV qui correspondent à l'offre
- Structure : accroche → compétences pertinentes → motivation → conclusion
- Évite les formules génériques comme "Passionné par..."
- Termine par une formule de politesse adaptée au contexte français"""

    lettre = llm.invoke(prompt).content
    chemin = _sauvegarder_docx(lettre, nom_entreprise)
    return f"{lettre}\n\n---\nLettre sauvegardée : {chemin}"