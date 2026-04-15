from agent import creer_agent

agent = creer_agent()
SESSION = "session_1"

print("Agent de recherche d'emploi prêt. Tape 'exit' pour quitter.\n")

while True:
    user_input = input("Vous : ").strip()
    if user_input.lower() == "exit":
        break
    if not user_input:
        continue

    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": SESSION}}
    )
    print(f"\nAgent : {response['messages'][-1].content}\n")