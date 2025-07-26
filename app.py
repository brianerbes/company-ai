import os
import json
from pathlib import Path

# Define the root path of the workspace where all companies are stored.
WORKSPACE_ROOT = Path(__file__).parent / "workspace"

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
        print(f"Workspace directory not found at: {workspace_path}")
        return discovered_companies

    for company_dir in workspace_path.iterdir():
        if not company_dir.is_dir():
            continue

        manifest_path = company_dir / "manifest.json"
        if manifest_path.is_file():
            print(f"Found potential company: '{company_dir.name}'")
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                    # We can add more validation here later
                    discovered_companies.append(manifest_data)
                    print(f"  -> Successfully loaded manifest for '{manifest_data['identity']['name']}'.")
            except json.JSONDecodeError:
                print(f"  -> ERROR: Could not parse manifest.json for '{company_dir.name}'.")
            except KeyError:
                print(f"  -> ERROR: Manifest for '{company_dir.name}' is missing required keys.")
        
    return discovered_companies

def main():
    """
    Main entry point for the CompanIA application.
    """
    print("CompanIA application starting...")
    print("-" * 20)
    print("Discovering companies in workspace...")
    
    companies = discover_companies(WORKSPACE_ROOT)
    
    print("-" * 20)
    if not companies:
        print("No valid companies found. Please create a company folder with a valid manifest.json.")
    else:
        print(f"Found {len(companies)} company/companies:")
        for company_data in companies:
            print(f" - {company_data['identity']['name']}")
    print("-" * 20)


if __name__ == "__main__":
    main()