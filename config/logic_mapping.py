# config/logic_mapping.py

"""
Contains the decision-making rules that connect communication Intent
and context (e.g., hierarchical direction) to a specific Strategy and Expression.
This is the "grammar" of the system.
"""

LOGIC_MAPPING = {
    "description": "The grammar of the system...",
    "decision_rules": [
        # --- Core Communication Rules ---
        {
            "rule_id": "LGC-001",
            "description": "Rule for requesting information from a superior.",
            "if_conditions": {"intent_is": "REQUEST_INFORMATION", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DEFERENTIAL", "FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "QUERY"
            }
        },
        # ... (other existing core communication rules remain here) ...
        {
            "rule_id": "LGC-006",
            "description": "Rule for providing information to a peer.",
            "if_conditions": {"intent_is": "PROVIDE_INFORMATION", "direction_is": "HORIZONTAL"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "REPORT"
            }
        },

        # --- NEW: Task Management Rules ---
        {
            "rule_id": "LGC-013",
            "description": "Rule for a subordinate reporting a task status update.",
            "if_conditions": {"intent_is": "UPDATE_TASK_STATUS", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["FORMAL", "DATA_DRIVEN"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "STATUS_UPDATE"
            }
        },
        {
            "rule_id": "LGC-012", # This was an existing rule, but it fits here
            "description": "Rule for a superior giving a direct order to a subordinate.",
            "if_conditions": {"intent_is": "ASSIGN_TASK", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DIRECTIVE", "FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "ORDER"
            }
        },
        
        # --- NEW: File System & Security Rules ---
        {
            "rule_id": "LGC-014",
            "description": "Rule for requesting approval from a human for a sensitive action.",
            "if_conditions": {"intent_is": "REQUEST_APPROVAL", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DEFERENTIAL", "FORMAL"], "urgency": "HIGH", "message_structure": "CONTEXTUAL"},
                "select_expression": "REQUEST"
            }
        },
        {
            "rule_id": "LGC-015",
            "description": "Generic rule for most file system operations.",
            # This is a generic rule. We can use a list for intents.
            "if_conditions": {"intent_is": ["CREATE_FILE", "READ_FILE", "WRITE_FILE", "SET_PERMISSIONS", "EXECUTE_FILE"]},
            "then_outcome": {
                "select_strategy": {"tone": ["FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "REQUEST"
            }
        },

        # --- Fallback Rule ---
        {
            "rule_id": "LGC-DEFAULT",
            "description": "Default rule for any unhandled combination of conditions.",
            "if_conditions": {}, # Empty condition block catches all unmatched cases
            "then_outcome": {
                "select_strategy": {"tone": ["FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "QUERY"
            }
        }
    ]
}