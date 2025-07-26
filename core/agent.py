# core/agent.py

import json
from pathlib import Path
from .vfs import FileSystemManager

class Agent:
    """
    Represents a single AI agent in the system.

    An agent's identity, role, and capabilities are defined by its
    metadata file. It operates within the company's VFS.
    """
    def __init__(self, agent_id: str, agent_meta: dict, company_fs: FileSystemManager):
        self.id = agent_id
        self.meta = agent_meta
        self.fs = company_fs
        
        self.role = self.meta.get('role', 'Generic Agent')
        self.system_prompt = self.meta.get('system_prompt', 'You are a helpful assistant.')
    
    def __repr__(self) -> str:
        return f"<Agent id='{self.id}' role='{self.role}'>"

    def print_summary(self):
        """Prints a brief summary of the agent's identity."""
        print(f"  - Agent ID: {self.id}")
        print(f"    Role: {self.role}")