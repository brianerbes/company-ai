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
from core_logic.protocols import communication_protocol

# Define the safety limit for consecutive internal turns to prevent loops
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
        
        # Initialize core system managers
        self.file_system = FileSystemManager(base_path="virtual_fs")
        self.task_manager = TaskManager()
        self.audit_log = AuditLogger()
        
        self.hierarchy = HIERARCHY
        self.agents = {}
        self.human_agents = []
        
        # Create agent instances based on their type
        for agent_id, details in self.hierarchy.items():
            if details['type'] == 'ai':
                # We only create Agent objects for AI-type agents
                self.agents[agent_id] = Agent(agent_id, self)
            elif details['type'] == 'human':
                self.human_agents.append(agent_id)
        
        # The universal inbox system for all agents
        self.agent_inboxes = defaultdict(list)
        self.turn_counter = 0

        print("Orchestrator initialized successfully.")

    # --- Helper Methods ---
    def get_parent(self, agent_id: str) -> str | None:
        return self.hierarchy.get(agent_id, {}).get('parent')

    # --- LLM Query Methods ---
    def direct_llm_query(self, prompt: str) -> str:
        """Performs a direct, simple query to the LLM without context."""
        response = self.model.generate_content(prompt)
        return response.text

    def query_llm_for_agent(self, agent_id: str, prompt: str) -> str:
        """Sends a query to the LLM with the agent's specific role."""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Attempted to query LLM for non-AI agent: {agent_id}")

        full_prompt = f"{agent.role_prompt}\n\n--- TASK ---\n{prompt}"
        response = self.model.generate_content(full_prompt)
        return response.text

    # --- Main Loop and Routing ---
    def route_message_to_inbox(self, agent_id: str, message: dict):
        """Adds a message to an agent's inbox for processing."""
        if agent_id not in self.hierarchy:
            print(f"[Orchestrator] ERROR: Attempted to route message to non-existent agent '{agent_id}'.")
            return
        print(f"[Orchestrator] Routing message to '{agent_id}' inbox.")
        self.agent_inboxes[agent_id].append(message)

    def process_agent_inboxes(self):
        """Processes one turn of the AI agent inboxes."""
        for agent_id, inbox in self.agent_inboxes.items():
            if not inbox or self.hierarchy[agent_id]['type'] == 'human':
                continue

            message = inbox.pop(0)
            agent = self.agents[agent_id]
            response_message = agent.execute_task(message)
            
            if response_message:
                # This routing logic will be expanded to handle escalation etc.
                recipient = self.get_parent(agent_id) or "Owner" # Default to Owner
                self.route_message_to_inbox(recipient, response_message)

    def start_task(self, agent_id: str, task_prompt: str, user_as="Owner") -> dict:
        """
        Main entry point for the user to assign a task.
        Returns a response for the UI.
        """
        self.turn_counter = 0
        print(f"\n--- New Task Delegated to {agent_id} by {user_as} ---")

        if agent_id not in self.hierarchy:
            return {"status": "error", "message": f"Agent '{agent_id}' not found."}

        task_object = self.task_manager.create_task(
            description=task_prompt,
            delegator_id=user_as,
            assignee_id=agent_id
        )

        initial_message = {
            "task_id": task_object['task_id'],
            "intent": "ASSIGN_TASK",
            "payload": {"description": task_prompt}
        }
        
        self.route_message_to_inbox(agent_id, initial_message)
        
        # If the agent is an AI, we can process its response immediately for a chatbot-like feel
        if self.hierarchy[agent_id]['type'] == 'ai':
            # This is a simplified synchronous response loop
            response = self.agents[agent_id].execute_task(initial_message)
            return {"status": "success", "message": response.get("payload", {}).get("details", "Task processed.")}
        else: # If the agent is human
            return {"status": "pending", "message": f"Task {task_object['task_id']} assigned to human agent '{agent_id}'. It's now in their inbox."}