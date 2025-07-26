from pathlib import Path
from core.company import Company, discover_companies

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

def main():
    """
    Main entry point for the CompanIA application.
    """
    print("CompanIA application starting...")
    print("-" * 20)
    
    # 1. Load the company and agents
    # ... (this part is unchanged)
    company_manifests = discover_companies(WORKSPACE_ROOT)
    if not company_manifests:
        print("No valid companies found. Exiting.")
        return
    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path')
    active_company = Company(selected_manifest, company_path)
    active_company.load_agents()
    print("-" * 20)

    # 2. Create, assign, and process a task
    cto_id = "agent_id_cto_001"
    if cto_id in active_company.agents:
        task_description = "Draft the technical specification for the new 'Dynamic Task Graph' feature. The document should be created at 'docs/tech_spec_task_graph.md'."
        task = active_company.create_task(description=task_description, assignee_id=cto_id)
        
        cto_agent = active_company.agents[cto_id]
        cto_agent.process_task(task)
        
        # **NEW STEP: Verify the work was done**
        print("\n--- Verifying agent's work ---")
        file_path = "docs/tech_spec_task_graph.md"
        content = active_company.fs.read_file(file_path)
        if content:
            print(f"Successfully read file at '{file_path}'.")
            print(f"Content length: {len(content)} characters.")
        else:
            print(f"Verification FAILED: Could not read file at '{file_path}'.")

    else:
        print(f"Could not create task: Agent '{cto_id}' not found.")
    
    print("-" * 20)
    print("Application cycle complete.")


if __name__ == "__main__":
    main()