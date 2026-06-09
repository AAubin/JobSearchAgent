import streamlit as st
from src.database import init_db, get_applications_to_follow
from datetime import datetime, timedelta, date

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

applications_to_follow = get_applications_to_follow()
if applications_to_follow:
    with st.sidebar:
        content = "**Candidatures à relancer cette semaine :**\n\n"
        for application in applications_to_follow:
            content += f"- **{application[1]}** :\n\n {application[0]}\n"
        st.warning(content)
        st.divider()

pg.run()
