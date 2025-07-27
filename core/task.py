# core/task.py

import uuid
from enum import Enum
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "PENDING"
    READY = "READY"  # Kept for future, more advanced scheduling
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED" # A task is waiting on dependencies

class Task:
    def __init__(self, description: str, assignee_id: str, delegator_id: str = "OWNER", dependencies: list[str] = None):
        self.task_id: str = str(uuid.uuid4())
        self.description: str = description

        # State memory for the agent's iterative process
        self.iteration_count: int = 0
        self.previous_attempts: list = []
        self.ui_channel: str | None = None
        self.assignee_id: str = assignee_id
        self.delegator_id: str = delegator_id
        
        # A list of task_ids that must be COMPLETED before this task can run
        self.dependencies: list[str] = dependencies if dependencies is not None else []
        
        self.status: TaskStatus = TaskStatus.PENDING
        # If a task starts with dependencies, it should immediately be blocked.
        if self.dependencies:
            self.status = TaskStatus.BLOCKED

        self.context_pointers: list[str] = []
        
        self.outcome: dict | None = None
        self.history: list[dict] = [{
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.status.value,
            "notes": "Task created."
        }]
        
        self.resource_consumption: dict = {
            "llm_tokens": {"prompt": 0, "completion": 0},
            "tool_calls": 0,
            "execution_time_ms": 0
        }

    def __repr__(self) -> str:
        return f"<Task id='{self.task_id}' status='{self.status.value}' assignee='{self.assignee_id}'>"

    def set_status(self, new_status: TaskStatus, notes: str = ""):
        """Updates the task's status and logs the change to its history."""
        self.status = new_status
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.status.value,
            "notes": notes
        })
        print(f"Task {self.task_id} status changed to: {self.status.value}")