# core_logic/protocols/escalation_protocol.py

"""
This module contains the logic for the question escalation protocol, which
is triggered when an agent determines it lacks the information to proceed.
"""


def handle_question_escalation(orchestrator, start_agent_id: str, question_payload: dict) -> dict:
    """
    Manages the escalation of a question up the chain of command.

    The process continues until an agent in the hierarchy can provide an
    answer or until it reaches the top-level agent (who then escalates to
    the user).

    Args:
        orchestrator: The main orchestrator instance.
        start_agent_id: The ID of the agent who originally asked the question.
        question_payload: The payload from the agent's message, e.g., {'QUESTION': '...'}.

    Returns:
        A dictionary containing the final answer or a notification that the
        question was escalated to the user.
    """
    question_text = question_payload.get("QUESTION", "An unspecified question.")
    print(f"[EscalationProtocol] Initiating for '{start_agent_id}': '{question_text}'")

    current_agent_id = start_agent_id
    
    # Start a loop that travels up the hierarchy
    while (parent_id := orchestrator.get_parent(current_agent_id)):
        # --- Safety Check: Circuit Breaker ---
        orchestrator.turn_counter += 1
        print(f"[EscalationProtocol] Turn {orchestrator.turn_counter}/{orchestrator.MAX_INTERNAL_TURNS}")
        if orchestrator.turn_counter >= orchestrator.MAX_INTERNAL_TURNS:
            print("[EscalationProtocol] HALTED: Maximum internal turns reached.")
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {
                    "EXECUTIVE_SUMMARY": "Process Halted",
                    "DETAILS": f"Process stopped after {orchestrator.turn_counter} internal turns to prevent a potential loop."
                }
            }

        # Get the parent agent instance
        parent_agent = orchestrator.agents[parent_id]
        print(f"[EscalationProtocol] Escalating to parent: [{parent_agent.agent_id}]")

        # Format the question as a new task for the parent
        task_for_parent = (
            f"My subordinate ({current_agent_id}) requires clarification. "
            f"Please address the following question: {question_text}"
        )
        
        # The parent agent executes the task (the question)
        response_message = parent_agent.execute_task(task_for_parent)
        
        # If the parent provides a definitive answer, the escalation is successful
        if response_message.get("intent") != "REQUEST_INFORMATION":
            final_answer = response_message.get("payload", {}).get("DETAILS", "No details provided.")
            print(f"[EscalationProtocol] [{parent_agent.agent_id}] resolved the question.")

            # Add the definitive answer to the knowledge base for future reference
            fact_to_add = f"Regarding the question '{question_text}', the decision is: {final_answer}"
            orchestrator.knowledge_base.add_fact(fact_to_add)

            # Return the successful resolution
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {
                    "EXECUTIVE_SUMMARY": f"Question resolved by {parent_agent.agent_id}.",
                    "DETAILS": final_answer
                }
            }

        # If the parent also has a question, update the question and continue the loop
        question_text = response_message.get("payload", {}).get("QUESTION", "An unspecified follow-up question.")
        current_agent_id = parent_id
        print(f"[EscalationProtocol] [{parent_agent.agent_id}] also has a question. Continuing escalation.")

    # If the loop completes, it means the CEO was reached and still couldn't answer.
    # The final escalation point is the human user.
    return {
        "intent": "PROVIDE_INFORMATION",
        "payload": {
            "EXECUTIVE_SUMMARY": "Escalated to Human User",
            "DETAILS": (
                "The question has been escalated through the entire hierarchy and requires your input. "
                f"The final question is: {question_text}"
            )
        }
    }