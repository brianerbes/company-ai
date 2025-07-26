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
    print("Discovering companies in workspace...")
    company_manifests = discover_companies(WORKSPACE_ROOT)
    
    if not company_manifests:
        print("No valid companies found. Exiting.")
        return

    print(f"Found {len(company_manifests)} company/companies:")
    for i, manifest in enumerate(company_manifests):
        print(f"  [{i+1}] {manifest['identity']['name']}")
    print("-" * 20)

    # 2. Select a company (auto-selecting the first one)
    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path') # Get and remove path from dict
    print(f"Loading selected company: '{selected_manifest['identity']['name']}'...")
    
    # 3. Load the company into an object, now providing its path
    active_company = Company(selected_manifest, company_path)
    
    print("Company loaded successfully.")
    print("-" * 20)
    active_company.print_summary()
    print("-" * 20)
    
    # 4. Test the Virtual File System
    print("Testing VFS by listing files at company root ('/'):")
    root_files = active_company.fs.list_files('/')
    print(f"  -> Found files: {root_files}")
    print("-" * 20)
    
if __name__ == "__main__":
    main()