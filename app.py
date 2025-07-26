from pathlib import Path
from core.company import Company, discover_companies

# Define the root path of the workspace where all companies are stored.
WORKSPACE_ROOT = Path(__file__).parent / "workspace"

def main():
    """
    Main entry point for the CompanIA application.
    """
    print("CompanIA application starting...")
    print("-" * 20)
    
    # 1. Discover available companies
    print("Discovering companies in workspace...")
    company_manifests = discover_companies(WORKSPACE_ROOT)
    
    if not company_manifests:
        print("No valid companies found. Please create a company folder with a valid manifest.json.")
        return

    print(f"Found {len(company_manifests)} company/companies:")
    for i, manifest in enumerate(company_manifests):
        print(f"  [{i+1}] {manifest['identity']['name']}")
    print("-" * 20)

    # 2. Select a company (for now, we'll auto-select the first one)
    # In the future, this will be a user input prompt.
    selected_manifest = company_manifests[0]
    print(f"Loading selected company: '{selected_manifest['identity']['name']}'...")
    
    # 3. Load the company into a dedicated object
    active_company = Company(selected_manifest)
    
    print("Company loaded successfully.")
    print("-" * 20)
    active_company.print_summary()
    print("-" * 20)
    
    # The main application loop will start here in the future...

if __name__ == "__main__":
    main()