import flet as ft
from pathlib import Path
import time
import threading
import json
from core.company import Company, discover_companies
from core.task import TaskStatus

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

# --- SCHEDULER CLASS ---
class Scheduler:
    def __init__(self, company: Company):
        self.company = company
        self.is_running = False

    def run(self):
        self.is_running = True
        print("--- Starting Main Scheduler Loop ---")
        
        MAX_SCHEDULER_CYCLES = 10
        cycles = 0
        while cycles < MAX_SCHEDULER_CYCLES and self.is_running:
            cycles += 1
            print(f"\n{'='*15} Scheduler Cycle {cycles} {'='*15}")

            # 1. Un-block tasks
            print("Checking for completed dependencies...")
            for task in self.company.tasks.values():
                if task.status == TaskStatus.BLOCKED:
                    if all(self.company.tasks.get(dep_id).status == TaskStatus.COMPLETED for dep_id in task.dependencies):
                        task.set_status(TaskStatus.PENDING, f"All dependencies complete.")

            # 2. Find and execute runnable tasks
            runnable_tasks = [t for t in self.company.tasks.values() if t.status == TaskStatus.PENDING]
            
            if not runnable_tasks:
                print("No runnable tasks found in this cycle.")
                if all(t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for t in self.company.tasks.values()):
                    print("All tasks are completed or failed. Shutting down scheduler.")
                    self.is_running = False
                    if self.company.pubsub:
                        self.company.pubsub.send_all({"text": "All tasks complete. Scheduler finished.", "type": "system"})
                    break
                time.sleep(1)
                continue

            print(f"Found {len(runnable_tasks)} runnable task(s).")
            for task in runnable_tasks:
                if not self.is_running: break
                agent = self.company.agents.get(task.assignee_id)
                if agent:
                    agent.process_task(task)
                    print(f"--- Short delay after {agent.role}'s turn ---")
                    time.sleep(1) 
                else:
                    task.set_status(TaskStatus.FAILED, f"Assignee '{task.assignee_id}' not found.")
        
        print("\n--- Scheduler Finished ---")
        self.is_running = False

# --- MAIN FLET APP ---
def main(page: ft.Page):
    page.title = "CompanIA"
    page.window_width = 1200
    page.window_height = 800

    # --- Data Loading ---
    company_manifests = discover_companies(WORKSPACE_ROOT)
    if not company_manifests: 
        page.add(ft.Text("FATAL: No valid companies found in workspace."))
        return
        
    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path')
    active_company = Company(selected_manifest, company_path, pubsub_handle=page.pubsub)
    active_company.load_agents()

    # --- App State ---
    selected_agent = None
    scheduler_thread = None

    # --- UI Controls ---
    chat_view = ft.ListView(expand=True, spacing=10, padding=20)
    message_input = ft.TextField(hint_text="Type a message...", expand=True)

    def on_message(msg):
        """PubSub handler to display messages from the backend."""
        msg_channel = msg.get("channel")
        if msg_channel and selected_agent and msg_channel != selected_agent.id:
            return

        mtype = msg.get("type", "info")
        text = msg.get("text", "")
        agent_role = msg.get("agent", "System")
        
        # Determine the visual style of the message
        is_user_facing = mtype == "user_facing"
        is_system = mtype == "system"
        is_user = mtype == "user"

        # Save all message types to history
        if selected_agent:
            selected_agent.chat_history.append({"speaker": agent_role, "text": text, "type": mtype})
        
        # Only show user-facing and system messages in the chat view
        if is_user_facing or is_system:
            chat_view.controls.append(
                ft.Text(f"{agent_role}: {text}", size=14, italic=is_system, color="white50" if is_system else "white")
            )
            page.update()

    page.pubsub.subscribe(on_message)

    def send_message(e):
        nonlocal selected_agent, scheduler_thread
        user_message = message_input.value
        if not user_message or not selected_agent:
            return

        # Save the user's message to the history
        selected_agent.chat_history.append({"speaker": "You", "text": user_message, "type": "user"})

        chat_view.controls.append(ft.Text(f"You: {user_message}", size=14, weight=ft.FontWeight.BOLD))
        message_input.value = ""
        
        active_company.create_task(description=user_message, assignee_id=selected_agent.id, ui_channel=selected_agent.id)
        
        if scheduler_thread is None or not scheduler_thread.is_alive():
            scheduler = Scheduler(company=active_company)
            scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
            scheduler_thread.start()
        
        chat_view.scroll_to(offset=-1, duration=100)
        page.update()

    send_button = ft.IconButton(icon="send_rounded", on_click=send_message)

    def select_agent(e):
        nonlocal selected_agent
        selected_agent = e.control.data
        chat_view.controls.clear()
        
        chat_view.controls.append(ft.Text(f"Conversation with {selected_agent.role}", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER))
        chat_view.controls.append(ft.Divider())

        for message in selected_agent.chat_history:
            speaker = message.get("speaker")
            text = message.get("text")
            mtype = message.get("type")

            if speaker == "You":
                chat_view.controls.append(ft.Text(f"You: {text}", size=14, weight=ft.FontWeight.BOLD))
            else:
                color = "white50" if mtype == "info" else "white"
                chat_view.controls.append(ft.Text(f"{speaker}: {text}", size=14, italic=(mtype == "info"), color=color))
        
        def scroll_async():
            """Gives the UI a moment to render before scrolling."""
            time.sleep(0.05) # A tiny delay
            chat_view.scroll_to(offset=-1)
            page.update()

        # Update the page to draw the history, then run the scroll as a separate background task
        page.update()
        page.run_thread(scroll_async)

    # --- Build the UI Layout ---
    agent_list_items = [
        ft.ListTile(
            leading=ft.Icon(name="person_outline"),
            title=ft.Text(agent.role),
            subtitle=ft.Text(agent_id, size=10),
            on_click=select_agent,
            data=agent,
        ) for agent_id, agent in active_company.agents.items()
    ]
    
    sidebar = ft.Column(
        controls=[
            ft.Text("Agents", size=18, weight=ft.FontWeight.BOLD),
            ft.Column(controls=agent_list_items, scroll=ft.ScrollMode.AUTO)
        ],
        width=250,
        spacing=10,
    )

    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.VerticalDivider(width=1),
                ft.Column(controls=[
                    chat_view,
                    ft.Row(controls=[message_input, send_button])
                ], expand=True)
            ],
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)





