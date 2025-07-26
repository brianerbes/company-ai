import json
from pathlib import Path
from .vfs import FileSystemManager
from .task import Task, TaskStatus
from .llm_api import generate_structured_response
from .orchestrator import execute_actions

class Agent:
    def __init__(self, agent_id: str, agent_meta: dict, company_fs: FileSystemManager):
        self.id = agent_id
        self.meta = agent_meta
        self.fs = company_fs
        self.role = self.meta.get('role', 'Generic Agent')
        self.system_prompt = self.meta.get('system_prompt', 'You are a helpful assistant.')
    
    def __repr__(self) -> str:
        return f"<Agent id='{self.id}' role='{self.role}'>"

    def print_summary(self):
        print(f"  - Agent ID: {self.id}")
        print(f"    Role: {self.role}")
        
    def _get_tool_manifest(self) -> str:
        tool_descriptions = {
            "CREATE_FILE": "Creates a new, empty file. Payload requires a 'path'.",
            "WRITE_FILE": "Writes content to a file, overwriting it. Payload requires 'path' and 'content'.",
            "READ_FILE": "Reads the content of a file. Payload requires a 'path'.",
            "DELEGATE_TASK": "Delegates a new task to another agent. Payload requires 'assignee_id' and 'description'."
        }
        available_tools = self.meta.get('capabilities', {}).get('allowed_tools', [])
        manifest = "Your available tools and their required parameters are:\n"
        for tool_name in available_tools:
            description = tool_descriptions.get(tool_name, "No description available.")
            manifest += f"- {tool_name}: {description}\n"
        return manifest

    def _construct_initial_prompt(self, task: Task) -> str:
        said_format = """
        {
          "reasoning": "A brief, step-by-step thought process for how you will approach the task. Explain your plan.",
          "actions": [
            {
              "tool_name": "TOOL_NAME",
              "payload": {
                "param1": "value1"
              }
            }
          ]
        }
        """
        tool_manifest = self._get_tool_manifest()
        prompt = f"""
        You are an AI agent. Do not act as a user.
        
        Your Identity:
        {self.system_prompt}

        Your assigned task is:
        "{task.description}"

        {tool_manifest}

        Based on your identity and the task, you must formulate a plan.
        Your response MUST be a valid JSON object following this exact structure (do NOT output any other text, just the JSON):
        {said_format}
        """
        return prompt

    def _construct_iteration_prompt(self, task: Task, previous_attempts: list) -> str:
        said_format = """
        {
          "reasoning": "A new, improved reasoning for how you will address the critiques from your last attempt.",
          "actions": [
            {
              "tool_name": "TOOL_NAME",
              "payload": {
                "param1": "value1"
              }
            }
          ]
        }
        """
        tool_manifest = self._get_tool_manifest()
        history = ""
        for i, attempt in enumerate(previous_attempts):
            history += f"\n--- Attempt #{i+1} ---\n"
            history += f"Plan: {json.dumps(attempt['plan'], indent=2)}\n"
            history += f"Execution Results: {json.dumps(attempt['execution_results'], indent=2)}\n"
            history += f"Self-Critique: {attempt['critique']['critique']}\n"
            history += "------------------\n"

        prompt = f"""
        You are an AI agent attempting to complete a task. You have tried before and failed.
        Use your previous self-critique to formulate a new, improved plan.

        Your Identity:
        {self.system_prompt}

        The original task is:
        "{task.description}"

        Review your previous attempts:
        {history}

        Based on your critique of what went wrong, create a new plan to fully complete the task.
        
        {tool_manifest}
        
        Your new response MUST be a valid JSON object following this exact structure:
        {said_format}
        """
        return prompt

    def _construct_reflection_prompt(self, task: Task, plan: dict, execution_results: list) -> str:
        """Constructs a prompt for the agent to reflect on its own work."""
        reflection_format = """
        {
          "critique": "Critically evaluate your own work. Did you fully accomplish the original task? Were there any errors or oversights in the execution? Was the result of high quality?",
          "is_complete": true
        }
        """
        prompt = f"""
        You are an AI agent reflecting on a task you just attempted.

        Your Identity:
        {self.system_prompt}

        The original task was:
        "{task.description}"

        This was your plan:
        {json.dumps(plan, indent=2)}

        These were the results of executing your plan:
        {json.dumps(execution_results, indent=2)}

        Now, reflect on your work. Critically evaluate whether you successfully completed the original task based on the execution results.
        **CRUCIAL RULE: If your critique identifies ANY missing details, errors, or low-quality output, you MUST set 'is_complete' to false.** Only set 'is_complete' to true if the original task has been fully satisfied to a professional standard.

        Your response MUST be a valid JSON object following this exact structure:
        {reflection_format}
        """
        return prompt

    def process_task(self, task: Task):
        print(f"\nAgent '{self.role}' is processing Task {task.task_id}...")
        
        max_iterations = 3
        iteration_count = 0
        previous_attempts = []
        is_complete = False

        while not is_complete and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n{'='*10} Starting Iteration #{iteration_count} {'='*10}")

            # === 1. PLAN PHASE ===
            print("\n--- Phase 1: Planning ---")
            task.set_status(TaskStatus.IN_PROGRESS, f"Agent is planning iteration {iteration_count}.")
            if iteration_count == 1:
                plan_prompt = self._construct_initial_prompt(task)
            else:
                plan_prompt = self._construct_iteration_prompt(task, previous_attempts)
            
            raw_plan_response = generate_structured_response(plan_prompt)
            if not raw_plan_response:
                task.set_status(TaskStatus.FAILED, "Agent failed to generate a plan.")
                return

            try:
                plan = json.loads(raw_plan_response.strip().replace("```json", "").replace("```", ""))
                print(f"Agent's Plan Reasoning: {plan.get('reasoning')}")
            except json.JSONDecodeError:
                task.set_status(TaskStatus.FAILED, f"Agent returned invalid JSON for its plan. Raw response: {raw_plan_response}")
                return
            
            # === 2. EXECUTE PHASE ===
            print("\n--- Phase 2: Execution ---")
            actions = plan.get('actions', [])
            execution_results = execute_actions(actions, self.fs) if actions else []

            # === 3. REFLECT PHASE ===
            print("\n--- Phase 3: Reflection ---")
            reflection_prompt = self._construct_reflection_prompt(task, plan, execution_results)
            raw_reflection_response = generate_structured_response(reflection_prompt)
            if not raw_reflection_response:
                task.set_status(TaskStatus.FAILED, "Agent failed to generate a reflection.")
                return
            
            try:
                reflection = json.loads(raw_reflection_response.strip().replace("```json", "").replace("```", ""))
                critique = reflection.get('critique', 'No critique provided.')
                is_complete = reflection.get('is_complete', False)
                print(f"Agent's Self-Critique: {critique}")
                
                if is_complete:
                    print("\nAgent has concluded the task is complete.")
                    task.set_status(TaskStatus.COMPLETED, f"Agent self-assessed as complete after {iteration_count} iteration(s).")
                else:
                    print("\nAgent has concluded the task is INCOMPLETE. Preparing for next iteration.")
                    previous_attempts.append({
                        "plan": plan,
                        "execution_results": execution_results,
                        "critique": reflection
                    })

            except json.JSONDecodeError:
                task.set_status(TaskStatus.FAILED, f"Agent returned invalid JSON for its reflection. Raw response: {raw_reflection_response}")
                return

        if not is_complete:
            print(f"\nAgent failed to complete the task after {max_iterations} iterations.")
            task.set_status(TaskStatus.FAILED, f"Agent failed to complete task after {max_iterations} iterations.")