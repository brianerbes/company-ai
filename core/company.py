# core/company.py

import json
from pathlib import Path
from .vfs import FileSystemManager
from .agent import Agent
from .task import Task
from .memory import MemoryManager

class Company:
    def __init__(self, manifest_data: dict, company_path: Path, pubsub_handle=None):
        self.manifest = manifest_data
        self.path = company_path
        self.pubsub = pubsub_handle
        self.name = manifest_data.get('identity', {}).get('name', 'Unnamed Company')
        self.fs = FileSystemManager(company_root=self.path)
        self.memory = MemoryManager(company_root=self.path) # <-- ADD THIS LINE
        self.agents = {}
        self.tasks = {} # A dictionary to hold active tasks

    def __repr__(self) -> str:
        return f"<Company name='{self.name}'>"

    def print_summary(self):
        """Prints a brief summary of the company's identity."""
        print(f"Company Name: {self.name}")
        print(f"Vision: {self.manifest.get('identity', {}).get('vision', 'N/A')}")
        print(f"Path: {self.path}")

    def create_task(self, description: str, assignee_id: str, ui_channel: str = None) -> Task:
        """Creates a new task and adds it to the company's task registry."""
        if assignee_id not in self.agents:
            raise ValueError(f"Cannot assign task: Agent ID '{assignee_id}' not found.")
        
        new_task = Task(description=description, assignee_id=assignee_id)
        new_task.ui_channel = ui_channel
        self.tasks[new_task.task_id] = new_task
        print(f"New task created and assigned to {assignee_id}: {new_task.task_id}")
        return new_task

    def load_agents(self):
        """
        Scans the company's VFS for agent directories and loads them.
        """
        print("Loading agents...")
        agent_dirs = self.fs.list_files('/')
        for dir_name in agent_dirs:
            meta_path = Path(dir_name) / '.agent_meta.json'
            meta_content_str = self.fs.read_file(str(meta_path))

            if meta_content_str:
                try:
                    agent_meta = json.loads(meta_content_str)
                    agent_id = agent_meta.get('agent_id')
                    if agent_id:
                        agent = Agent(agent_id, agent_meta, self) 
                        self.agents[agent_id] = agent
                        print(f"  -> Successfully loaded agent: {agent.role}")
                except json.JSONDecodeError:
                    print(f"  -> WARNING: Could not parse .agent_meta.json in '{dir_name}'")
        print(f"Total agents loaded: {len(self.agents)}")

# --- La función discover_companies permanece igual ---
def discover_companies(workspace_path: Path) -> list[dict]:
    # ... (código sin cambios)
    discovered_companies = []
    if not workspace_path.is_dir():
        return discovered_companies

    for company_dir in workspace_path.iterdir():
        if not company_dir.is_dir():
            continue

        manifest_path = company_dir / "manifest.json"
        if manifest_path.is_file():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                    manifest_data['_company_path'] = company_dir
                    discovered_companies.append(manifest_data)
            except (json.JSONDecodeError, KeyError):
                pass
        
    return discovered_companies