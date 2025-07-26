# core/task.py

import uuid
from enum import Enum
from datetime import datetime

class TaskStatus(Enum):
    """Defines the possible states of a Task."""
    PENDING = "PENDING"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

class Task:
    """
    Represents a single, self-contained unit of work in the system.

    This object tracks the entire lifecycle of an assignment, including its
    dependencies, status, and history.
    """
    def __init__(self, description: str, assignee_id: str, delegator_id: str = "OWNER"):
        self.task_id: str = str(uuid.uuid4())
        self.description: str = description
        self.assignee_id: str = assignee_id
        self.delegator_id: str = delegator_id
        
        self.status: TaskStatus = TaskStatus.PENDING
        self.dependencies: list[str] = []
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