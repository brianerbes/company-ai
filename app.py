# app.py

from pathlib import Path
from core.company import Company, discover_companies

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

def main():
    """
    Main entry point for the CompanIA application.
    """
    print("CompanIA application starting...")
    print("-" * 20)
    
    # 1. Discover available companies
    company_manifests = discover_companies(WORKSPACE_ROOT)
    if not company_manifests:
        print("No valid companies found. Exiting.")
        return
    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path')
    
    # 2. Load the company
    print(f"Loading company: '{selected_manifest['identity']['name']}'...")
    active_company = Company(selected_manifest, company_path)
    active_company.print_summary()
    print("-" * 20)
    
    # 3. Load the company's agents
    active_company.load_agents()
    print("-" * 20)

    # 4. Print a summary of the loaded team
    print("Active team roster:")
    if not active_company.agents:
        print("  No agents found.")
    else:
        for agent in active_company.agents.values():
            agent.print_summary()
    print("-" * 20)
    
if __name__ == "__main__":
    main()