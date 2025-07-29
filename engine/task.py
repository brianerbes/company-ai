from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID, uuid4


class InteractionType(Enum):
    """Defines the complete vocabulary of communication acts available in the system."""

    TASK_DELEGATION = "TASK_DELEGATION"
    TASK_COLLABORATION_REQUEST = "TASK_COLLABORATION_REQUEST"
    STATUS_UPDATE = "STATUS_UPDATE"
    QUERY_FOR_INFO = "QUERY_FOR_INFO"
    ESCALATION_FOR_APPROVAL = "ESCALATION_FOR_APPROVAL"


class TaskStatus(Enum):
    """Defines the complete lifecycle of a task from creation to completion."""

    AWAITING_ACCEPTANCE = "AWAITING_ACCEPTANCE"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class TaskEvent:
    """Represents a single, immutable event in a Task's history for a structured audit trail."""

    event_type: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: UUID = field(default_factory=uuid4)


@dataclass
class Interaction:
    """The foundational data structure for any communication event between agents."""

    # Non-default fields must come first.
    type: InteractionType
    source_agent_id: UUID
    target_agent_id: UUID
    payload: Dict[str, Any]

    # Fields with default values follow.
    interaction_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Task(Interaction):
    """A specialized Interaction that represents a formal unit of work to be done."""

    # This field is derived from the payload, so it's not part of the constructor.
    description: str = field(init=False)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 100
    dependencies: List[UUID] = field(default_factory=list)
    parent_task_id: UUID | None = None
    history: List[TaskEvent] = field(default_factory=list)
    iteration_count: int = 0
    previous_attempts: List[Dict[str, Any]] = field(default_factory=list)
    ui_channel: str | None = None

    def __post_init__(self) -> None:
        """Initializes derived fields and records the creation event."""
        self.description = self.payload.get("description", "No description provided.")
        creation_event = TaskEvent(
            event_type="TASK_CREATED", details={"description": self.description}
        )
        self.history.append(creation_event)

    def add_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Adds a new event to the task's history and updates status if necessary."""
        event = TaskEvent(event_type=event_type, details=details)
        self.history.append(event)
        if event_type == "STATUS_CHANGE":
            # This logic assumes the new status is passed in the details dict.
            # A more robust implementation might validate the type of the new status.
            new_status = details.get("status")
            if isinstance(new_status, TaskStatus):
                self.status = new_status
