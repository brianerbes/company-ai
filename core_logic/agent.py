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

    def execute_task(self, message: dict) -> dict | None:
        """
        The main thinking loop for an agent, executed when it processes a message
        from its inbox.

        Args:
            message (dict): The message object from the agent's inbox.

        Returns:
            A dictionary representing the agent's desired next action, or None.
        """
        task_id = message.get("task_id")
        task_prompt = message.get("payload", {}).get("description", "No description provided.")
        print(f"[{self.agent_id}] is executing Task {task_id}: '{task_prompt[:60]}...'")

        # 1. Update task status to IN_PROGRESS
        if task_id:
            self.orchestrator.task_manager.update_task_status(task_id, 'IN_PROGRESS', self.agent_id)

        # 2. Check the Knowledge Base first
        relevant_fact = self.orchestrator.knowledge_base.search_fact(task_prompt)
        if relevant_fact:
            print(f"[{self.agent_id}] Found relevant fact in Knowledge Base.")
            # If fact is found, the task is to provide it.
            if task_id:
                self.orchestrator.task_manager.update_task_status(task_id, 'COMPLETED', self.agent_id)
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {"details": relevant_fact}
            }

        # 3. Formulate the full prompt for the LLM to get a plan
        # In a more advanced version, context injection would happen here.
        # For now, we pass the main task prompt.
        plan_prompt = f"""
        Based on your role and the following task, what is your plan?
        Your plan should be a sequence of intents. Choose from the available intents.
        If you need to ask a question, your plan should be a single REQUEST_INFORMATION intent.
        If you have the answer, your plan should be a single PROVIDE_INFORMATION intent with the details.
        If you need to create and then write to a file, your plan can be [CREATE_FILE, WRITE_FILE].

        TASK: "{task_prompt}"

        AVAILABLE INTENTS: {[intent['name'] for intent in COMMUNICATION_DEFINITIONS['INTENT_DOMAIN']['primary_intents']]}

        Provide only the final action or sequence of actions.
        """
        
        # 4. Query the LLM for a plan
        # We use a more direct query here that includes the role but not the whole history
        raw_plan = self.orchestrator.query_llm(self.agent_id, plan_prompt)

        # For now, we will assume the agent's response is the final information.
        # A more complex system would parse the `raw_plan` and execute multiple intents.
        print(f"[{self.agent_id}] LLM Response/Plan: '{raw_plan[:100]}...'")

        # 5. Analyze the response and formulate a final action
        if "[QUESTION]" in raw_plan.upper():
            question = raw_plan.replace("[QUESTION]", "").strip()
            return {
                "intent": "REQUEST_INFORMATION",
                "payload": {"QUESTION": question}
            }
        else:
            # If it's not a question, assume the task is complete for this turn.
            if task_id:
                self.orchestrator.task_manager.update_task_status(task_id, 'COMPLETED', self.agent_id)
            
            return {
                "intent": "PROVIDE_INFORMATION",
                "payload": {"details": raw_plan}
            }