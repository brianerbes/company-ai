# core_logic/agent.py

"""
This file defines the Agent class, which is the blueprint for all individual
AI workers in the organization.
"""

from config.prompts import AGENT_PROMPTS
from config.communication_definitions import COMMUNICATION_DEFINITIONS

class Agent:
    """
    Represents a single AI agent in the company. It processes tasks from its
    inbox and formulates a response intent for the Orchestrator to execute.
    """
    def __init__(self, agent_id: str, orchestrator):
        if agent_id not in AGENT_PROMPTS:
            raise ValueError(f"No role prompt defined for agent_id: {agent_id} in config/prompts.py")

        self.agent_id = agent_id
        self.orchestrator = orchestrator
        self.role_prompt = AGENT_PROMPTS[agent_id]
        print(f"Agent '{self.agent_id}' created.")

    def __repr__(self) -> str:
        return f"Agent(id='{self.agent_id}')"

    def _determine_intent(self, task_prompt: str) -> str:
        """
        Uses the LLM to determine the primary intent of a given task.
        """
        print(f"[{self.agent_id}] Determining intent for task: '{task_prompt[:50]}...'")

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
        response = self.orchestrator.direct_llm_query(prompt)
        determined_intent = response.strip().upper()
        print(f"[{self.agent_id}] Determined Intent: {determined_intent}")
        return determined_intent

    def execute_task(self, message: dict) -> dict | None:
        """
        The main thinking loop for an agent, executed when it processes a message.
        """
        task_id = message.get("task_id")
        task_prompt = message.get("payload", {}).get("description", "No description provided.")
        print(f"[{self.agent_id}] is executing Task {task_id}: '{task_prompt[:60]}...'")

        if task_id:
            self.orchestrator.task_manager.update_task_status(task_id, 'IN_PROGRESS', self.agent_id)

        relevant_fact = self.orchestrator.knowledge_base.search_fact(task_prompt)
        if relevant_fact:
            print(f"[{self.agent_id}] Found relevant fact in Knowledge Base.")
            if task_id:
                self.orchestrator.task_manager.update_task_status(task_id, 'COMPLETED', self.agent_id)
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {"details": relevant_fact}
            }
        
        # This is a simplified logic loop. A more advanced version would use the
        # determined intent to choose different actions (e.g., use file system).
        
        # Query the LLM for a direct response to the task.
        llm_response = self.orchestrator.query_llm_for_agent(self.agent_id, task_prompt)
        print(f"[{self.agent_id}] LLM Response: '{llm_response[:100]}...'")

        # Analyze the response and formulate a final action
        if "[QUESTION]" in llm_response.upper():
            question = llm_response.replace("[QUESTION]", "").strip()
            return {
                "intent": "REQUEST_INFORMATION",
                "payload": {"QUESTION": question}
            }
        else:
            if task_id:
                self.orchestrator.task_manager.update_task_status(task_id, 'COMPLETED', self.agent_id)
            
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {"details": llm_response}
            }