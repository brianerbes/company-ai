# core_logic/orchestrator.py

import google.generativeai as genai
from collections import defaultdict

# Import our custom modules
from config.hierarchy import HIERARCHY
from core_logic.agent import Agent
from core_logic.file_system_manager import FileSystemManager
from core_logic.task_manager import TaskManager
from core_logic.audit_log import AuditLogger
from utils import configure_genai

# Import the protocol handlers
from core_logic.protocols import communication_protocol
# Note: Escalation and Delegation logic will be more deeply integrated here for now.

# Define the safety limit
MAX_INTERNAL_TURNS = 15

class Orchestrator:
    """
    The central OS of the Company-IA. It manages agents, communication flow,
    history, tools, and all system protocols.
    """
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        print("Initializing Orchestrator...")
        configure_genai()
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize core systems
        self.file_system = FileSystemManager(base_path="virtual_fs")
        self.task_manager = TaskManager()
        self.audit_log = AuditLogger()
        
        self.hierarchy = HIERARCHY
        self.agents = {}
        self.human_agents = []
        
        # Create agent instances based on type
        for agent_id, details in self.hierarchy.items():
            if details['type'] == 'ai':
                self.agents[agent_id] = Agent(agent_id, self)
            elif details['type'] == 'human':
                self.human_agents.append(agent_id)
                self.agents[agent_id] = None # Placeholder for human agents
        
        self.agent_inboxes = defaultdict(list)
        self.turn_counter = 0
        print("Orchestrator initialized successfully.")

    def get_parent(self, agent_id: str) -> str | None:
        return self.hierarchy.get(agent_id, {}).get('parent')

    # --- LLM Query Methods ---
    def direct_llm_query(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def query_llm(self, agent_id: str, task: str, context: str = "") -> str:
        agent = self.agents[agent_id]
        system_prompt = agent.role_prompt
        
        full_prompt = f"{system_prompt}\n\n--- CONTEXT ---\n{context}\n\n--- TASK ---\n{task}"
        
        response = self.model.generate_content(full_prompt)
        return response.text

    # --- Main Loop and Routing ---
    def route_message_to_agent(self, agent_id: str, message: dict):
        """Adds a message to an agent's inbox."""
        print(f"[Orchestrator] Routing message to '{agent_id}' inbox.")
        self.agent_inboxes[agent_id].append(message)

    def process_agent_inboxes(self):
        """Processes the next message in each agent's inbox."""
        # This is a simple round-robin scheduler. A more complex one could use priority.
        for agent_id, inbox in self.agent_inboxes.items():
            if not inbox:
                continue

            message = inbox.pop(0)
            
            # If the agent is human, we stop and wait for user input.
            if self.hierarchy[agent_id]['type'] == 'human':
                print(f"\n--- PENDING ACTION for Human Agent: {agent_id} ---")
                print(f"Task: {message}")
                # The main loop in main.py will now handle this.
                # We put the message back in the inbox to be handled by the user.
                inbox.insert(0, message)
                return

            # If the agent is AI, it processes the task.
            agent = self.agents[agent_id]
            response_message = agent.execute_task(message) # Assumes agent.execute_task is updated
            
            # Route the agent's response
            if response_message:
                recipient = response_message.get('recipient', self.get_parent(agent_id))
                self.route_message_to_agent(recipient, response_message)

    def start_task(self, agent_id: str, task_prompt: str, user_as="Owner"):
        """
        Main entry point for the user to assign a task.
        """
        if agent_id not in self.hierarchy:
            return f"Error: Agent '{agent_id}' not found."
        
        print(f"\n--- New Task Delegated to {agent_id} by {user_as} ---")
        
        # Create the initial task in the TaskManager
        task_object = self.task_manager.create_task(
            description=task_prompt,
            delegator_id=user_as,
            assignee_id=agent_id
        )

        # Create the initial message for the agent's inbox
        initial_message = {
            "task_id": task_object['task_id'],
            "intent": "ASSIGN_TASK",
            "payload": {"description": task_prompt}
        }
        
        self.route_message_to_agent(agent_id, initial_message)
        # In a real async application, the loop would run independently.
        # For our CLI, we might need to manually trigger processing.
        self.process_agent_inboxes() # Process one turn
        
        return f"Task {task_object['task_id']} has been assigned to {agent_id} and is now in their inbox."