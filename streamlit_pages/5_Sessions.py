import sys
sys.path.insert(0, 'src')
import streamlit as st
import pandas as pd
from database import get_all_sessions
from config.llm_base_models import AGENT_MODEL, LETTER_MODEL, AGENT_MODEL_COST, LETTER_MODEL_COST

st.title("Suivi des tokens consommés et des coûts associés")

sessions = get_all_sessions()
if not sessions:
    st.info("Aucune session enregistrée pour le moment.")
    st.stop()

nb_sessions = len(sessions)
tokens = sum(s["input_tokens"] + s["output_tokens"] for s in sessions)
cost = sum(s["cost_usd"] for s in sessions)

with st.container(horizontal=True):
    st.metric("Nombre total de sessions", nb_sessions)
    st.metric("Nombre total de tokens consommés", tokens)
    st.metric("Coût total estimé (USD)", f"${cost:.5f}")

st.dataframe(
    pd.DataFrame(sessions),
    column_config={
        "id_session": None,
        "date_start": st.column_config.DatetimeColumn(),
        "date_end": st.column_config.DatetimeColumn(),
        "input_tokens": st.column_config.NumberColumn(),
        "output_tokens": st.column_config.NumberColumn(),
        "cost_usd": st.column_config.NumberColumn(format="$%.5f")
    },
    hide_index=True
)

st.sidebar.info(
    "**Tarifs et modèles utilisés :**  \n"
    f"- Modèle agent :  \n"
    f"  `{AGENT_MODEL}`  \n"
    f"  - Input : ${AGENT_MODEL_COST[0]} / 1M tokens  \n"
    f"  - Output : ${AGENT_MODEL_COST[1]} / 1M tokens  \n"
    f"- Modèle lettres :  \n"
    f"  `{LETTER_MODEL}`  \n"
    f"  - Input : ${LETTER_MODEL_COST[0]} / 1M tokens  \n"
    f"  - Output : ${LETTER_MODEL_COST[1]} / 1M tokens"
)