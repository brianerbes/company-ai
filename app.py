import time
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
    if cto_id in active_company.agents and not active_company.tasks:
        task_description = "Oversee the creation of the technical specification for the new 'Dynamic Task Graph' feature. You must delegate the detailed work to your team and block your own task until they are complete. You will then assemble their work into the final document."
        active_company.create_task(description=task_description, assignee_id=cto_id)
    
    # 3. Main Scheduler Loop
    print("\n--- Starting Main Scheduler Loop ---")
    MAX_SCHEDULER_CYCLES = 10 
    cycles = 0
    while cycles < MAX_SCHEDULER_CYCLES:
        cycles += 1
        print(f"\n{'='*15} Scheduler Cycle {cycles} {'='*15}")
        
        # 1. Un-block tasks whose dependencies are complete
        print("Checking for completed dependencies...")
        for task in active_company.tasks.values():
            if task.status == TaskStatus.BLOCKED:
                deps_ids = task.dependencies
                # Check if all dependencies are complete
                if all(active_company.tasks.get(dep_id).status == TaskStatus.COMPLETED for dep_id in deps_ids):
                    task.set_status(TaskStatus.PENDING, f"All dependencies ({len(deps_ids)}) are complete.")

        # 2. Find and execute runnable tasks
        runnable_tasks = [t for t in active_company.tasks.values() if t.status == TaskStatus.PENDING]
        
        if not runnable_tasks:
            print("No runnable tasks found in this cycle.")
            if all(t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for t in active_company.tasks.values()):
                print("All tasks are completed or failed. Shutting down scheduler.")
                break
            # Add a small delay if there's nothing to do, to prevent busy-waiting
            time.sleep(2)
            continue

        print(f"Found {len(runnable_tasks)} runnable task(s).")
        for task in runnable_tasks:
            agent = active_company.agents.get(task.assignee_id)
            if agent:
                agent.process_task(task)
                # Add a delay *between* each agent's turn to space out API calls
                print(f"--- Short delay after {agent.role}'s turn ---")
                time.sleep(2) 
            else:
                task.set_status(TaskStatus.FAILED, f"Assignee '{task.assignee_id}' not found.")
    print("Final Task Statuses:")
    for task in active_company.tasks.values():
        print(f"  - Task {task.task_id[:8]}: {task.status.value}")

if __name__ == "__main__":
    main()