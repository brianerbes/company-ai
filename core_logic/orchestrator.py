# core_logic/orchestrator.py

import google.generativeai as genai
from collections import defaultdict

from config.hierarchy import HIERARCHY
from core_logic.agent import Agent
from core_logic.file_system_manager import FileSystemManager
from core_logic.task_manager import TaskManager
from core_logic.audit_log import AuditLogger
from utils import configure_genai

MAX_INTERNAL_TURNS = 15

class Orchestrator:
    """
    The central OS of the Company-IA. It manages agents, communication flow,
    and all system protocols.
    """
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        print("Initializing Orchestrator...")
        configure_genai()
        self.model = genai.GenerativeModel(model_name)
        
        self.file_system = FileSystemManager(base_path="virtual_fs")
        self.task_manager = TaskManager()
        self.audit_log = AuditLogger()
        
        self.hierarchy = HIERARCHY
        self.agents = {}
        self.human_agents = []
        
        for agent_id, details in self.hierarchy.items():
            if details['type'] == 'ai':
                self.agents[agent_id] = Agent(agent_id, self)
            elif details['type'] == 'human':
                self.human_agents.append(agent_id)
        
        self.agent_inboxes = defaultdict(list)
        print("Orchestrator initialized successfully.")

    def get_parent(self, agent_id: str) -> str | None:
        return self.hierarchy.get(agent_id, {}).get('parent')

    def direct_llm_query(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def query_llm_for_agent(self, agent_id: str, prompt: str) -> str:
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Attempted to query LLM for non-AI agent: {agent_id}")

        full_prompt = f"{agent.role_prompt}\n\n--- TASK ---\n{prompt}"
        response = self.model.generate_content(full_prompt)
        return response.text

    def _process_agent_response(self, agent_id: str, response_message: dict):
        """
        Processes the response from an AI agent, executing the requested intent.
        """
        intent = response_message.get("intent")
        payload = response_message.get("payload", {})
        task_id = response_message.get("task_id")
        
        print(f"[Orchestrator] Processing response from '{agent_id}' with intent '{intent}'.")

        if intent == "PROVIDE_INFORMATION":
            # For now, we assume information is for the delegator of the task
            task = self.task_manager.get_task(task_id)
            if task and task['delegator_id']:
                # In a real system, we'd queue a new message. For the UI, we just return it.
                return {"status": "completed", "message": payload.get("details", "Task completed.")}
        
        elif intent == "CREATE_FILE":
            filename = payload.get("filename")
            if filename:
                self.file_system.create_file(filename, agent_id)
        
        elif intent == "WRITE_FILE":
            filename = payload.get("filename")
            content = payload.get("content")
            if filename and content is not None:
                self.file_system.write_file(filename, content, agent_id)

        elif intent == "REQUEST_INFORMATION":
            # This would trigger the escalation protocol
            # For now, we will surface this to the user
            question = payload.get("QUESTION", "An unspecified question.")
            return {"status": "needs_clarification", "message": f"Agent '{agent_id}' has a question: {question}"}

        # More intents (SET_PERMISSIONS, DELEGATE_SUBTASKS, etc.) would be handled here.

        return {"status": "in_progress", "message": f"Agent '{agent_id}' completed an action with intent '{intent}'."}


    def start_task(self, agent_id: str, task_prompt: str, user_as="Owner") -> dict:
        """
        Main entry point for the user to assign a task.
        """
        if agent_id not in self.hierarchy:
            return {"status": "error", "message": f"Agent '{agent_id}' not found."}

        task_object = self.task_manager.create_task(
            description=task_prompt,
            delegator_id=user_as,
            assignee_id=agent_id
        )

        initial_message = {
            "task_id": task_object['task_id'],
            "intent": "ASSIGN_TASK",
            "payload": {"description": task_prompt}
        }
        
        # If the agent is human, just queue the task and return
        if self.hierarchy[agent_id]['type'] == 'human':
            self.agent_inboxes[agent_id].append(initial_message)
            return {"status": "pending", "message": f"Task {task_object['task_id']} assigned to human agent '{agent_id}'. It's in their inbox."}

        # If the agent is an AI, execute the task synchronously for a chatbot-like feel
        if self.hierarchy[agent_id]['type'] == 'ai':
            agent = self.agents[agent_id]
            response_message = agent.execute_task(initial_message)
            
            # Process the agent's response to execute its desired action
            final_result = self._process_agent_response(agent_id, response_message)
            return final_result