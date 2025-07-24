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

    # --- Print Welcome Message ---
    print("\n--- Company-IA Command Console ---")
    print("Welcome, Owner.")
    print("Type 'help' for a list of commands.")
    print("----------------------------------\n")

    # --- Main Interaction Loop ---
    while True:
        try:
            # Check for and display pending actions for human agents
            human_tasks_pending = False
            for agent_id in orchestrator.human_agents:
                if orchestrator.agent_inboxes[agent_id]:
                    print(f"!!! PENDING ACTION for Human Agent: '{agent_id}' has tasks in their inbox. Use 'inbox {agent_id}'.")
                    human_tasks_pending = True
            
            if not human_tasks_pending:
                 # Process one turn of the AI agent inboxes if no humans are blocked
                 orchestrator.process_agent_inboxes()


            command = input("You (Owner)> ")

            if command.lower() in ['exit', 'quit']:
                print("Shutting down Company-IA.")
                break
            
            if command.lower() == 'help':
                print("\n--- Available Commands ---")
                print("delegate to [agent_id]: [task] - Assign a new top-level task.")
                print("inbox [human_agent_id]           - View the task inbox for one of your human agents.")
                print("respond as [human_agent_id]: [response] - Respond to the oldest task in a human agent's inbox.")
                print("help                             - Show this help message.")
                print("exit / quit                      - Close the application.")
                print("------------------------\n")
                continue

            parts = command.split(":", 1)
            if len(parts) < 2:
                print("Invalid command format. Type 'help' for assistance.")
                continue

            command_verb = parts[0].strip()
            command_args = parts[1].strip()

            if command_verb.startswith("delegate to"):
                agent_id = command_verb.replace("delegate to", "").strip()
                result = orchestrator.start_task(agent_id, command_args)
                print(f"[System] {result}")

            elif command_verb.startswith("respond as"):
                agent_id = command_verb.replace("respond as", "").strip()
                if agent_id not in orchestrator.human_agents:
                    print(f"Error: '{agent_id}' is not a designated human agent.")
                    continue
                # This is a simplified response mechanism
                # In a real system, you'd specify which task_id you're responding to.
                if not orchestrator.agent_inboxes[agent_id]:
                    print(f"Inbox for '{agent_id}' is empty.")
                    continue

                # Respond to the oldest message in the inbox
                message_to_respond = orchestrator.agent_inboxes[agent_id].pop(0)
                print(f"Responding to task: {message_to_respond}")
                # This logic would be expanded to allow the human to formulate a full structured message
                # For now, we'll just complete the task.
                orchestrator.task_manager.update_task_status(message_to_respond['task_id'], 'COMPLETED', agent_id)
                orchestrator.audit_log.log_action(agent_id, 'TASK_RESPONSE', f"Human provided response: {command_args}")
                print(f"Response from '{agent_id}' logged.")
            
            elif command_verb.startswith("inbox"):
                agent_id = command_verb.replace("inbox", "").strip()
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

            else:
                print("Unknown command. Type 'help' for a list of commands.")


        except KeyboardInterrupt:
            print("\nShutting down Company-IA.")
            break
        except Exception as e:
            print(f"\n--- An unexpected error occurred ---")
            print(f"Error: {e}")
            print("------------------------------------\n")


if __name__ == "__main__":
    main()