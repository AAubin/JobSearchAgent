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
    st.Page("streamlit_pages/2_Candidatures.py", title="Suivi des candidatures", icon="📋"),
    st.Page("streamlit_pages/3_Offres.py", title="Offres sauvegardées", icon="🔍"),
    st.Page("streamlit_pages/4_Profil.py", title="Profil de recherches", icon="⚙️"),
    st.Page("streamlit_pages/5_Sessions.py", title="Résumé des sessions", icon="📊"),
]
pg = st.navigation(pages)
pg.run()
