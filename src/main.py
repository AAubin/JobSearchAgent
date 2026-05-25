import sys
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from agent import creer_agent

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

    tokens_data = response_message.usage_metadata or {}
    this_run_inputs = tokens_data.get("input_tokens", 0)
    this_run_outputs = tokens_data.get("output_tokens", 0)
    print(f"Tokens utilisés - Input: {this_run_inputs}, Output: {this_run_outputs}\n")
    
    total_inputs += this_run_inputs
    total_outputs += this_run_outputs