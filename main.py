# main.py

"""
The main entry point for the Company-IA application.

This script initializes the system and runs a command-line interface (CLI)
for the user to interact with the AI agents.
"""

from core_logic.orchestrator import Orchestrator

def main():
    """
    Main function to run the Company-IA command-line interface.
    """
    try:
        # This one object initializes the entire system.
        orchestrator = Orchestrator()
    except Exception as e:
        print(f"\n--- FATAL ERROR DURING INITIALIZATION ---")
        print(f"Error: {e}")
        print("Please ensure your .env file is set up correctly with a valid GEMINI_API_KEY.")
        print("-----------------------------------------\n")
        return

    # --- Print Welcome Message and Instructions ---
    print("\n--- Company-IA Command Line Interface ---")
    print("Welcome! You are the board of directors.")
    print("Assign tasks using the format: delegate to [agent_id]: [your task]")
    print("Example: delegate to ceo: Summarize our current project strategy.")
    print("Type 'exit' or 'quit' to close.")
    print("-------------------------------------------\n")

    # --- Main Interaction Loop ---
    while True:
        try:
            command = input("You> ")

            if command.lower() in ['exit', 'quit']:
                print("Shutting down Company-IA.")
                break

            if not command.lower().startswith("delegate to"):
                print("Invalid command format. Use 'delegate to [agent_id]: [task]'")
                continue
            
            # Parse the command to get the target agent and the task
            parts = command.split(":", 1)
            if len(parts) < 2:
                print("Invalid command format. Make sure to include a ':' after the agent_id.")
                continue

            agent_id = parts[0].replace("delegate to", "").strip()
            task = parts[1].strip()

            # Delegate the task via the orchestrator. This is where all the magic happens.
            result = orchestrator.delegate_task(agent_id, task)
            
            # Print the final result from the system.
            print(f"\nSystem Response:\n---\n{result}\n---")

        except KeyboardInterrupt:
            # Allow user to exit with Ctrl+C
            print("\nShutting down Company-IA.")
            break
        except Exception as e:
            # Catch any other unexpected errors during the loop
            print(f"\n--- An unexpected error occurred ---")
            print(f"Error: {e}")
            print("------------------------------------\n")


if __name__ == "__main__":
    main()