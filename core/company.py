# core/company.py

import json
from pathlib import Path
from .vfs import FileSystemManager
from .agent import Agent  # Import the new Agent class

class Company:
    """
    Represents a single, loaded company instance.
    """
    def __init__(self, manifest_data: dict, company_path: Path):
        self.manifest = manifest_data
        self.path = company_path
        self.name = manifest_data.get('identity', {}).get('name', 'Unnamed Company')
        self.fs = FileSystemManager(company_root=self.path)
        self.agents = {} # A dictionary to hold loaded agent objects

    def __repr__(self) -> str:
        return f"<Company name='{self.name}'>"

    def print_summary(self):
        """Prints a brief summary of the company's identity."""
        print(f"Company Name: {self.name}")
        print(f"Vision: {self.manifest.get('identity', {}).get('vision', 'N/A')}")
        print(f"Path: {self.path}")

    def load_agents(self):
        """
        Scans the company's VFS for agent directories and loads them.
        An agent directory is identified by the presence of a '.agent_meta.json' file.
        """
        print("Loading agents...")
        agent_dirs = self.fs.list_files('/')
        for dir_name in agent_dirs:
            # In a real VFS, we'd check if it's a directory.
            # For now, we'll just check for the meta file's path.
            meta_path = Path(dir_name) / '.agent_meta.json'
            meta_content_str = self.fs.read_file(str(meta_path))

            if meta_content_str:
                try:
                    agent_meta = json.loads(meta_content_str)
                    agent_id = agent_meta.get('agent_id')
                    if agent_id:
                        agent = Agent(agent_id, agent_meta, self.fs)
                        self.agents[agent_id] = agent
                        print(f"  -> Successfully loaded agent: {agent.role}")
                except json.JSONDecodeError:
                    print(f"  -> WARNING: Could not parse .agent_meta.json in '{dir_name}'")
        print(f"Total agents loaded: {len(self.agents)}")

# --- discover_companies function remains the same ---
# (The rest of the file is unchanged)

def discover_companies(workspace_path: Path) -> list[dict]:
    """
    Scans the workspace directory for valid company folders.
    ...
    """
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