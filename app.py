from flask import Flask, render_template, request, jsonify
from core_logic.orchestrator import Orchestrator

# 1. Initialize the Flask App and the Orchestrator
app = Flask(__name__)
orchestrator = Orchestrator()

# 2. Define the main route to serve the HTML page
@app.route('/')
def home():
    """Serves the main chat interface."""
    return render_template('index.html')

# 3. Define an API endpoint to get the list of agents
@app.route('/get_agents', methods=['GET'])
def get_agents():
    """Provides the list of agents to populate the dropdown menu."""
    agent_ids = list(orchestrator.hierarchy.keys())
    return jsonify({"agents": agent_ids})

# 4. Define the main API endpoint for sending messages
@app.route('/send_message', methods=['POST'])
def send_message():
    """Receives a message from the UI, processes it, and returns the response."""
    data = request.get_json()
    agent_id = data.get('agent_id')
    prompt = data.get('prompt')

    if not agent_id or not prompt:
        return jsonify({"response": "[System Error] Missing agent_id or prompt."}), 400

    # This is the same method we used in the command-line version
    response = orchestrator.start_task(agent_id, prompt, user_as="Owner")
    
    return jsonify({"response": response})

# 5. Run the Flask App
if __name__ == "__main__":
    # Note: debug=True is for development. In production, a proper WSGI server is used.
    app.run(port=5001, debug=True)