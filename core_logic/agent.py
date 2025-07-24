# core_logic/agent.py

import json
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

    def execute_task(self, message: dict) -> dict:
        """
        The main thinking loop for an agent. It formulates a plan and returns
        the first actionable step for the Orchestrator.
        """
        task_id = message.get("task_id")
        task_prompt = message.get("payload", {}).get("description", "No description provided.")
        print(f"[{self.agent_id}] executing Task {task_id}: '{task_prompt[:60]}...'")

        if task_id:
            self.orchestrator.task_manager.update_task_status(task_id, 'IN_PROGRESS', self.agent_id)

        # Formulate the prompt to get a structured plan from the LLM
        possible_intents = [f"'{intent['name']}'" for intent in COMMUNICATION_DEFINITIONS['INTENT_DOMAIN']['primary_intents']]
        
        plan_prompt = f"""
        You are an AI agent with the role: {self.role_prompt}
        Your task is: "{task_prompt}"

        Based on your task, determine the single most appropriate next action (intent) to take.
        Your available intents are: {', '.join(possible_intents)}.

        Respond in a JSON format with two keys:
        1. "intent": The name of the intent you have chosen.
        2. "payload": A dictionary containing the necessary data for that intent.
           - For PROVIDE_INFORMATION, the payload should be {{"details": "your full response here"}}.
           - For REQUEST_INFORMATION, the payload should be {{"QUESTION": "your specific question here"}}.
           - For CREATE_FILE, the payload should be {{"filename": "path/to/file.txt"}}.
           - For WRITE_FILE, the payload should be {{"filename": "path/to/file.txt", "content": "the content to write"}}.

        Example:
        If the task is "Write a summary of our goals to goals.txt", your response should be:
        {{
            "intent": "WRITE_FILE",
            "payload": {{
                "filename": "goals.txt",
                "content": "Our main goal is to deliver a high-quality product..."
            }}
        }}

        Now, provide the JSON for your task.
        """
        
        # Query the LLM for a structured plan
        raw_response = self.orchestrator.direct_llm_query(plan_prompt)
        print(f"[{self.agent_id}] LLM Raw Response: '{raw_response[:150]}...'")

        # Parse the JSON response from the LLM
        try:
            # Clean up the response to ensure it's valid JSON
            json_response_str = raw_response.strip().replace("```json", "").replace("```", "")
            action = json.loads(json_response_str)
        except json.JSONDecodeError:
            print(f"[{self.agent_id}] ERROR: Failed to decode LLM response into JSON. Defaulting to PROVIDE_INFORMATION.")
            # Fallback for when the LLM doesn't respond with valid JSON
            action = {
                "intent": "PROVIDE_INFORMATION",
                "payload": {"details": raw_response}
            }

        # Add the task_id to the final action for tracking
        action['task_id'] = task_id
        
        # If the task is considered complete by this action, update the status.
        if action['intent'] in ["PROVIDE_INFORMATION", "REQUEST_INFORMATION"]:
             if task_id:
                self.orchestrator.task_manager.update_task_status(task_id, 'COMPLETED', self.agent_id)
        
        return action