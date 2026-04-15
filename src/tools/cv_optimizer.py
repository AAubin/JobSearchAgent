from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from .utils import charger_cv

load_dotenv()
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3)

@tool
def optimiser_cv(description_offre: str, nom_entreprise: str = "") -> str:
    """
    Analyse le CV par rapport à une offre et propose des modifications concrètes.
    Utilise cet outil quand l'utilisateur veut améliorer son CV pour un poste précis.

    Args:
        description_offre: texte de l'offre ou description du poste
        nom_entreprise: nom de l'entreprise (optionnel)
    """
    cv = charger_cv()
    prompt = f"""Tu es un expert en recrutement français et en optimisation de CV.

CV actuel du candidat :
{cv}

Offre visée :
Entreprise : {nom_entreprise or 'Non précisée'}
Description : {description_offre}

Effectue une analyse en 3 parties :

1. CORRESPONDANCE (points forts)
   - Liste les éléments du CV qui matchent bien l'offre
   - Mots-clés de l'offre déjà présents dans le CV

2. MODIFICATIONS SUGGÉRÉES
   Pour chaque suggestion, donne le format :
   [SECTION] Texte actuel → Texte proposé
   Exemple : [EXPÉRIENCE] "Développement d'outils internes" → "Développement d'outils d'analyse de données (Python, SQL)"
   
   Cible en priorité :
   - Reformulations pour intégrer les mots-clés manquants
   - Réordonner les compétences selon la priorité de l'offre
   - Bullet points d'expérience à renforcer avec des métriques

3. ÉLÉMENTS MANQUANTS
   - Compétences demandées absentes du CV (à acquérir ou à mentionner si tu les as)
   - Certifications ou formations qui renforcerait le dossier

Sois précis et actionnable. Évite les conseils génériques."""

    return llm.invoke(prompt).content