import gradio as gr
from core_logic.orchestrator import Orchestrator

# 1. Initialize the Backend
orchestrator = Orchestrator()

# 2. Define the UI Interaction Logic
def handle_user_input(message, history, agent_selector):
    if not agent_selector:
        history.append((message, "**[System Error]** Please select an agent to delegate to."))
        return history, ""

    response = orchestrator.start_task(agent_selector, message, user_as="Owner")
    history.append((message, response))
    
    return history, ""

# 3. Build the Gradio Interface
def main_interface():
    agent_ids = list(orchestrator.hierarchy.keys())

    with gr.Blocks(title="Company-IA", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Company-IA Command Console")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Controls")
                agent_selector = gr.Dropdown(
                    label="Delegate Task To:",
                    choices=agent_ids,
                    value="ceo"
                )
            
            with gr.Column(scale=4):
                # --- CAMBIO 1: Arreglar el UserWarning ---
                chatbot = gr.Chatbot(label="System Output", height=500, type="messages")
                msg_textbox = gr.Textbox(
                    placeholder="Type your high-level task here and press Enter...",
                    label="Your Command"
                )
                
                msg_textbox.submit(handle_user_input, [msg_textbox, chatbot, agent_selector], [chatbot, msg_textbox])

    return app

# 4. Launch the App
if __name__ == "__main__":
    app = main_interface()
    # --- CAMBIO 2: Añadir share=True para crear un enlace público ---
    app.launch(server_port=7861, share=True)