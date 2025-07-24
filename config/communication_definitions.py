# config/communication_definitions.py

"""
Defines the formal vocabulary for all inter-agent communication.
This structure breaks down communication into three domains:
1.  INTENT_DOMAIN: The "why" or fundamental purpose of the message.
2.  STRATEGY_DOMAIN: The "how" the message is styled (tone, urgency).
3.  EXPRESSION_DOMAIN: The final message format or template.
"""

COMMUNICATION_DEFINITIONS = {
    "INTENT_DOMAIN": {
        "description": "Defines the fundamental purpose that drives an act of communication.",
        "primary_intents": [
            # --- Core Communication Intents ---
            {
                "ID": "INT-001",
                "name": "REQUEST_INFORMATION",
                "description": "The need to obtain data from another node to resolve an ambiguity.",
            },
            {
                "ID": "INT-002",
                "name": "PROVIDE_INFORMATION",
                "description": "The need to deliver data, status, or a final answer.",
            },
            {
                "ID": "INT-003",
                "name": "GENERATE_NEW_IDEAS",
                "description": "The need to explore a problem or concept openly; brainstorming.",
            },

            # --- Task Management Intents ---
            {
                "ID": "INT-004",
                "name": "ASSIGN_TASK",
                "description": "The need to delegate a specific unit of work to a subordinate node.",
            },
            {
                "ID": "INT-005",
                "name": "UPDATE_TASK_STATUS",
                "description": "The need to report a change in a task's status (e.g., COMPLETED).",
            },

            # --- File System Intents ---
            {
                "ID": "INT-006",
                "name": "CREATE_FILE",
                "description": "The need to create a new file in the virtual file system.",
            },
            {
                "ID": "INT-007",
                "name": "READ_FILE",
                "description": "The need to read the contents of a file in the virtual file system.",
            },
            {
                "ID": "INT-008",
                "name": "WRITE_FILE",
                "description": "The need to write or append content to a file in the virtual file system.",
            },
            {
                "ID": "INT-009",
                "name": "SET_PERMISSIONS",
                "description": "The need to change the read/write/execute permissions of a file for another agent.",
            },

            # --- Advanced / Security Intents ---
            {
                "ID": "INT-010",
                "name": "REQUEST_APPROVAL",
                "description": "The need to ask a human agent for explicit approval to perform a sensitive action, like executing code.",
            },
            {
                "ID": "INT-011",
                "name": "EXECUTE_FILE",
                "description": "The need to run an executable file (e.g., a python script) in the secure sandbox.",
            },
        ]
    },
    "STRATEGY_DOMAIN": {
        "description": "Defines 'how' an intent is packaged for delivery by selecting a set of tactical components.",
        "strategy_components": {
            "tone": {
                "description": "The relational style of the message, adapted to the recipient and intent.",
                "options": [
                    "FORMAL", "DIRECTIVE", "COLLABORATIVE", "DEFERENTIAL", "DATA_DRIVEN", "URGENT"
                ]
            },
            "urgency": {
                "description": "The priority level and expected response time for the communication.",
                "options": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            },
            "message_structure": {
                "description": "How the information within the message is organized.",
                "options": ["DIRECT", "CONTEXTUAL"]
            }
        }
    },
    # Note: The EXPRESSION_DOMAIN can be simplified for now, as the payload will be more dynamic.
    # We can rely on the INTENT to guide the agent on what fields to include in the payload.
    "EXPRESSION_DOMAIN": {
        "description": "Defines final, concrete message formats. This is a template library.",
        "communication_modes": [
            {"ID": "EXP-001", "name": "QUERY"},
            {"ID": "EXP-002", "name": "REPORT"},
            {"ID": "EXP-003", "name": "ORDER"},
            {"ID": "EXP-004", "name": "REQUEST"},
            {"ID": "EXP-005", "name": "STATUS_UPDATE"},
        ]
    }
}