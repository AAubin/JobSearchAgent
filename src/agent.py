from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from tools.resume_optimizer import resume_optimizer
from tools.search_offers import search_offer
from tools.cover_letter import write_cover_letter
from tools.interview import interview_advice
from tools.add_manual_offer import add_manual_offer

from utils import load_prompt, load_profile
import yaml

def creer_agent() -> CompiledStateGraph:
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    tools = [search_offer, resume_optimizer, write_cover_letter, interview_advice, add_manual_offer]

    user_profile = load_profile()
    profile_clean = {k: v for k, v in user_profile.items() if v is not None}
    profile_str = yaml.dump(profile_clean, allow_unicode=True, default_flow_style=False)
    system_prompt_data = load_prompt("system_prompt")
    system_prompt = system_prompt_data["template"].format(user_profile=profile_str)
    
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=MemorySaver(),
    )
