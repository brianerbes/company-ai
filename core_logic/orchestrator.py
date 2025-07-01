# core_logic/orchestrator.py

"""
This file defines the Orchestrator class, the central controller for the
entire multi-agent system.
"""

from collections import defaultdict
import google.generativeai as genai

# Import our custom modules
from config.hierarchy import HIERARCHY
from core_logic.agent import Agent
from knowledge_base import KnowledgeBase
from utils import configure_genai

# Define the safety limit for consecutive internal turns to prevent loops
MAX_INTERNAL_TURNS = 10

class Orchestrator:
    """
    The central OS of the Company-IA. It manages agents, communication flow,
    history, tools, and all system protocols.
    """
    def __init__(self, model_name="gemini-1.5-pro-latest"):
        """
        Initializes the entire multi-agent system.
        """
        print("Initializing Orchestrator...")

        # Configure the Generative AI model
        configure_genai()
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize subsystems
        self.knowledge_base = KnowledgeBase()
        
        # Load configurations
        self.hierarchy = HIERARCHY
        
        # Create all agent instances based on the hierarchy
        self.agents = {
            agent_id: Agent(agent_id, self) for agent_id in self.hierarchy
        }
        
        # Initialize state management properties
        self.conversation_histories = defaultdict(list)
        self.turn_counter = 0

        print("Orchestrator initialized successfully with all agents.")

    def get_parent(self, agent_id: str) -> str | None:
        """Helper function to get an agent's parent from the hierarchy."""
        return self.hierarchy.get(agent_id, {}).get('parent')

    def get_children(self, agent_id: str) -> list:
        """Helper function to get an agent's children from the hierarchy."""
        return self.hierarchy.get(agent_id, {}).get('children', [])

    def delegate_task(self, agent_id: str, task_prompt: str):
        """
        The main entry point for the user to assign a task to the system.
        This will eventually use the communication protocol to format the task
        into a structured message.
        """
        self.turn_counter = 0  # Reset counter for each new task
        print(f"\n--- New Task Delegated to {agent_id} ---")
        print(f"Task: {task_prompt}")

        # --- FUTURE LOGIC ---
        # 1. Convert the plain text task_prompt into a structured message object.
        #    e.g., {'intent': 'ASSIGN_TASK', 'payload': {'KEY_INSTRUCTION': task_prompt}}
        # 2. Call the target agent's execute_task method with the structured message.
        # 3. Process the final response to display to the user.
        pass

    def route_message(self, sender_id: str, recipient_id: str, message: dict):
        """
        Routes a structured message from one agent to another, enforcing
        communication rules.
        """
        # --- FUTURE LOGIC ---
        # 1. Check if communication is allowed between sender and recipient
        #    based on the hierarchy (parent, child, or sibling).
        # 2. If allowed, call the recipient agent's execute_task method.
        # 3. If not, return an error message to the sender agent.
        pass