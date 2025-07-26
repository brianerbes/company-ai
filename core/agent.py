import json
from pathlib import Path
from .vfs import FileSystemManager
from .task import Task, TaskStatus
from .llm_api import generate_structured_response # Import the LLM call function

class Agent:
    """
    Represents a single AI agent in the system.
    """
    def __init__(self, agent_id: str, agent_meta: dict, company_fs: FileSystemManager):
        self.id = agent_id
        self.meta = agent_meta
        self.fs = company_fs
        
        self.role = self.meta.get('role', 'Generic Agent')
        self.system_prompt = self.meta.get('system_prompt', 'You are a helpful assistant.')
    
    def __repr__(self) -> str:
        return f"<Agent id='{self.id}' role='{self.role}'>"

    def print_summary(self):
        """Prints a brief summary of the agent's identity."""
        print(f"  - Agent ID: {self.id}")
        print(f"    Role: {self.role}")
        
    def _construct_prompt(self, task: Task) -> str:
        """Constructs the full prompt for the LLM based on agent and task context."""
        
        # This is the "Invisible Protocol" (SAID) defined in the blueprint.
        # We are instructing the LLM on how to behave and format its response.
        said_format = """
        {
          "reasoning": "A brief, step-by-step thought process for how you will approach the task. Explain your plan.",
          "actions": [
            {
              "tool_name": "TOOL_NAME",
              "payload": {
                "param1": "value1",
                "param2": "value2"
              }
            }
          ]
        }
        """

        prompt = f"""
        You are an AI agent. Do not act as a user.
        
        Your Identity:
        {self.system_prompt}

        Your assigned task is:
        "{task.description}"

        Your available tools are: {json.dumps(self.meta.get('capabilities', {}).get('allowed_tools', []))}

        Based on your identity and the task, you must formulate a plan.
        Your response MUST be a valid JSON object following this exact structure (do NOT output any other text, just the JSON):
        {said_format}
        """
        return prompt

    def process_task(self, task: Task):
        """
        Processes a given task by calling the LLM and parsing the response.
        """
        print(f"\nAgent '{self.role}' is now processing Task {task.task_id}...")
        task.set_status(TaskStatus.IN_PROGRESS)
        
        # 1. Construct the prompt
        prompt = self._construct_prompt(task)
        
        # 2. Call the LLM
        raw_response = generate_structured_response(prompt)
        
        if not raw_response:
            print("  -> Agent failed to get a response from the LLM.")
            task.set_status(TaskStatus.FAILED, "No response from LLM.")
            return

        print("  -> Agent received a response from the LLM.")
        
        # 3. Parse and display the response
        try:
            # Clean the response to ensure it's valid JSON
            clean_response = raw_response.strip().replace("```json", "").replace("```", "")
            parsed_response = json.loads(clean_response)
            
            print("\n--- Agent's Plan ---")
            print(f"Reasoning: {parsed_response.get('reasoning')}")
            print("Proposed Actions:")
            for i, action in enumerate(parsed_response.get('actions', [])):
                print(f"  {i+1}. Tool: {action.get('tool_name')}")
                print(f"     Payload: {action.get('payload')}")
            print("--------------------\n")
            
            # For now, we'll just mark it as complete after planning.
            task.set_status(TaskStatus.COMPLETED, "Agent plan generated successfully.")
            
        except json.JSONDecodeError:
            print("  -> ERROR: Agent returned invalid JSON. Could not parse the plan.")
            print(f"  -> Raw Response:\n{raw_response}")
            task.set_status(TaskStatus.FAILED, "Agent returned invalid JSON.")