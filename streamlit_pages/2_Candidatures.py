import sys
sys.path.insert(0, 'src')
import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import datetime
from database import get_all_applications, update_application

def update_status():
    old_data = st.session_state.get('applications_before_update')
    new_data = st.session_state.get('updated_applications')
    applications_to_update = new_data[
        (new_data['A relancer'] != old_data['A relancer']) | (new_data['Statut'] != old_data['Statut'])
    ]
    for _, row in applications_to_update.iterrows():
        update_application(row['id_application'], row['A relancer'], row['Statut'])

st.title("Suivi des candidatures")

all_applications = pd.DataFrame(get_all_applications() or [])
if all_applications.empty:
    st.info("Aucune candidature enregistrée pour le moment.")
    st.stop()
all_applications['Postulé le'] = all_applications['Postulé le'].apply(lambda x: datetime.fromisoformat(x).date())
all_applications['Date de relance'] = all_applications['Date de relance'].apply(lambda x: datetime.fromisoformat(x).date())
all_applications['Lettre'] = all_applications['path'].apply(lambda x: Path(x).name.split('.')[0] if x else None)

st.session_state['applications_before_update'] = all_applications

updated_applications = st.data_editor(
    all_applications,
    column_order=('Postulé le', "Poste", "Entreprise", "Lieu", "Statut", "A relancer", "Date de relance", "Lettre", "Lien", "Source", "path", "id_application", "offer_id", "id_letter"),
    column_config={
        "Postulé le": st.column_config.DateColumn(disabled=True),
        "Poste": st.column_config.TextColumn(disabled=True),
        "Entreprise": st.column_config.TextColumn(disabled=True),
        "Lieu": st.column_config.TextColumn(disabled=True),
        "Statut": st.column_config.SelectboxColumn(
            options=[
                "En cours",
                "Relancée",
                "Refusée",
                "Entretien programmé",
            ]
        ),
        "A relancer": st.column_config.CheckboxColumn(),
        "Date de relance": st.column_config.DateColumn(disabled=True),
        "Lettre": st.column_config.TextColumn(disabled=True),
        "Lien": st.column_config.LinkColumn(disabled=True),
        "Source": None,
        "path": None,
        "id_application": None,
        "offer_id": None,
        "id_letter": None,
    },
    hide_index=True
    )

st.session_state['updated_applications'] = updated_applications

st.button("Mettre à jour le suivi des candidatures", on_click=update_status())
