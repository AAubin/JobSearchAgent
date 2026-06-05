import streamlit as st
from src.database import init_db

init_db()

st.set_page_config(
    page_title="Agent pour la recherche d'emploi",
    page_icon="🤖",
    layout="wide"
)

pages = [
    st.Page("streamlit_pages/1_Chat.py", title="Chat", icon="💬"),
    st.Page("streamlit_pages/2_Offres.py", title="Offres", icon="🔍"),
    st.Page("streamlit_pages/3_Suivi_candidatures.py", title="Candidatures", icon="📋"),
    st.Page("streamlit_pages/4_Sessions.py", title="Sessions", icon="📊"),
]
pg = st.navigation(pages)
pg.run()
