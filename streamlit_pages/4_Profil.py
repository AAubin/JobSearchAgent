import sys
sys.path.insert(0, 'src')
import streamlit as st
import yaml
from utils import load_profile, save_profile

def render_field(key, config, value):
    value_str = None
    if config['type'] == 'text':
        return st.text_input(label=config['label'], value=value)
    if config['type'] == 'tags':
        if value is not None:
            value_str = ', '.join(value)
        return st.text_input(label=config['label'], value=value_str)
    if config['type'] == 'textarea':
        if value is not None:
            value_str = '\n'.join(value)
        return st.text_area(label=config['label'], value=value_str)
    if config['type'] == 'multiselect':
        return st.multiselect(label=config['label'], options=config['options'], default=value)

def parse_field(config, value):
    if not value:
        return None
    if config['type'] == 'text':
        return value
    if config['type'] == 'tags':
        return [v.strip() for v in value.split(",") if v.strip()]
    if config['type'] == 'textarea':
        return [v.strip() for v in value.split('\n') if v.strip()]
    if config['type'] == 'multiselect':
        return value

st.title("Profil de recherche")

FIELDS = load_profile("user_profile_fields.yaml")
user_profile = load_profile()

values = {}
with st.form("preferences"):
    for key, config in FIELDS.items():
        if key not in ['version', 'description']:
            values[key] = render_field(key, config, user_profile.get(key))
    submitted = st.form_submit_button("Enregistrer les préférences")
    if submitted:
        new_profile = {
            key: parse_field(config, values[key]) for key, config in FIELDS.items() if key not in ['version', 'description']
        }
        save_profile(new_profile)
        st.toast("Profil enregistré !", icon="✅")
