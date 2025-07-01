# config/logic_mapping.py

"""
Contains the decision-making rules that connect communication Intent
and context (e.g., hierarchical direction) to a specific Strategy and Expression.
This is the "grammar" of the system. The Orchestrator uses these rules to
determine how a message should be formatted.
"""

LOGIC_MAPPING = {
    "description": "The grammar of the system. This contains the rules that connect Intent and Strategy to a final Expression, based on context like hierarchical direction.",
    "decision_rules": [
        # Rules for Intent: REQUEST_INFORMATION
        {
            "rule_id": "LGC-001",
            "description": "Rule for requesting information from a superior.",
            "if_conditions": {"intent_is": "REQUEST_INFORMATION", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DEFERENTIAL", "FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "QUERY"
            }
        },
        {
            "rule_id": "LGC-002",
            "description": "Rule for requesting information from a subordinate.",
            "if_conditions": {"intent_is": "REQUEST_INFORMATION", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DIRECTIVE"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "QUERY"
            }
        },
        {
            "rule_id": "LGC-003",
            "description": "Rule for requesting information from a peer.",
            "if_conditions": {"intent_is": "REQUEST_INFORMATION", "direction_is": "HORIZONTAL"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "QUERY"
            }
        },

        # Rules for Intent: PROVIDE_INFORMATION
        {
            "rule_id": "LGC-004",
            "description": "Rule for providing information to a superior.",
            "if_conditions": {"intent_is": "PROVIDE_INFORMATION", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["FORMAL", "DATA_DRIVEN"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "REPORT"
            }
        },
        {
            "rule_id": "LGC-005",
            "description": "Rule for providing information to a subordinate.",
            "if_conditions": {"intent_is": "PROVIDE_INFORMATION", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DIRECTIVE"], "urgency": "MEDIUM", "message_structure": "CONTEXTUAL"},
                "select_expression": "REPORT"
            }
        },
        {
            "rule_id": "LGC-006",
            "description": "Rule for providing information to a peer.",
            "if_conditions": {"intent_is": "PROVIDE_INFORMATION", "direction_is": "HORIZONTAL"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "REPORT"
            }
        },

        # Rules for Intent: PERSUADE_TOWARDS_DECISION
        {
            "rule_id": "LGC-007",
            "description": "Rule for persuading a superior, requiring a formal debate.",
            "if_conditions": {"intent_is": "PERSUADE_TOWARDS_DECISION", "direction_is": "UPWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DEFERENTIAL", "DATA_DRIVEN", "FORMAL"], "urgency": "HIGH", "message_structure": "CONTEXTUAL"},
                "select_expression": "DIALECTIC"
            }
        },
        {
            "rule_id": "LGC-008",
            "description": "Rule for persuading a subordinate by providing context and reasoning.",
            "if_conditions": {"intent_is": "PERSUADE_TOWARDS_DECISION", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DIRECTIVE", "DATA_DRIVEN"], "urgency": "MEDIUM", "message_structure": "CONTEXTUAL"},
                "select_expression": "REPORT"
            }
        },
        {
            "rule_id": "LGC-009",
            "description": "Rule for persuading a peer, initiating a formal debate.",
            "if_conditions": {"intent_is": "PERSUADE_TOWARDS_DECISION", "direction_is": "HORIZONTAL"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE", "DATA_DRIVEN"], "urgency": "HIGH", "message_structure": "CONTEXTUAL"},
                "select_expression": "DIALECTIC"
            }
        },

        # Rules for Intent: GENERATE_NEW_IDEAS
        {
            "rule_id": "LGC-010",
            "description": "Rule for a leader initiating a brainstorming workshop with their team.",
            "if_conditions": {"intent_is": "GENERATE_NEW_IDEAS", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE"], "urgency": "MEDIUM", "message_structure": "CONTEXTUAL"},
                "select_expression": "WORKSHOP"
            }
        },
        {
            "rule_id": "LGC-011",
            "description": "Rule for initiating a creative workshop with a peer.",
            "if_conditions": {"intent_is": "GENERATE_NEW_IDEAS", "direction_is": "HORIZONTAL"},
            "then_outcome": {
                "select_strategy": {"tone": ["COLLABORATIVE"], "urgency": "MEDIUM", "message_structure": "CONTEXTUAL"},
                "select_expression": "WORKSHOP"
            }
        },

        # Rule for Intent: ASSIGN_TASK
        {
            "rule_id": "LGC-012",
            "description": "Rule for a superior giving a direct order to a subordinate.",
            "if_conditions": {"intent_is": "ASSIGN_TASK", "direction_is": "DOWNWARD"},
            "then_outcome": {
                "select_strategy": {"tone": ["DIRECTIVE", "FORMAL"], "urgency": "MEDIUM", "message_structure": "DIRECT"},
                "select_expression": "ORDER"
            }
        },
        
        # Default Fallback Rule
        {
            "rule_id": "LGC-DEFAULT",
            "description": "Default rule for any unhandled combination of conditions.",
            "if_conditions": {}, # Empty condition block catches all unmatched cases
            "then_outcome": {
                "select_strategy": {"tone": ["URGENT", "FORMAL"], "urgency": "HIGH", "message_structure": "DIRECT"},
                "select_expression": "QUERY" # The query would ask for clarification on how to proceed.
            }
        }
    ]
}