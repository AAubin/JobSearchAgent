import sys
sys.path.insert(0, 'src')
import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_all_offers, update_offers

def apply_to_selected_offers():
    offers = st.session_state.get('updated_offers')
    if offers is None:
        return
    offers_to_apply = offers[offers['Postuler ?'] == True]
    if offers_to_apply.empty:
        st.warning("Aucune offre sélectionnée pour postuler.")
    else:
        st.session_state['offers_to_apply'] = offers_to_apply
        st.session_state['go_to_chat'] = True


st.title("Offres d'emplois précédemment sauvegardés")

all_offers = pd.DataFrame(get_all_offers())

all_offers['Postuler ?'] = [False for _ in range(len(all_offers))]
all_offers['Recherché le'] = all_offers['Recherché le'].apply(lambda x: datetime.fromisoformat(x).date())

filters_name = ['Lieu', 'Intéressé', 'Recherché le']
filters = {}
with st.container(horizontal=True):
    for c in filters_name:
        filters[c] = st.multiselect(label = c, options=all_offers[c].unique())

offers_to_display = all_offers.copy()
for c, values in filters.items():
    if values:
        offers_to_display = offers_to_display[offers_to_display[c].isin(values)]

updated_offers = st.data_editor(
    offers_to_display,
    column_order=('Postuler ?', "Intitulé", "Entreprise", "Lieu", "Intéressé", "Lien", "Recherché le", "offer_id"),
    column_config={
        "Postuler ?": st.column_config.CheckboxColumn(),
        "Intitulé": st.column_config.TextColumn(),
        "Entreprise": st.column_config.TextColumn(),
        "Lieu": st.column_config.TextColumn(),
        "Intéressé": st.column_config.CheckboxColumn(),
        "Lien": st.column_config.LinkColumn(disabled=True),
        "Recherché le": st.column_config.DateColumn(disabled=True),
        "offer_id": None,
    },
    hide_index=True
    )

st.session_state['updated_offers'] = updated_offers

offers_to_update = updated_offers[( updated_offers['Entreprise'] != offers_to_display['Entreprise'])
                                   | (updated_offers['Intitulé'] != offers_to_display['Intitulé'])
                                   | (updated_offers['Lieu'] != offers_to_display['Lieu'])
                                   | (updated_offers['Intéressé'] != offers_to_display['Intéressé'])
                                   ]
for _, row in offers_to_update.iterrows():
    update_offers(row['offer_id'], row['Entreprise'], row['Intitulé'], row['Lieu'], row['Intéressé'])

st.button("Postuler aux offres sélectionnées", on_click=apply_to_selected_offers)

if st.session_state.pop('go_to_chat', False):
    st.switch_page("streamlit_pages/1_Chat.py")