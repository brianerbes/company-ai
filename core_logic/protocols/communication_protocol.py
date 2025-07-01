# core_logic/protocols/communication_protocol.py

"""
This module contains the logic for constructing and interpreting the formal
communication messages used by agents. It acts as the "etiquette engine"
of the system.
"""

from config.logic_mapping import LOGIC_MAPPING


def _get_direction(orchestrator, sender_id: str, recipient_id: str) -> str:
    """
    Determines the hierarchical direction of communication.

    Args:
        orchestrator: The main orchestrator instance.
        sender_id: The ID of the agent sending the message.
        recipient_id: The ID of the agent receiving the message.

    Returns:
        A string: "UPWARD", "DOWNWARD", "HORIZONTAL", or "SELF".
    """
    if sender_id == recipient_id:
        return "SELF"

    sender_parent = orchestrator.get_parent(sender_id)
    recipient_parent = orchestrator.get_parent(recipient_id)

    if sender_parent == recipient_id:
        return "UPWARD"
    if recipient_parent == sender_id:
        return "DOWNWARD"
    if sender_parent == recipient_parent:
        return "HORIZONTAL"

    # Default case for more complex relationships (e.g., uncle/nephew),
    # which we can treat as horizontal for now.
    return "HORIZONTAL"


def build_structured_message(orchestrator, sender_id: str, recipient_id: str, intent: str, payload: dict) -> dict:
    """
    Builds a structured message object based on the sender's intent and the
    hierarchical relationship between the sender and recipient.

    Args:
        orchestrator: The main orchestrator instance, needed to determine hierarchy.
        sender_id: The ID of the agent sending the message.
        recipient_id: The ID of the agent receiving the message.
        intent: The core intent of the message (e.g., 'REQUEST_INFORMATION').
        payload: The actual content of the message.

    Returns:
        A dictionary representing the fully structured message.
    """
    print(f"[Protocol] Building message from '{sender_id}' to '{recipient_id}' with intent '{intent}'.")

    direction = _get_direction(orchestrator, sender_id, recipient_id)
    print(f"[Protocol] Determined communication direction: {direction}")

    # Find the matching rule in our logic mapping
    found_rule = None
    for rule in LOGIC_MAPPING['decision_rules']:
        conditions = rule['if_conditions']
        if (conditions.get('intent_is') == intent and
                conditions.get('direction_is') == direction):
            found_rule = rule
            break

    # If no specific rule is found, use the default fallback rule
    if not found_rule:
        found_rule = next(
            rule for rule in LOGIC_MAPPING['decision_rules'] if rule['rule_id'] == 'LGC-DEFAULT'
        )
        print(f"[Protocol] No specific rule found. Using default.")

    print(f"[Protocol] Applying rule: {found_rule['rule_id']} - {found_rule['description']}")
    
    outcome = found_rule['then_outcome']
    strategy = outcome['select_strategy']
    expression_mode = outcome['select_expression']

    # Assemble the final message object
    final_message = {
        "sender": sender_id,
        "recipient": recipient_id,
        "intent": intent,
        "strategy": {
            "tone": strategy['tone'],
            "urgency": strategy['urgency'],
            "message_structure": strategy['message_structure']
        },
        "expression_mode": expression_mode,
        "payload": payload
    }

    return final_message


def parse_message_for_llm(structured_message: dict) -> str:
    """
    Converts a structured message object into a plain string prompt
    that can be understood by the LLM.

    Args:
        structured_message: The message object to convert.

    Returns:
        A plain string representation of the message for the LLM.
    """
    mode = structured_message.get("expression_mode", "UNKNOWN")
    payload = structured_message.get("payload", {})
    
    # This formatting can be made much more sophisticated, but this provides a clean, readable output.
    prompt_lines = [
        f"You have received a new task formatted as a '{mode}'.",
        "--- Task Details ---"
    ]
    for key, value in payload.items():
        # Format the key nicely (e.g., 'KEY_INSTRUCTION' -> 'Key Instruction')
        formatted_key = key.replace('_', ' ').title()
        prompt_lines.append(f"- {formatted_key}: {value}")
    prompt_lines.append("--------------------")
    prompt_lines.append("Determine your next action based on this information and your role.")

    return "\n".join(prompt_lines)