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
            {
                "ID": "INT-001",
                "name": "REQUEST_INFORMATION",
                "description": "The need to obtain a specific, concrete piece of data from another node.",
                "requires_direct_response": True,
                "objective": "To close a personal knowledge gap."
            },
            {
                "ID": "INT-002",
                "name": "PROVIDE_INFORMATION",
                "description": "The need to deliver data or status proactively or as a response.",
                "requires_direct_response": False,
                "objective": "To close a knowledge gap in another node."
            },
            {
                "ID": "INT-003",
                "name": "PERSUADE_TOWARDS_DECISION",
                "description": "The need to convince another node (usually a superior) to take a specific course of action.",
                "requires_argumentative_thesis": True,
                "requires_evidence": True,
                "objective": "To influence the project's strategy or execution."
            },
            {
                "ID": "INT-004",
                "name": "GENERATE_NEW_IDEAS",
                "description": "The need to explore a problem or concept openly, without a predefined solution.",
                "is_collaborative_process": True,
                "objective": "To expand the space of possible solutions."
            },
            {
                "ID": "INT-005",
                "name": "ASSIGN_TASK",
                "description": "The need to delegate a specific unit of work to a subordinate node.",
                "requires_hierarchical_authority": True,
                "objective": "To distribute the workload and execute the plan."
            }
        ]
    },
    "STRATEGY_DOMAIN": {
        "description": "Defines 'how' an intent is packaged for delivery by selecting a set of tactical components.",
        "strategy_components": {
            "tone": {
                "description": "The relational style of the message, adapted to the recipient and intent.",
                "options": [
                    "FORMAL",           # For official communications, documentation.
                    "DIRECTIVE",        # For downward communication (orders, instructions).
                    "COLLABORATIVE",    # For horizontal communication with peers (workshops).
                    "DEFERENTIAL",      # For upward communication, showing respect for hierarchy.
                    "DATA_DRIVEN",      # For arguments, emphasizing evidence and logic over opinion.
                    "URGENT"            # For alerts and critical issues.
                ]
            },
            "urgency": {
                "description": "The priority level and expected response time for the communication.",
                "options": [
                    "LOW",              # Can be addressed when time permits.
                    "MEDIUM",           # Standard priority, should be addressed in the current work cycle.
                    "HIGH",             # Requires prompt attention, may block other tasks.
                    "CRITICAL"          # System-level alert, requires immediate attention, bypassing standard queues.
                ]
            },
            "message_structure": {
                "description": "How the information within the message is organized.",
                "options": [
                    "DIRECT",           # Bottom Line Up Front (BLUFF). Conclusion first, then supporting data.
                    "CONTEXTUAL"        # Background and context first, leading up to the main point.
                ]
            }
        }
    },
    "EXPRESSION_DOMAIN": {
        "description": "Defines the final, concrete message formats that materialize an intent and strategy. This is the system's template library.",
        "communication_modes": [
            {
                "ID": "EXP-001",
                "name": "QUERY",
                "description": "A two-part interaction for requesting and receiving a specific piece of data.",
                "key_fields": ["QUESTION", "RESPONSE"]
            },
            {
                "ID": "EXP-002",
                "name": "REPORT",
                "description": "A one-way broadcast of information, such as a status update or an alert.",
                "key_fields": ["EXECUTIVE_SUMMARY", "DETAILS", "POTENTIAL_IMPACT"]
            },
            {
                "ID": "EXP-003",
                "name": "ORDER",
                "description": "A top-down, formal instruction for a subordinate to execute a task.",
                "key_fields": ["KEY_INSTRUCTION", "FINAL_OBJECTIVE", "ESTIMATED_TIMELINE", "LINKED_DOCUMENTS"]
            },
            {
                "ID": "EXP-004",
                "name": "WORKSHOP",
                "description": "A collaborative session for multi-party brainstorming and creative exploration.",
                "key_fields": ["TOPIC", "SESSION_OBJECTIVE", "PARTICIPANTS", "SESSION_STATUS", "SYNTHESIZED_RESULTS"]
            },
            {
                "ID": "EXP-005",
                "name": "DIALECTIC",
                "description": "A structured, three-step debate for resolving a high-stakes decision.",
                "key_fields": ["DIALECTICAL_ROLE", "ARGUMENT_BLOCK", "EVIDENCE_LINK"]
            }
        ]
    }
}