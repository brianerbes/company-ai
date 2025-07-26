from pathlib import Path
from core.company import Company, discover_companies
from core.task import TaskStatus

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

def main():
    print("CompanIA application starting...")
    print("-" * 20)
    
    # 1. Load the company and agents
    company_manifests = discover_companies(WORKSPACE_ROOT)
    if not company_manifests: return
    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path')
    active_company = Company(selected_manifest, company_path)
    active_company.load_agents()
    
    print("\nTeam Roster:")
    for agent in active_company.agents.values():
        agent.print_summary()
    print("-" * 20)

    # 2. Create the initial, high-level task for the CTO
    cto_id = "agent_id_cto_001"
    if cto_id in active_company.agents:
        task_description = "Oversee the creation of the technical specification for the new 'Dynamic Task Graph' feature. You must delegate the detailed work to your team, such as the API design to the Lead Programmer and the database schema to the Database Architect. You will then assemble their work into the final document."
        active_company.create_task(description=task_description, assignee_id=cto_id)
    
    # 3. Main Scheduler Loop
    print("\n--- Starting Main Scheduler Loop ---")
    MAX_SCHEDULER_CYCLES = 5 # Prevent infinite loops
    cycles = 0
    while cycles < MAX_SCHEDULER_CYCLES:
        runnable_tasks = [t for t in active_company.tasks.values() if t.status == TaskStatus.PENDING]
        
        if not runnable_tasks:
            print("No runnable tasks found. Shutting down scheduler.")
            break
            
        print(f"\n[Scheduler Cycle {cycles+1}] Found {len(runnable_tasks)} runnable task(s).")
        
        # Process tasks one by one
        for task in runnable_tasks:
            agent = active_company.agents.get(task.assignee_id)
            if agent:
                agent.process_task(task)
            else:
                task.set_status(TaskStatus.FAILED, f"Assignee '{task.assignee_id}' not found.")
        
        cycles += 1

    print("\n--- Scheduler Finished ---")
    print("Final Task Statuses:")
    for task in active_company.tasks.values():
        print(f"  - Task {task.task_id[:8]}: {task.status.value}")

if __name__ == "__main__":
    main()