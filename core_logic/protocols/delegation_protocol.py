# core_logic/protocols/delegation_protocol.py

"""
This module contains the logic for handling downward delegation of tasks,
especially when a single task is assigned to multiple subordinates,
triggering a "group chat" or "team meeting" scenario.
"""


def handle_delegation_to_group(orchestrator, sender_id: str, recipient_ids: list, task_payload: dict):
    """
    Manages the delegation of a task from a manager to multiple subordinates.

    This function creates a temporary, shared conversation history for the
    duration of the briefing to ensure all team members are aligned.

    Args:
        orchestrator: The main orchestrator instance.
        sender_id: The ID of the manager agent delegating the task.
        recipient_ids: A list of subordinate agent IDs receiving the task.
        task_payload: The initial payload from the manager's message.

    Returns:
        A dictionary summarizing the delegation outcome.
    """
    print(f"[DelegationProtocol] Initiating group delegation from '{sender_id}' to {recipient_ids}")

    manager_agent = orchestrator.agents[sender_id]
    
    # --- This is a simplified simulation of a group chat ---
    # A full implementation would be more complex. This version captures the essence.
    
    # 1. Create a shared "meeting transcript"
    shared_history = []
    initial_task_text = f"Manager '{sender_id}' has assigned a group task: {task_payload.get('KEY_INSTRUCTION', 'No instruction provided.')}"
    shared_history.append(f"SYSTEM: {initial_task_text}")
    print(f"[DelegationProtocol] {initial_task_text}")

    # 2. Poll each subordinate for initial questions.
    questions_to_address = []
    for recipient_id in recipient_ids:
        recipient_agent = orchestrator.agents[recipient_id]
        # We give the subordinate the task directly to see if they have a question
        response = recipient_agent.execute_task(initial_task_text)
        
        if response.get("intent") == "REQUEST_INFORMATION":
            question = response.get("payload", {}).get("QUESTION", "Unspecified question.")
            questions_to_address.append({'asker': recipient_id, 'question': question})
            shared_history.append(f"QUESTION from {recipient_id}: {question}")

    # 3. The manager addresses all collected questions.
    if questions_to_address:
        print(f"[DelegationProtocol] Manager '{sender_id}' needs to address {len(questions_to_address)} questions.")
        
        q_and_a_prompt = (
            "Your team has the following clarifying questions about the task you just assigned. "
            "Please provide a single, comprehensive response that addresses all of them.\n\n"
        )
        for item in questions_to_address:
            q_and_a_prompt += f"- From {item['asker']}: {item['question']}\n"

        # The manager "thinks" about the answers
        manager_response = manager_agent.execute_task(q_and_a_prompt)
        manager_answer = manager_response.get("payload", {}).get("DETAILS", "No specific answer provided.")
        shared_history.append(f"CLARIFICATION from Manager {sender_id}: {manager_answer}")
        print(f"[DelegationProtocol] Manager provided clarification: '{manager_answer[:100]}...'")

    # 4. Finalize the delegation
    final_context = "\n".join(shared_history)
    for recipient_id in recipient_ids:
        # Add the full meeting transcript to each subordinate's permanent history
        orchestrator.add_to_history(
            recipient_id,
            'user',
            f"You participated in a group briefing. Here is the full transcript to use as context for your task:\n{final_context}"
        )
    
    print("[DelegationProtocol] Delegation complete. All subordinates have been briefed with full context.")
    return {
        "intent": "PROVIDE_INFORMATION",
        "payload": {
            "EXECUTIVE_SUMMARY": "Group delegation completed successfully.",
            "DETAILS": f"Task was assigned to {len(recipient_ids)} agents with a shared context session."
        }
    }