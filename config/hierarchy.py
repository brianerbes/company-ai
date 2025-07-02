# config/hierarchy.py

"""
Defines the reporting structure of the entire AI organization.

Each key represents an agent's unique ID.
- 'parent': The ID of the agent's direct manager. 'None' for the top-level agents
            who report to the Owner/User.
- 'children': A list of agent IDs that are direct reports to this agent.
"""

HIERARCHY = {
    # Level 1: The Board, reporting to the Owner (user)
    'board_of_directors': {
        'parent': None, # Reports to the Owner
        'children': ['ceo']
    },
    
    # Level 2: The C-Suite, reporting to the Board
    'ceo': {
        'parent': 'board_of_directors',
        'children': ['cto', 'cfo', 'cmo', 'lead_game_designer']
    },
    'cto': {
        'parent': 'ceo',
        'children': ['lead_programmer']
    },
    'cfo': {
        'parent': 'ceo',
        'children': [] # Manages budget, doesn't have direct production reports in this model
    },
    'cmo': {
        'parent': 'ceo',
        'children': [] # Manages marketing, no direct production reports
    },

    # Level 3: Production Leads, reporting to the C-Suite
    'lead_game_designer': {
        'parent': 'ceo',
        'children': ['lead_artist', 'lead_sound_designer']
    },
    'lead_programmer': {
        'parent': 'cto',
        'children': ['character_programmer', 'gameplay_programmer', 'qa_tester']
    },
    'lead_artist': {
        'parent': 'lead_game_designer',
        'children': ['ui_ux_designer']
    },
    'lead_sound_designer': {
        'parent': 'lead_game_designer',
        'children': []
    },
    'qa_tester': {
        'parent': 'lead_programmer',
        'children': []
    },

    # Level 4: Specialists, reporting to their leads
    'character_programmer': {
        'parent': 'lead_programmer',
        'children': []
    },
    'gameplay_programmer': {
        'parent': 'lead_programmer',
        'children': []
    },
    'ui_ux_designer': {
        'parent': 'lead_artist',
        'children': []
    }
}