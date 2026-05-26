import sys
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from database import init_db, save_session, get_last_letter_id, rate_letter
init_db()

from agent import creer_agent


def calculate_session_cost(inputs_tokens, output_tokens):
    cost_input_tokens_by_million = 3.0 #USD
    cost_output_tokens_by_million = 15.0 #USD
    return (inputs_tokens * cost_input_tokens_by_million + output_tokens * cost_output_tokens_by_million) / 1000000

def prompt_for_rating():
    while True:
        try:
            rating = int(input("Veuillez évaluer la lettre de motivation générée (1-5) : "))
            if rating == 0:
                print("Lettre non évaluée par l'utilisateur.")
                return None
            if 1 <= rating <= 5:
                return rating
            else:
                print("Veuillez entrer un nombre entre 1 et 5.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre entre 1 et 5.")

def automatic_action_after_tools(response):
    # Si une lettre de motivation a été générée, demander une évaluation à l'utilisateur
    letter_was_generated  = any([m.type == "tool" and m.name == "rediger_lettre_motivation" for m in response])
    if letter_was_generated:
        rating = prompt_for_rating()
        if rating is not None:
            last_letter_id = get_last_letter_id()
            if last_letter_id is not None:
                rate_letter(last_letter_id, rating)
                print(f"Merci pour votre évaluation de {rating}/5 !")
            else:
                print("Aucune lettre trouvée pour enregistrer l'évaluation.")
        else:
            print("Aucune évaluation enregistrée.")

agent = creer_agent()
ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
run_name = f"run_{ts}"
SESSION = "session_1"

print("Agent de recherche d'emploi prêt. Tape 'exit' pour quitter.\n")

total_inputs = 0
total_outputs = 0

while True:
    user_input = input("Vous : ").strip()
    if user_input.lower() == "exit":
        print(f"Total tokens utilisés - Input: {total_inputs}, Output: {total_outputs}")
        cost_session = calculate_session_cost(total_inputs, total_outputs)
        print(f"Coût estimé de la session : ${cost_session:.4f}")
        save_session(total_inputs, total_outputs, cost_session)  # Coût à calculer si nécessaire
        break
    if not user_input:
        continue
    
    config = {"configurable": {"thread_id": SESSION},
              "run_name": run_name}
    
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config
    )
    response_message = response["messages"][-1]
    print(f"\nAgent : {response_message.content}\n")

    automatic_action_after_tools(response["messages"])

    tokens_data = response_message.usage_metadata or {}
    this_run_inputs = tokens_data.get("input_tokens", 0)
    this_run_outputs = tokens_data.get("output_tokens", 0)

    total_inputs += this_run_inputs
    total_outputs += this_run_outputs
    

