# config/hierarchy.py

"""
Defines the reporting structure and type for every agent in the organization.

Each key is the agent's unique ID.
- 'parent': The ID of the agent's direct manager. 'None' for top-level agents.
- 'children': A list of agent IDs that are direct reports.
- 'type': Defines the agent as 'ai' or 'human'. Human agents require
          direct input from the user to act.
"""

HIERARCHY = {
    # The Owner (user) is implicitly above this entire structure.
    
    'board_of_directors': {
        'parent': None,
        'children': ['ceo'],
        'type': 'ai' 
    },
    
    # Level 2: C-Suite. The CEO is the primary human-controlled node.
    'ceo': {
        'parent': 'board_of_directors',
        'children': ['cto', 'cfo', 'cmo', 'lead_game_designer'],
        'type': 'human'
    },
    'cto': {
        'parent': 'ceo',
        'children': ['lead_programmer'],
        'type': 'ai'
    },
    'cfo': {
        'parent': 'ceo',
        'children': [],
        'type': 'ai'
    },
    'cmo': {
        'parent': 'ceo',
        'children': [],
        'type': 'ai'
    },

    # Level 3: Production Leads
    'lead_game_designer': {
        'parent': 'ceo',
        'children': ['lead_artist', 'lead_sound_designer'],
        'type': 'ai'
    },
    'lead_programmer': {
        'parent': 'cto',
        'children': ['character_programmer', 'gameplay_programmer', 'qa_tester'],
        'type': 'ai'
    },
    'lead_artist': {
        'parent': 'lead_game_designer',
        'children': ['ui_ux_designer'],
        'type': 'ai'
    },
    'lead_sound_designer': {
        'parent': 'lead_game_designer',
        'children': [],
        'type': 'ai'
    },
    'qa_tester': {
        'parent': 'lead_programmer',
        'children': [],
        'type': 'ai'
    },

    # Level 4: Specialists
    'character_programmer': {
        'parent': 'lead_programmer',
        'children': [],
        'type': 'ai'
    },
    'gameplay_programmer': {
        'parent': 'lead_programmer',
        'children': [],
        'type': 'ai'
    },
    'ui_ux_designer': {
        'parent': 'lead_artist',
        'children': [],
        'type': 'ai'
    }
}