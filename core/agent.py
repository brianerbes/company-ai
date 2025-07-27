import json
from pathlib import Path
from typing import TYPE_CHECKING
from .vfs import FileSystemManager
from .task import Task, TaskStatus
from .llm_api import generate_structured_response
from .orchestrator import execute_actions

if TYPE_CHECKING:
    from .company import Company

class Agent:
    def __init__(self, agent_id: str, agent_meta: dict, company: "Company"):
        self.id = agent_id
        self.meta = agent_meta
        self.company = company
        self.chat_history: list[dict] = []
        self.fs = company.fs
        self.role = self.meta.get('role', 'Generic Agent')
        self.system_prompt = self.meta.get('system_prompt', 'You are a helpful assistant.')
    
    def __repr__(self) -> str:
        return f"<Agent id='{self.id}' role='{self.role}'>"

    def print_summary(self):
        print(f"  - Agent ID: {self.id}")
        print(f"    Role: {self.role}")
        
    def _get_tool_manifest(self) -> str:
        tool_descriptions = {
            "CREATE_FILE": "Creates a new, empty file. Payload requires 'path'.",
            "WRITE_FILE": "Writes or appends content. Payload requires 'path' and 'content'. Optional: 'append': true.",
            "READ_FILE": "Reads a file's content. Payload requires 'path'.",
            "LIST_FILES": "Lists files in a directory. Optional payload: 'path'.",
            "DELEGATE_TASK": "Delegates a task to another agent. Payload requires 'assignee_id', 'description'. Optional: 'block_self': true.",
            "MEMORIZE_THIS": "Adds text to long-term memory. Payload requires 'text', and an optional 'metadata' dictionary.",
            "RECALL_CONTEXT": "Searches long-term memory. Payload requires 'query'.",
            "SEND_MESSAGE_TO_USER": "Sends a conversational message back to the user in the chat UI. This should be your final action. Payload requires 'text'."
        }
        available_tools = self.meta.get('capabilities', {}).get('allowed_tools', [])
        manifest = "Your available tools and their required parameters are:\n"
        for tool_name in available_tools:
            description = tool_descriptions.get(tool_name, "No description available.")
            manifest += f"- {tool_name}: {description}\n"
        return manifest

    def _get_team_roster(self) -> str:
        roster = "You can delegate to the following team members (use their agent_id):\n"
        if not self.company.agents or len(self.company.agents) <= 1:
            return "There are no other agents available for delegation.\n"
        for agent_id, agent in self.company.agents.items():
            if agent_id != self.id:
                roster += f"- {agent.id}: {agent.role}\n"
        return roster

    def _construct_initial_prompt(self, task: Task) -> str:
        said_format = """
        {
          "reasoning": "A brief, step-by-step thought process for how you will approach the task. Explain your plan.",
          "actions": [ { "tool_name": "TOOL_NAME", "payload": { "param1": "value1" } } ]
        }
        """
        tool_manifest = self._get_tool_manifest()
        team_roster = self._get_team_roster()
        prompt = f"""
        You are an AI agent. Do not act as a user. Your Identity: {self.system_prompt}
        Your assigned task is: "{task.description}"
        {tool_manifest}
        {team_roster}
        **Planning Strategy:** If you use the DELEGATE_TASK tool with 'block_self' set to true, your plan for this turn should ONLY contain the delegation actions. You can read their work and assemble it in a future turn, after your task has been unblocked by the scheduler.
        Based on all the information above, you must formulate a plan. Your response MUST be a valid JSON object following this exact structure (do NOT output any other text, just the JSON):
        {said_format}
        """
        return prompt

    def _construct_iteration_prompt(self, task: Task, previous_attempts: list) -> str:
        said_format = """
        {
          "reasoning": "A new, improved reasoning for how you will address the critiques from your last attempt.",
          "actions": [ { "tool_name": "TOOL_NAME", "payload": { "param1": "value1" } } ]
        }
        """
        tool_manifest = self._get_tool_manifest()
        team_roster = self._get_team_roster()
        history = ""
        for i, attempt in enumerate(previous_attempts):
            history += f"\n--- Attempt #{i+1} ---\nPlan: {json.dumps(attempt['plan'], indent=2)}\nExecution Results: {json.dumps(attempt['execution_results'], indent=2)}\nSelf-Critique: {attempt['critique']['critique']}\n------------------\n"
        prompt = f"""
        You are an AI agent attempting to complete a task. You have tried before and failed. Use your previous self-critique to formulate a new, improved plan.
        Your Identity: {self.system_prompt}. The original task is: "{task.description}"
        Review your previous attempts: {history}
        Based on your critique, create a new plan.
        {tool_manifest}
        {team_roster}
        **Planning Strategy:** If you use the DELEGATE_TASK tool with 'block_self' set to true, your plan for this turn should ONLY contain the delegation actions. You can read their work and assemble it in a future turn, after your task has been unblocked by the scheduler.
        Your new response MUST be a valid JSON object following this exact structure: {said_format}
        """
        return prompt

    def _construct_reflection_prompt(self, task: Task, plan: dict, execution_results: list) -> str:
        reflection_format = """
        {
          "critique": "Critically evaluate your own work. Did you fully accomplish the original task? Were there any errors or oversights in the execution? Was the result of high quality?",
          "is_complete": true
        }
        """
        prompt = f"""
        You are an AI agent reflecting on a task you just attempted. Your Identity: {self.system_prompt}
        The original task was: "{task.description}"
        This was your plan: {json.dumps(plan, indent=2)}
        These were the results of executing your plan: {json.dumps(execution_results, indent=2)}
        Now, reflect on your work. **CRUCIAL RULE: If your critique identifies ANY missing details, errors, or low-quality output, you MUST set 'is_complete' to false.** Only set 'is_complete' to true if the original task has been fully satisfied to a professional standard.
        Your response MUST be a valid JSON object following this exact structure: {reflection_format}
        """
        return prompt

    def process_task(self, task: Task):
        def ui_message(text, msg_type="info"):
            if self.company.pubsub and task.ui_channel:
                self.company.pubsub.send_all({
                    "text": text,
                    "type": msg_type,
                    "agent": self.role,
                    "channel": task.ui_channel
                })
        
        ui_message(f"Processing Task {task.task_id[:8]}...")
        
        max_iterations = 3
        is_complete = False
        while not is_complete and task.iteration_count < max_iterations:
            task.iteration_count += 1
            print(f"\n{'='*10} Starting Iteration #{task.iteration_count} {'='*10}")

            # === 1. PLAN PHASE ===
            ui_message(f"Starting Iteration #{task.iteration_count}: Planning...")
            task.set_status(TaskStatus.IN_PROGRESS, f"Agent is planning iteration {task.iteration_count}.")
            if task.iteration_count == 1:
                plan_prompt = self._construct_initial_prompt(task)
            else:
                plan_prompt = self._construct_iteration_prompt(task, task.previous_attempts)
            
            raw_plan_response = generate_structured_response(plan_prompt)
            if not raw_plan_response:
                task.set_status(TaskStatus.FAILED, "Agent failed to generate a plan.")
                return

            try:
                plan = json.loads(raw_plan_response.strip().replace("```json", "").replace("```", ""))
                ui_message(f"Plan: {plan.get('reasoning')}", msg_type="agent")
            except json.JSONDecodeError:
                task.set_status(TaskStatus.FAILED, f"Agent returned invalid JSON for its plan. Raw response: {raw_plan_response}")
                return
            
            # === 2. EXECUTE PHASE ===
            actions = plan.get('actions', [])
            execution_results = execute_actions(actions, self.company, task) if actions else []
            
            if task.status == TaskStatus.BLOCKED:
                ui_message(f"Task is now BLOCKED, waiting for dependencies. Ending turn.")
                return

            # === 3. REFLECT PHASE ===
            ui_message("Reflecting on the results...")
            reflection_prompt = self._construct_reflection_prompt(task, plan, execution_results)
            raw_reflection_response = generate_structured_response(reflection_prompt)
            if not raw_reflection_response:
                task.set_status(TaskStatus.FAILED, "Agent failed to generate a reflection.")
                return
            
            try:
                reflection = json.loads(raw_reflection_response.strip().replace("```json", "").replace("```", ""))
                critique = reflection.get('critique', 'No critique provided.')
                is_complete = reflection.get('is_complete', False)
                ui_message(f"Critique: {critique}", msg_type="agent")
                
                if is_complete:
                    task.set_status(TaskStatus.COMPLETED, f"Agent self-assessed as complete after {task.iteration_count} iteration(s).")
                else:
                    ui_message("Task is INCOMPLETE. Preparing for next iteration.")
                    task.previous_attempts.append({
                        "plan": plan, "execution_results": execution_results, "critique": reflection
                    })
            except json.JSONDecodeError:
                task.set_status(TaskStatus.FAILED, f"Agent returned invalid JSON for its reflection. Raw response: {raw_reflection_response}")
                return

        if not is_complete:
            ui_message(f"Failed to complete the task after {max_iterations} iterations.", msg_type="system")
            task.set_status(TaskStatus.FAILED, f"Agent failed to complete task after {max_iterations} iterations.")