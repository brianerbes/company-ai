from __future__ import annotations

from pathlib import Path
from uuid import UUID

from engine.company import Company
from engine.task import InteractionType, Task


def main():
    """
    Main entry point for the application.
    This function serves as a test harness for our first vertical slice.
    """
    print("--- CompanIA Engine: Simple Chat Test ---")

    # 1. Load the company from the workspace directory.
    try:
        company_path = Path(__file__).parent / "workspace" / "alpha_corp"
        company = Company(path=company_path)
        print(f"Successfully loaded company: {company.name}")
    except ValueError as e:
        print(f"Error loading company: {e}")
        return

    # 2. Get the root agent specified in the manifest.
    root_agent_id_str = company.manifest.get("hierarchy", {}).get("root_agent_id")
    if not root_agent_id_str:
        print("Error: root_agent_id not found in manifest.")
        return

    root_agent = company.get_agent(UUID(root_agent_id_str))
    if not root_agent:
        print(f"Error: Could not load root agent with ID: {root_agent_id_str}")
        return

    print(f"Loaded Root Agent: {root_agent.role} (ID: {root_agent.id})")

    # 3. Create a new task for the agent to process.
    #    This simulates the user giving a command.
    user_command = "Hello, this is my first command."
    task = Task(
        type=InteractionType.TASK_DELEGATION,
        source_agent_id=root_agent.id,  # In a real scenario, this could be a UI ID.
        target_agent_id=root_agent.id,
        payload={"description": user_command},
    )

    print(f"\nCreated new task: {task.description} (Status: {task.status.value})")

    # 4. Ask the agent to process the task.
    root_agent.process_task(task)

    # 5. Check the final status of the task.
    print(f"\nFinal task status: {task.status.value}")
    print("--- Test Complete ---")


if __name__ == "__main__":
    main()
