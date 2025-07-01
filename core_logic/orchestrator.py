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

# Import the protocol handlers
from core_logic.protocols import communication_protocol
from core_logic.protocols import escalation_protocol
from core_logic.protocols import delegation_protocol


# Define the safety limit for consecutive internal turns to prevent loops
MAX_INTERNAL_TURNS = 10

class Orchestrator:
    """
    The central OS of the Company-IA. It manages agents, communication flow,
    history, tools, and all system protocols.
    """
    def __init__(self, model_name="gemini-2.5-flash"):
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

    def add_to_history(self, agent_id: str, role: str, text: str):
        """Adds a message to an agent's personal history."""
        self.conversation_histories[agent_id].append({'role': role, 'parts': [text]})

    def get_history(self, agent_id: str) -> list:
        """Gets an agent's personal history."""
        return self.conversation_histories[agent_id]

    def direct_llm_query(self, prompt: str) -> str:
        """
        Performs a direct, simple query to the LLM without system prompts or history.
        Used for simple tasks like intent determination.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def query_llm(self, agent_id: str, task: str, history: list) -> str:
        """
        Sends a query to the LLM with the agent's specific role and history.
        """
        agent = self.agents[agent_id]
        system_prompt = agent.role_prompt
        
        messages = [
            {'role': 'user', 'parts': [system_prompt]},
            {'role': 'model', 'parts': ["Understood. I am ready to begin."]}
        ]
        messages.extend(history)
        messages.append({'role': 'user', 'parts': [task]})
        
        # Note: A production system would add more robust error handling here.
        response = self.model.generate_content(messages)
        return response.text

    # In core_logic/orchestrator.py

    def route_message(self, message: dict) -> dict:
        """
        Routes a structured message from a sender to a recipient and processes
        the response, triggering protocols as needed.
        """
        sender_id = message['sender']
        recipient_id = message['recipient']

        # --- NEW: Handle messages intended for the human user ---
        # If the recipient is the user, it means the conversation flow has
        # reached its end for this turn, and we should output the result.
        if recipient_id == 'user':
            print(f"[Orchestrator] Message for user from '{sender_id}'. Final output.")
            return message # Return the final message object directly.

        # Convert the structured message to a string for the receiving agent's LLM
        task_prompt = communication_protocol.parse_message_for_llm(message)
        
        # The recipient agent executes the task
        recipient_agent = self.agents[recipient_id]
        response_message = recipient_agent.execute_task(task_prompt)
        
        # Prepare the response for the next step in the chain
        response_message_full = {
            "sender": recipient_id,
            "recipient": self.get_parent(recipient_id) or 'user',
            **response_message
        }
        
        response_intent = response_message.get("intent")
        
        # If the response is a question, trigger the escalation protocol
        if response_intent == "REQUEST_INFORMATION":
            # NOTE: We pass the full response message to the protocol now
            return escalation_protocol.handle_question_escalation(
                self,
                start_agent_id=recipient_id,
                message=response_message_full
            )
        
        # If the response is to delegate, handle it.
        # This part of the logic is simplified for now.
        if response_intent == "ASSIGN_TASK":
             # In a future version, you could call the delegation_protocol here.
             pass

        # Otherwise, route the information to the next agent up the chain
        return self.route_message(response_message_full)

    def delegate_task(self, agent_id: str, task_prompt: str) -> str:
        """
        The main entry point for the user to assign a task to the system.
        """
        self.turn_counter = 0  # Reset counter for each new user task
        print(f"\n--- New Task Delegated to {agent_id} ---")
        print(f"Task: {task_prompt}")

        if agent_id not in self.agents:
            return f"Error: Agent '{agent_id}' not found."

        # The user is the ultimate sender, but we'll assign the CEO for protocol purposes
        sender_id = 'user' # In a more complex system, this could be the authenticated user

        # Build the initial structured message
        initial_message = communication_protocol.build_structured_message(
            self,
            sender_id='user',
            recipient_id=agent_id,
            intent='ASSIGN_TASK',
            payload={'KEY_INSTRUCTION': task_prompt}
        )
        
        # The agent executes the task
        agent = self.agents[agent_id]
        response_message = agent.execute_task(
            communication_protocol.parse_message_for_llm(initial_message)
        )
        
        # Process the agent's response
        final_result = self.route_message(
            {
                "sender": agent_id,
                "recipient": self.get_parent(agent_id) or 'user', # Respond to parent or user
                **response_message
            }
        )

        return final_result.get("payload", {}).get("DETAILS", "Task completed with no details.")