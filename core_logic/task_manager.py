# core_logic/task_manager.py

"""
This module contains the TaskManager class, which is responsible for tracking
the lifecycle of all tasks delegated within the system.
"""

from collections import defaultdict

class TaskManager:
    """
    Acts as a central "to-do list" or "Jira board" for the organization.
    It creates and tracks the status of all delegated tasks.
    """
    def __init__(self):
        """
        Initializes the TaskManager.
        """
        self.tasks = {} # A dictionary to store task objects by their ID
        self.task_id_counter = 0
        print("TaskManager initialized.")

    def _generate_task_id(self) -> str:
        """Generates a new, unique task ID."""
        new_id = f"T-{self.task_id_counter}"
        self.task_id_counter += 1
        return new_id

    def create_task(self, description: str, delegator_id: str, assignee_id: str, context: dict = None) -> dict:
        """
        Creates a new task object and adds it to the central tracking dictionary.

        Args:
            description (str): The main instruction for the task.
            delegator_id (str): The ID of the agent assigning the task.
            assignee_id (str): The ID of the agent the task is assigned to.
            context (dict, optional): Contextual information, like relevant files. Defaults to None.

        Returns:
            The newly created task object.
        """
        task_id = self._generate_task_id()
        task_object = {
            "task_id": task_id,
            "description": description,
            "delegator_id": delegator_id,
            "assignee_id": assignee_id,
            "status": "PENDING", # All tasks start as pending
            "context": context or {},
            "subtasks": [],
            "history": [f"Created by {delegator_id} for {assignee_id}"]
        }
        self.tasks[task_id] = task_object
        print(f"[TaskManager] Created Task {task_id}: '{description[:50]}...' for {assignee_id}")
        return task_object

    def update_task_status(self, task_id: str, new_status: str, agent_id: str) -> bool:
        """
        Updates the status of an existing task.

        Args:
            task_id (str): The ID of the task to update.
            new_status (str): The new status (e.g., 'IN_PROGRESS', 'COMPLETED').
            agent_id (str): The agent making the update.

        Returns:
            True if the update was successful, False otherwise.
        """
        if task_id not in self.tasks:
            print(f"[TaskManager] Error: Task {task_id} not found.")
            return False

        # Basic permission check: only the assignee or delegator can update status.
        task = self.tasks[task_id]
        if agent_id not in [task['assignee_id'], task['delegator_id']]:
            print(f"[SECURITY] Agent '{agent_id}' denied status update on task {task_id}.")
            return False

        task['status'] = new_status
        task['history'].append(f"Status updated to {new_status} by {agent_id}")
        print(f"[TaskManager] Updated Task {task_id} status to {new_status}")
        return True

    def get_task(self, task_id: str) -> dict | None:
        """Retrieves a task object by its ID."""
        return self.tasks.get(task_id)

    def get_tasks_for_agent(self, agent_id: str) -> list:
        """Retrieves all tasks assigned to a specific agent."""
        return [task for task in self.tasks.values() if task['assignee_id'] == agent_id]