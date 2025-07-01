# core_logic/protocols/communication_protocol.py

"""
This module contains the logic for constructing and interpreting the formal
communication messages used by agents. It acts as the "etiquette engine"
of the system.
"""

from config.logic_mapping import LOGIC_MAPPING
from config.communication_definitions import COMMUNICATION_DEFINITIONS


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
    print(f"Building message from '{sender_id}' to '{recipient_id}' with intent '{intent}'.")
    
    # --- FUTURE LOGIC WILL GO HERE ---
    # 1. Determine communication direction (UPWARD, DOWNWARD, HORIZONTAL) by
    #    comparing sender and recipient in orchestrator.hierarchy.
    #
    # 2. Search through LOGIC_MAPPING['decision_rules'] to find the rule that
    #    matches the intent and direction.
    #
    # 3. Use the found rule to get the correct strategy (tone, urgency) and
    #    expression format (e.g., 'QUERY', 'ORDER').
    #
    # 4. Assemble the final message object using the determined components
    #    and the provided payload.
    #
    # Example placeholder return:
    return {
        "sender": sender_id,
        "recipient": recipient_id,
        "intent": intent,
        "strategy": {
            "tone": ["DIRECTIVE"],
            "urgency": "MEDIUM"
        },
        "expression_mode": "ORDER",
        "payload": payload
    }


def parse_message_for_llm(structured_message: dict) -> str:
    """
    Converts a structured message object into a plain string prompt
    that can be understood by the LLM.

    Args:
        structured_message: The message object to convert.

    Returns:
        A plain string representation of the message for the LLM.
    """
    # --- FUTURE LOGIC WILL GO HERE ---
    # This function will format the message nicely. For example:
    # "You have received an ORDER with MEDIUM urgency. The instruction is: ..."
    
    payload_str = ", ".join(f"{k}: '{v}'" for k, v in structured_message.get("payload", {}).items())
    return f"Received a message. Intent: {structured_message.get('intent')}. Payload: {payload_str}"