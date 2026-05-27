import sys
from datetime import datetime
from agent import creer_agent
from interactions import update_token_count, calculate_session_cost, post_letter_interaction, post_search_interaction, application

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from database import init_db, save_session
init_db()

def main():
    agent = creer_agent()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_name = f"run_{ts}"
    SESSION = datetime.now().strftime("session_%Y%m%d")

    print("Agent de recherche d'emploi prêt. Tape 'exit' pour quitter.\n")

    token_count = {"input_tokens": 0, "output_tokens": 0}

    while True:
        user_input = input("Vous : ").strip()
        if user_input.lower() == "exit":
            print(f"Total tokens utilisés - Input: {token_count['input_tokens']}, Output: {token_count['output_tokens']}")
            cost_session = calculate_session_cost(token_count)
            print(f"Coût estimé de la session : ${cost_session:.4f}")
            end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_session(ts, end, token_count, cost_session)
            break
        if not user_input:
            continue
        
        config = {"configurable": {"thread_id": SESSION},
                "run_name": run_name}
        
        old_state = agent.get_state(config)
        old_count = len(old_state.values.get("messages", [])) if old_state.values else 0

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )
        response_message = response["messages"][-1]
        print(f"\nAgent : {response_message.content}\n")

        current_messages = response["messages"][old_count:]

        offer_to_candidate = post_search_interaction(current_messages)
        if offer_to_candidate:
            token_count = application(agent, config, token_count, offer_to_candidate['id'], offer_to_candidate)
        else:
            post_letter_interaction(current_messages)
        tokens_data = response_message.usage_metadata or {}
        token_count = update_token_count(token_count, tokens_data)

    
if __name__ == "__main__":
    main()
