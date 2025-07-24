# main.py

"""
The main entry point for the Company-IA application.

This script initializes the system and runs a command-line interface (CLI)
for the user to interact with the AI and Human agents.
"""

from core_logic.orchestrator import Orchestrator

def main():
    """
    Main function to run the Company-IA command-line interface.
    """
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        print(f"\n--- FATAL ERROR DURING INITIALIZATION ---")
        print(f"Error: {e}")
        return

    print("\n--- Company-IA Command Console ---")
    print("Welcome, Owner.")
    print("Type 'help' for a list of commands.")
    print("----------------------------------\n")

    while True:
        try:
            # Check for and display pending actions for human agents
            human_tasks_pending = False
            for agent_id in orchestrator.human_agents:
                if orchestrator.agent_inboxes[agent_id]:
                    print(f"!!! PENDING ACTION for Human Agent: '{agent_id}' has tasks in their inbox. Use 'inbox {agent_id}'.")
                    human_tasks_pending = True
            
            if not human_tasks_pending:
                 orchestrator.process_agent_inboxes()

            command = input("You (Owner)> ")
            cmd_lower = command.lower()
            
            # --- NEW, MORE FLEXIBLE COMMAND PARSING LOGIC ---

            if cmd_lower in ['exit', 'quit']:
                print("Shutting down Company-IA.")
                break
            
            if cmd_lower == 'help':
                print("\n--- Available Commands ---")
                print("delegate to [agent_id]: [task] - Assign a new top-level task.")
                print("inbox [human_agent_id]           - View the task inbox for one of your human agents.")
                print("respond as [human_agent_id]: [response] - Respond to the oldest task in a human agent's inbox.")
                print("help                             - Show this help message.")
                print("exit / quit                      - Close the application.")
                print("------------------------\n")
                continue

            # Handle commands with arguments but no colon
            if cmd_lower.startswith("inbox "):
                parts = command.split(" ", 1)
                agent_id = parts[1].strip()
                if agent_id not in orchestrator.human_agents:
                    print(f"Error: '{agent_id}' is not a designated human agent.")
                    continue
                
                print(f"\n--- Inbox for {agent_id} ---")
                inbox = orchestrator.agent_inboxes[agent_id]
                if not inbox:
                    print("Inbox is empty.")
                else:
                    for i, msg in enumerate(inbox):
                        print(f"{i+1}. TaskID: {msg.get('task_id')} - {msg.get('payload', {}).get('description', 'N/A')}")
                print("--------------------------\n")

            # Handle commands that require a colon
            elif ":" in command:
                parts = command.split(":", 1)
                command_verb = parts[0].strip()
                command_args = parts[1].strip()

                if command_verb.lower().startswith("delegate to"):
                    agent_id = command_verb.replace("delegate to", "").strip()
                    result = orchestrator.start_task(agent_id, command_args)
                    print(f"[System] {result}")

                elif command_verb.lower().startswith("respond as"):
                    agent_id = command_verb.replace("respond as", "").strip()
                    if agent_id not in orchestrator.human_agents:
                        print(f"Error: '{agent_id}' is not a designated human agent.")
                        continue
                    if not orchestrator.agent_inboxes[agent_id]:
                        print(f"Inbox for '{agent_id}' is empty.")
                        continue
                    
                    message_to_respond = orchestrator.agent_inboxes[agent_id].pop(0)
                    orchestrator.task_manager.update_task_status(message_to_respond['task_id'], 'COMPLETED', agent_id)
                    orchestrator.audit_log.log_action(agent_id, 'TASK_RESPONSE', f"Human provided response: {command_args}")
                    print(f"Response from '{agent_id}' to task {message_to_respond['task_id']} logged and task marked as COMPLETED.")

                else:
                    print("Unknown command format. Type 'help' for assistance.")
            
            else:
                 print("Invalid command format. Type 'help' for assistance.")

        except KeyboardInterrupt:
            print("\nShutting down Company-IA.")
            break
        except Exception as e:
            print(f"\n--- An unexpected error occurred ---")
            print(f"Error: {e}")
            print("------------------------------------\n")

if __name__ == "__main__":
    main()