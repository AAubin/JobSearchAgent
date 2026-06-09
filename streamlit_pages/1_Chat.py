import sys
sys.path.insert(0, 'src')
import streamlit as st
from datetime import datetime
from langchain_core.messages import AIMessageChunk
from agent import creer_agent
from utils import rate_letter, application, to_markdown, TokenCounterCallback
from database import save_session, update_session


def session_state_init():
    if "agent" not in st.session_state:
        st.session_state.agent = creer_agent()
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = [{
            "role": "assistant",
            "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider aujourd'hui ?"
        }]
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("session_%Y%m%d")
    if "pending_rating" not in st.session_state:
        st.session_state.pending_rating = False
    if "db_session_id" not in st.session_state:
        st.session_state.db_session_id = None
    if "token_callback" not in st.session_state:
        st.session_state.token_callback = TokenCounterCallback()


def on_click_rating(rating):
    rate_letter(rating)
    last_message = st.session_state.display_messages.pop()
    last_message["done"] = True
    st.session_state.display_messages.append(last_message)
    st.session_state.pending_rating = False

def session_token_management(db_session_id):
    token_count = st.session_state.token_callback.to_dict()
    cost = st.session_state.token_callback.cost
    if db_session_id is None:
        return save_session(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, token_count, cost)
    else:
        update_session(db_session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), token_count, cost)
        return db_session_id

def call_agent(prompt):
    #Config Langgraph
    agent = st.session_state.agent
    config = {
        "configurable": {"thread_id": st.session_state.session_id},
        "run_name": st.session_state.session_id,
        "callbacks": [st.session_state.token_callback]
    }
    user_message = {"role": "user", "content": prompt.strip()}
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        current_msg_id = None
        for msg, metadata in agent.stream({"messages": [user_message]}, config=config, stream_mode="messages"):
            if msg.content and isinstance(msg, AIMessageChunk) and metadata.get("langgraph_node") == 'model':
                if msg.id != current_msg_id:
                    if current_msg_id is not None:
                        full_text += "\n\n"
                    current_msg_id = msg.id
                if isinstance(msg.content, str):
                    text = msg.content
                else:
                    text = "".join(c.get("text", "") for c in msg.content if isinstance(c, dict))
                if text:
                    full_text += text
                    placeholder.markdown(to_markdown(full_text) + "▌")  
        placeholder.markdown(to_markdown(full_text)) 

    st.session_state.display_messages.append({"role": "assistant", "content": full_text})
    st.session_state.db_session_id = session_token_management(st.session_state.db_session_id)

    final_state = agent.get_state(config)
    all_messages = final_state.values["messages"]
    last_user_idx = max(
        (i for i, m in enumerate(all_messages) if m.type == "human"),
        default=-1
    )
    recent_messages = all_messages[last_user_idx + 1:]

    letter_interaction = any(m.type == "tool" and m.name == "write_cover_letter" for m in recent_messages)
    if letter_interaction:
        st.session_state.display_messages.append({"role": "system", "type": 'rating_widget', "done": False})
        st.session_state.pending_rating = True
        st.rerun()


session_state_init()

for message in st.session_state.display_messages:
    match message['role']:
        case "user":
            st.chat_message("user").markdown(message["content"])
        case "assistant":
            st.chat_message("assistant").markdown(message["content"])
        case "system":
            if message.get("type") == "rating_widget" and not message.get("done") and st.session_state.pending_rating:
                rating = st.slider("Veuillez évaluer la lettre de motivation générée (1-5) :", min_value=1, max_value=5, value=3, key=f"rating_{id(message)}")
                st.button("Ok", key=f"button_{id(message)}", on_click=lambda: on_click_rating(rating))

user_prompt = st.chat_input("Tapez votre message ici...", disabled=st.session_state.pending_rating)

if "offers_to_apply" in st.session_state and not st.session_state.pending_rating:
    offers_to_apply = st.session_state.offers_to_apply
    row = offers_to_apply.iloc[0]
    remaining = offers_to_apply.iloc[1:].reset_index(drop=True)
    
    if remaining.empty:
        del st.session_state.offers_to_apply
    else:
        st.session_state.offers_to_apply = remaining
    
    content = f"Candidature à l'offre {row['Intitulé']} chez {row['Entreprise']}..."
    st.session_state.display_messages.append({"role": "user", "content": content})
    st.chat_message("user").markdown(content)
    auto_prompt = application(row['offer_id'])
    call_agent(auto_prompt)
    
    st.rerun()

if user_prompt:
    user_message = {"role": "user", "content": user_prompt.strip()}
    st.session_state.display_messages.append(user_message)
    st.chat_message("user").markdown(user_prompt)
    call_agent(user_prompt)

with st.sidebar:
    st.header("Session en cours :")
    cb = st.session_state.token_callback
    st.metric("Tokens utilisés", cb.input_tokens + cb.output_tokens)
    st.metric("Coût estimé de la session", f"${cb.cost:.5f}")
