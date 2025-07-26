import json
from pathlib import Path

class Company:
    """
    Represents a single, loaded company instance.

    This class holds the state and configuration of a company, loaded from its
    manifest. It will be the central point for managing agents, tasks, and
    resources for that company instance.
    """
    def __init__(self, manifest_data: dict):
        self.manifest = manifest_data
        self.name = manifest_data.get('identity', {}).get('name', 'Unnamed Company')

    def __repr__(self) -> str:
        return f"<Company name='{self.name}'>"

    def print_summary(self):
        """Prints a brief summary of the company's identity."""
        print(f"Company Name: {self.name}")
        print(f"Vision: {self.manifest.get('identity', {}).get('vision', 'N/A')}")


def discover_companies(workspace_path: Path) -> list[dict]:
    """
    Scans the workspace directory for valid company folders.

    A company is considered valid if it's a directory containing a 'manifest.json' file.

    Args:
        workspace_path: The path to the workspace directory.

    Returns:
        A list of dictionaries, where each dictionary is a parsed manifest.json.
        Returns an empty list if the workspace doesn't exist or contains no companies.
    """
    discovered_companies = []
    if not workspace_path.is_dir():
        # This case is handled in the main app, but good practice to keep it.
        return discovered_companies

    for company_dir in workspace_path.iterdir():
        if not company_dir.is_dir():
            continue

        manifest_path = company_dir / "manifest.json"
        if manifest_path.is_file():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                    discovered_companies.append(manifest_data)
            except (json.JSONDecodeError, KeyError):
                # Silently ignore invalid manifests during discovery for now.
                # The main app can log these errors if needed.
                pass
        
    return discovered_companies