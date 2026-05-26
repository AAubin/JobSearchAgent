from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from tools.cv_optimizer import optimiser_cv
from tools.veille import rechercher_offres
from tools.motivation import rediger_lettre_motivation
from tools.entretien import preparer_entretien

from prompt_loader import load_prompt

def creer_agent() -> CompiledStateGraph:
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    tools = [rechercher_offres, optimiser_cv, rediger_lettre_motivation, preparer_entretien]

    system_prompt_data = load_prompt("system_prompt")
    system_prompt = system_prompt_data["template"].strip()
    
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=MemorySaver(),
    )
