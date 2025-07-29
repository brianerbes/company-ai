from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import UUID

from .task import Task, TaskStatus

if TYPE_CHECKING:
    from .company import Company


@dataclass
class Agent:
    """
    Represents a single agent (human or AI) at runtime.
    This initial version is focused on loading and the cognitive entry point.
    """

    # Core Attributes
    id: UUID
    role: str
    traits: List[str]
    capabilities: Dict[str, Any]
    system_prompt: str = field(init=False)
    company: "Company" = field(repr=False)

    # Private Attributes
    _raw_system_prompt: str = field(repr=False)

    def __post_init__(self):
        if self._raw_system_prompt.startswith("file://"):
            prompt_path = self._raw_system_prompt.replace("file://", "")
            full_path = self.company.path / prompt_path
            try:
                with open(full_path, "r") as file:
                    self.system_prompt = file.read()
            except FileNotFoundError as exc:
                raise FileNotFoundError(
                    f"System prompt file not found at: {full_path}"
                ) from exc
        else:
            self.system_prompt = self._raw_system_prompt

    def process_task(self, task: Task) -> None:
        print(f"Agent {self.id} starting task: {task.description}")
        task.status = TaskStatus.IN_PROGRESS
        # Assuming all tasks are simple_chat for now
        self._handle_simple_chat(task)
        print(f"Agent {self.id} finished task: {task.description}")

    def _handle_simple_chat(self, task: Task) -> None:
        print(f"Handling simple chat for task: {task.description}")
        task.status = TaskStatus.COMPLETED

    def _handle_complex_task(self, task: Task) -> None:
        pass
