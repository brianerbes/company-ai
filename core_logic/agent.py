# core_logic/agent.py

"""
This file defines the Agent class, which is the blueprint for all individual
AI workers in the organization.
"""

from config.prompts import AGENT_PROMPTS
from config.communication_definitions import COMMUNICATION_DEFINITIONS


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

    def _determine_intent(self, task_prompt: str) -> str:
        """
        Uses the LLM to determine the primary intent of a given task.
        """
        print(f"[{self.agent_id}] Determining intent for task: '{task_prompt[:50]}...'")

        # Create a list of possible intents from our config file
        possible_intents = [
            f"- {intent['name']}: {intent['description']}"
            for intent in COMMUNICATION_DEFINITIONS['INTENT_DOMAIN']['primary_intents']
        ]
        intent_list_str = "\n".join(possible_intents)

        prompt = f"""
        Given the following task, which of these primary intents is most appropriate?
        Respond with ONLY the name of the intent (e.g., ASSIGN_TASK).

        Task: "{task_prompt}"

        Possible Intents:
        {intent_list_str}
        """

        # This is a simple, direct call to the LLM.
        response = self.orchestrator.direct_llm_query(prompt)
        # Clean up the response to get only the intent name
        determined_intent = response.strip().upper()
        print(f"[{self.agent_id}] Determined Intent: {determined_intent}")
        return determined_intent

    def execute_task(self, task_prompt: str) -> dict:
        """
        The main thinking loop for an agent. It determines intent, checks
        knowledge, executes the core logic, and prepares a structured response.

        Args:
            task_prompt (str): The plain text task assigned to the agent.

        Returns:
            dict: A response message object to be routed by the Orchestrator.
        """
        print(f"[{self.agent_id}] received task: '{task_prompt}'")

        # 1. First, check the knowledge base for a direct answer.
        # This saves on complex processing if the answer is already known.
        relevant_fact = self.orchestrator.knowledge_base.search_fact(task_prompt)
        if relevant_fact:
            print(f"[{self.agent_id}] Found relevant fact in Knowledge Base.")
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {
                    "EXECUTIVE_SUMMARY": "Answer found in knowledge base.",
                    "DETAILS": relevant_fact,
                    "POTENTIAL_IMPACT": "None. This is previously established information."
                }
            }

        # 2. If no fact is found, determine the core intent of the task.
        intent = self._determine_intent(task_prompt)

        # 3. Execute the main logic based on the determined intent.
        # For now, we will simplify this. A more advanced version would have
        # different logic paths for each intent. Here, we just assume the
        # agent needs to think about the task.
        print(f"[{self.agent_id}] Executing main logic for intent: {intent}")
        history = self.orchestrator.get_history(self.agent_id)
        llm_response = self.orchestrator.query_llm(self.agent_id, task_prompt, history)
        
        # 4. Analyze the LLM's response to formulate a final action.
        if llm_response.strip().startswith("[QUESTION]"):
            # If the agent needs more info, its final action is to escalate.
            question_text = llm_response.strip().replace("[QUESTION]", "").strip()
            return {
                "intent": "REQUEST_INFORMATION",
                "payload": {"QUESTION": question_text}
            }
        else:
            # Otherwise, its final action is to provide the generated information.
            self.orchestrator.add_to_history(self.agent_id, 'model', llm_response)
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {
                    "EXECUTIVE_SUMMARY": f"Completed task: {task_prompt[:30]}...",
                    "DETAILS": llm_response,
                    "POTENTIAL_IMPACT": "Varies based on content."
                }
            }