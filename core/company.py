# core/company.py

import json
from pathlib import Path
from .vfs import FileSystemManager

class Company:
    """
    Represents a single, loaded company instance.
    """
    def __init__(self, manifest_data: dict, company_path: Path):
        self.manifest = manifest_data
        self.path = company_path
        self.name = manifest_data.get('identity', {}).get('name', 'Unnamed Company')
        
        # Each company gets its own sandboxed file system manager.
        self.fs = FileSystemManager(company_root=self.path)

    def __repr__(self) -> str:
        return f"<Company name='{self.name}'>"

    def print_summary(self):
        """Prints a brief summary of the company's identity."""
        print(f"Company Name: {self.name}")
        print(f"Vision: {self.manifest.get('identity', {}).get('vision', 'N/A')}")
        print(f"Path: {self.path}")

# --- discover_companies function remains the same ---

def discover_companies(workspace_path: Path) -> list[dict]:
    """
    Scans the workspace directory for valid company folders.

    A company is considered valid if it's a directory containing a 'manifest.json' file.

    Args:
        workspace_path: The path to the workspace directory.

    Returns:
        A list of dictionaries, where each dictionary is a parsed manifest.json,
        including its root path for later use.
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
                    # Add the company's path to the data we return
                    manifest_data['_company_path'] = company_dir
                    discovered_companies.append(manifest_data)
            except (json.JSONDecodeError, KeyError):
                pass
        
    return discovered_companies