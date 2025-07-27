import flet as ft
from pathlib import Path
from core.company import Company, discover_companies

WORKSPACE_ROOT = Path(__file__).parent / "workspace"

def main(page: ft.Page):
    page.title = "CompanIA"
    page.window_width = 1200
    page.window_height = 800
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Data Loading ---
    # Show a progress ring while we load the company data
    progress_ring = ft.ProgressRing()
    page.add(progress_ring)
    page.update()

    company_manifests = discover_companies(WORKSPACE_ROOT)
    if not company_manifests:
        page.controls.clear()
        page.add(ft.Text("FATAL: No valid companies found in workspace. Exiting.", size=20))
        page.update()
        return

    selected_manifest = company_manifests[0]
    company_path = selected_manifest.pop('_company_path')
    active_company = Company(selected_manifest, company_path)
    active_company.load_agents()

    # --- UI Controls and Event Handlers ---
    chat_view = ft.ListView(
        controls=[ft.Text("Select an agent to begin...", size=16, text_align=ft.TextAlign.CENTER)],
        expand=True,
        auto_scroll=True,
        spacing=10,
        padding=20,
    )

    def select_agent(e):
        """Called when an agent is clicked in the sidebar."""
        selected_agent = e.control.data
        
        # Clear the chat and add a header
        chat_view.controls.clear()
        chat_view.controls.append(
             ft.Text(f"Conversation with {selected_agent.role}", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        )
        chat_view.controls.append(ft.Divider())
        page.update()

    # --- Build the Sidebar ---
    agent_list_items = []
    for agent_id, agent in active_company.agents.items():
        agent_list_items.append(
            ft.ListTile(
                leading=ft.Icon(name="person_outline"),
                title=ft.Text(agent.role),
                subtitle=ft.Text(agent_id, size=10),
                on_click=select_agent,
                data=agent,
            )
        )
    
    sidebar = ft.Column(
        controls=[
            ft.Text("Agents", size=18, weight=ft.FontWeight.BOLD),
            ft.Column(controls=agent_list_items, scroll=ft.ScrollMode.AUTO)
        ],
        width=250,
        spacing=10,
    )

    # --- Build the Final Layout ---
    # Clear the progress ring and add the final UI
    page.controls.clear()
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.padding = 10
    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.VerticalDivider(width=1),
                chat_view,
            ],
            expand=True,
        )
    )
    page.update()

# --- Run the Application ---
if __name__ == "__main__":
    ft.app(target=main)