# config/hierarchy.py

"""
Defines the reporting structure of the entire AI organization.

Each key represents an agent's unique ID.
- 'parent': The ID of the agent's direct manager. 'None' for the top-level agent.
- 'children': A list of agent IDs that are direct reports to this agent.
"""

HIERARCHY = {
    'ceo': {
        'parent': None,
        'children': ['lead_game_designer', 'cmo']
    },
    'cmo': {
        'parent': 'ceo',
        'children': []
    },
    'lead_game_designer': {
        'parent': 'ceo',
        'children': ['lead_programmer', 'lead_artist']
    },
    'lead_programmer': {
        'parent': 'lead_game_designer',
        'children': ['character_programmer', 'gameplay_programmer']
    },
    'lead_artist': {
        'parent': 'lead_game_designer',
        'children': []
    },
    'character_programmer': {
        'parent': 'lead_programmer',
        'children': []
    },
    'gameplay_programmer': {
        'parent': 'lead_programmer',
        'children': []
    }
}