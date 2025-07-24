# app.py

from flask import Flask, render_template, request, jsonify
from core_logic.orchestrator import Orchestrator

# Initialize the Flask App and the Orchestrator
app = Flask(__name__)
orchestrator = Orchestrator()

@app.route('/')
def home():
    """Serves the main chat interface."""
    return render_template('index.html')

@app.route('/get_agents', methods=['GET'])
def get_agents():
    """Provides the list of agents to populate the dropdown menu."""
    agent_ids = list(orchestrator.hierarchy.keys())
    return jsonify({"agents": agent_ids})

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Receives a message from the UI, processes it via the Orchestrator,
    and returns a structured response for the chat.
    """
    data = request.get_json()
    agent_id = data.get('agent_id')
    prompt = data.get('prompt')

    if not agent_id or not prompt:
        return jsonify({"response": "[System Error] Missing agent_id or prompt."}), 400

    # Call the orchestrator to start the task.
    # The orchestrator now returns a dictionary with the status and message.
    response_data = orchestrator.start_task(agent_id, prompt, user_as="Owner")
    
    # Return the message from the orchestrator to be displayed in the chat.
    return jsonify({"response": response_data.get("message")})

if __name__ == "__main__":
    # debug=True is for development. In production, a proper WSGI server is used.
    app.run(port=5001, debug=True)