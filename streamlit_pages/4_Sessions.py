import sys
sys.path.insert(0, 'src')
import streamlit as st
import pandas as pd
from database import get_all_sessions


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
    "**Tarifs Claude Sonnet utilisés**  \n"
    "- Input : $3.00 / 1M tokens  \n"
    "- Output : $15.00 / 1M tokens"
)