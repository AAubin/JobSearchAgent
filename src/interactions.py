import re
from tools.search_offers import get_offer_details
from prompt_loader import load_prompt
from database import update_offer_interest, get_offer_by_id, get_offer_interest, get_last_letter_id, rate_letter

def calculate_session_cost(token_count):
    inputs_tokens = token_count["input_tokens"]
    output_tokens = token_count["output_tokens"]
    cost_input_tokens_by_million = 3.0 #USD
    cost_output_tokens_by_million = 15.0 #USD
    return (inputs_tokens * cost_input_tokens_by_million + output_tokens * cost_output_tokens_by_million) / 1000000

def update_token_count(token_count, tokens_data):
        if tokens_data:
            token_count["input_tokens"] += tokens_data.get("input_tokens", 0)
            token_count["output_tokens"] += tokens_data.get("output_tokens", 0)
        return token_count

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

def post_letter_interaction(messages):
    # Si une lettre de motivation a été générée, demander une évaluation à l'utilisateur
    letter_was_generated  = any([m.type == "tool" and m.name == "write_cover_letter" for m in messages])
    if not letter_was_generated:
        return
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

def post_search_interaction(reponse):
    search_offers_used = any([m.type == "tool" and m.name == "search_offer" for m in reponse])
    if not search_offers_used:
        return
    tool_msg = [m for m in reponse if getattr(m, "type", "") == "tool" and getattr(m, "name", "") == "search_offer"]
    if not tool_msg:
        return
    combined_content = "\n".join(m.content for m in tool_msg)
    id_liste_offres = re.findall(r"\| ID:([A-Z0-9]+) \|", combined_content)
    if not id_liste_offres:
        return
    for offre_id in id_liste_offres:
        existing_interest = get_offer_interest(offre_id)
        if existing_interest == 1:
            print(f'Offre {offre_id} : Vous avez déjà indiqué que cette offre vous intéressait.')
            continue
        elif existing_interest == 0:
            print(f'Offre {offre_id} : Vous avez déjà indiqué que cette offre ne vous intéressait pas.')
            continue
        choix = input(f'Offre {offre_id} : Cette offre vous intéresse-t-elle ? (o/n/Enter pour ignorer)   ')
        if choix == "o" or choix == "n":
            interest_map = {"o": 1, "n": 0}
            update_offer_interest(offre_id, interest_map.get(choix))
    application_choice = input("Souhaitez-vous postuler à l'une de ces offres ? Entrez l'ID de l'offre ou non) : ").strip()
    if application_choice.lower() == "non" or application_choice == "":
        return
    if application_choice not in id_liste_offres:
        print("ID d'offre invalide. Aucune candidature enregistrée.")
        return
    return get_offer_details(application_choice)

def application(agent, config, token_data, offer_id, details=None):
    if details is None:
        offer = get_offer_by_id(offer_id)
        if offer and offer.get("source") == "france_travail":
            details = get_offer_details(offer_id)
        else:
            details = offer
    entreprise_raw = details.get("entreprise", "")
    entreprise = entreprise_raw.get("nom", "N/A") if isinstance(entreprise_raw, dict) else (entreprise_raw or "Entreprise N/A")
    position = details.get("intitule") or details.get("position", "Poste N/A")
    description = details.get("description", "")
    prompt_data = load_prompt("application")
    prompt = prompt_data["template"].format(
        entreprise=entreprise,
        poste=position,
        description=description,
        offer_id=offer_id
    )
    agent_response = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, config=config)
    response_message = agent_response["messages"][-1]
    print(f"\nAgent : {response_message.content}\n")
    post_letter_interaction(agent_response["messages"])
    return update_token_count(token_data, response_message.usage_metadata or {})
