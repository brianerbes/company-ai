# core_logic/agent.py

"""
This file defines the Agent class, which is the blueprint for all individual
AI workers in the organization.
"""

from config.prompts import AGENT_PROMPTS

class Agent:
    """
    Represents a single AI agent in the company.

    Each agent has a specific role and interacts with the system via the
    Orchestrator. It is designed to be mostly stateless, relying on the
    Orchestrator to manage history and communication flow.
    """
    def __init__(self, agent_id: str, orchestrator):
        """
        Initializes an Agent instance.

        Args:
            agent_id (str): The unique identifier for the agent (e.g., 'ceo').
            orchestrator: An instance of the Orchestrator class to mediate communication.
        """
        if agent_id not in AGENT_PROMPTS:
            raise ValueError(f"No role prompt defined for agent_id: {agent_id} in config/prompts.py")

        self.agent_id = agent_id
        self.orchestrator = orchestrator
        self.role_prompt = AGENT_PROMPTS[agent_id]
        print(f"Agent '{self.agent_id}' created.")

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the agent.
        """
        return f"Agent(id='{self.agent_id}')"

    def execute_task(self, structured_message: dict) -> dict:
        """
        The main thinking loop for an agent.

        This method will eventually determine the agent's intent,
        query the knowledge base, and then ask the Orchestrator to
        query the LLM to get a final response.

        For now, it's a placeholder.

        Args:
            structured_message (dict): A message object following our defined protocol.

        Returns:
            dict: A response message object.
        """
        print(f"[{self.agent_id}] received task: {structured_message.get('payload', {})}")
        # --- FUTURE LOGIC WILL GO HERE ---
        # 1. Determine core intent from the message.
        # 2. Query the KnowledgeBase via the Orchestrator for relevant facts.
        # 3. If no facts, formulate a prompt for the LLM.
        # 4. Call the Orchestrator to query the LLM.
        # 5. Process the LLM's response to see if it's a final answer or a question to be escalated.
        # 6. Return a structured response message.
        pass