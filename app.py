import flet as ft
from pathlib import Path
import time
import threading
import json
from core.company import Company, discover_companies
from core.task import TaskStatus

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

# --- THE SINGLETON SCHEDULER ---
class Scheduler:
    def __init__(self, company: Company):
        self.company = company
        self.is_running = True
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.is_running = False

    def run(self):
        print("--- Main Scheduler Loop Started ---")
        while self.is_running:
            try:
                # 1. Un-block tasks
                for task in list(self.company.tasks.values()):
                    if task.status == TaskStatus.BLOCKED:
                        if all(self.company.tasks.get(dep_id, t).status == TaskStatus.COMPLETED for dep_id in task.dependencies):
                            task.set_status(TaskStatus.PENDING, f"All dependencies complete.")

                # 2. Find and execute a runnable task
                runnable_tasks = [t for t in self.company.tasks.values() if t.status == TaskStatus.PENDING]
                
                if runnable_tasks:
                    task_to_run = runnable_tasks[0] # Process one task per cycle
                    agent = self.company.agents.get(task_to_run.assignee_id)
                    if agent:
                        agent.process_task(task_to_run)
                
                # Prevent busy-waiting
                time.sleep(1)

            except Exception as e:
                print(f"FATAL ERROR in scheduler loop: {e}")
                time.sleep(5)
        
        print("\n--- Scheduler Finished ---")

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

    # --- Create and start the single, persistent scheduler ---
    scheduler = Scheduler(company=active_company)
    scheduler.start()
    page.window_destroy = lambda e: scheduler.stop() # Stop scheduler when window closes

    # --- App State ---
    selected_agent = None

    # --- UI Controls & Handlers ---
    chat_view = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)

    def on_message(msg):
        msg_channel = msg.get("channel")
        if not selected_agent or (msg_channel and msg_channel != selected_agent.id):
            return

        mtype = msg.get("type")
        text = msg.get("text")
        agent_role = msg.get("agent", "System")
        
        if selected_agent:
            selected_agent.chat_history.append({"speaker": agent_role, "text": text, "type": mtype})
        
        if mtype == "user_facing" or mtype == "system":
            is_system = mtype == "system"
            chat_view.controls.append(ft.Text(f"{agent_role}: {text}", size=14, italic=is_system, color="white50" if is_system else "white"))
            page.update()

    page.pubsub.subscribe(on_message)

    def send_message(user_message: str):
        if not user_message or not selected_agent:
            return

        selected_agent.chat_history.append({"speaker": "You", "text": user_message, "type": "user"})
        chat_view.controls.append(ft.Text(f"You: {user_message}", size=14, weight=ft.FontWeight.BOLD))
        message_input.value = ""
        
        # Simply add a new task to the queue. The running scheduler will pick it up.
        active_company.create_task(description=user_message, assignee_id=selected_agent.id, ui_channel=selected_agent.id)
        page.update()

    message_input = ft.TextField(hint_text="Type a message...", expand=True, on_submit=lambda e: send_message(e.control.value))
    send_button = ft.IconButton(icon="send_rounded", on_click=lambda e: send_message(message_input.value))

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

            if mtype == "user":
                chat_view.controls.append(ft.Text(f"You: {text}", size=14, weight=ft.FontWeight.BOLD))
            elif mtype == "user_facing" or mtype == "system":
                is_system = mtype == "system"
                chat_view.controls.append(ft.Text(f"{speaker}: {text}", size=14, italic=is_system, color="white50" if is_system else "white"))
        page.update()

    # --- Build the UI Layout ---
    agent_list_items = [ft.ListTile(leading=ft.Icon(name="person_outline"), title=ft.Text(agent.role), subtitle=ft.Text(agent_id, size=10), on_click=select_agent, data=agent) for agent_id, agent in active_company.agents.items()]
    sidebar = ft.Column(controls=[ft.Text("Agents", size=18, weight=ft.FontWeight.BOLD), ft.Column(controls=agent_list_items, scroll=ft.ScrollMode.AUTO)], width=250, spacing=10)

    page.add(ft.Row(controls=[sidebar, ft.VerticalDivider(width=1), ft.Column(controls=[chat_view, ft.Row(controls=[message_input, send_button])], expand=True)], expand=True))
    page.update()

if __name__ == "__main__":
    ft.app(target=main)