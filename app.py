import flet as ft
from pathlib import Path
import time
from core.company import Company, discover_companies
from core.task import TaskStatus

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

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

    # --- UI Controls ---
    chat_view = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
    message_input = ft.TextField(hint_text="Type a message...", expand=True, on_submit=lambda e: send_message(e.control.value))
    send_button = ft.IconButton(icon="send_rounded", on_click=lambda e: send_message(message_input.value))
    progress_ring = ft.ProgressRing()

    def set_thinking_state(thinking: bool):
        """Disables the input and shows a progress ring while the agent works."""
        message_input.disabled = thinking
        send_button.disabled = thinking
        if thinking:
            chat_view.controls.append(progress_ring)
        else:
            # Find and remove the progress ring
            for control in chat_view.controls:
                if isinstance(control, ft.ProgressRing):
                    chat_view.controls.remove(control)
                    break
        page.update()

    def on_message(msg):
        """PubSub handler to display messages from the backend."""
        msg_channel = msg.get("channel")
        if not selected_agent or msg_channel != selected_agent.id:
            return

        mtype = msg.get("type")
        text = msg.get("text")
        agent_role = msg.get("agent", "System")
        
        selected_agent.chat_history.append({"speaker": agent_role, "text": text, "type": mtype})
        
        if mtype == "user_facing":
            chat_view.controls.append(ft.Text(f"{agent_role}: {text}", size=14))
        
        page.update()

    page.pubsub.subscribe(on_message)

    def send_message(user_message: str):
        if not user_message or not selected_agent:
            return

        # Display user message and save to history
        chat_view.controls.append(ft.Text(f"You: {user_message}", size=14, weight=ft.FontWeight.BOLD))
        selected_agent.chat_history.append({"speaker": "You", "text": user_message, "type": "user"})
        message_input.value = ""
        page.update()

        # Set UI to "thinking" state
        set_thinking_state(True)
        
        # --- SYNCHRONOUS TASK EXECUTION ---
        # Create a new task for the agent
        task = active_company.create_task(description=user_message, assignee_id=selected_agent.id, ui_channel=selected_agent.id)
        # Directly process the task
        agent = active_company.agents.get(task.assignee_id)
        if agent:
            agent.process_task(task) # This is now a direct, blocking call
        
        # We don't need a complex scheduler anymore for simple conversations
        # For now, we assume the task is done after one agent's turn.
        task.set_status(TaskStatus.COMPLETED)
        # --- END SYNCHRONOUS EXECUTION ---

        # Set UI back to "active" state
        set_thinking_state(False)

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
            elif mtype == "user_facing":
                chat_view.controls.append(ft.Text(f"{speaker}: {text}", size=14))
        page.update()

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
    sidebar = ft.Column(controls=[ft.Text("Agents", size=18, weight=ft.FontWeight.BOLD)] + agent_list_items, width=250)

    page.add(
        ft.Row(controls=[
            sidebar,
            ft.VerticalDivider(width=1),
            ft.Column(controls=[
                chat_view,
                ft.Row(controls=[message_input, send_button])
            ], expand=True)
        ], expand=True)
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)