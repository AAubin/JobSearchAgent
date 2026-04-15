from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from tools.cv_optimizer import optimiser_cv
from tools.veille import rechercher_offres
from tools.motivation import rediger_lettre_motivation
from tools.entretien import preparer_entretien

from dotenv import load_dotenv
load_dotenv()

def creer_agent() -> CompiledStateGraph:
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    tools = [rechercher_offres, optimiser_cv, rediger_lettre_motivation, preparer_entretien]

    system_prompt = """Tu es un assistant expert en recherche d'emploi en France.
Tu aides l'utilisateur avec 3 actions :
- Trouver des offres d'emploi (France Travail) quand tu liste les offres, inclue toujours le titre, l'entreprise, la localisation, l'ID de l'offre et un lien direct si possible
- Rédiger des lettres de motivation personnalisées à partir de son CV
- Optimiser son CV pour un poste précis avec des suggestions concrètes
- Préparer des entretiens avec des questions ciblées

Sois proactif : si l'utilisateur mentionne un poste, propose directement de chercher des offres.
Si il veut postuler, propose de rédiger la lettre. Réponds toujours en français."""

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=MemorySaver(),
    )
