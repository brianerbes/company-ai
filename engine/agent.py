from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import UUID

from tools.base_tool import ToolStatus as ToolExecutionStatus

from . import orchestrator
from .task import Task, TaskStatus

if TYPE_CHECKING:
    from .company import Company


@dataclass
class Agent:
    """
    Represents a single agent (human or AI) at runtime.
    This initial version is focused on loading and the cognitive entry point.
    """

    # --- Core Attributes ---
    id: UUID
    role: str
    traits: List[str]
    capabilities: Dict[str, Any]
    system_prompt: str = field(init=False)
    company: "Company" = field(repr=False)

    # --- Private Attributes ---
    _raw_system_prompt: str = field(repr=False)

    def __post_init__(self):
        """Initializes derived fields like the system prompt from a file or string."""
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
        """
        The entry point for the agent's turn. It reads the task's
        intent and selects the appropriate cognitive process to handle it.
        """
        print(f"Agent {self.id} starting task: {task.description}")
        task.status = TaskStatus.IN_PROGRESS

        # For now, assume all tasks are "simple_chat".
        # TODO: Add routing logic based on task.intent.
        self._handle_simple_chat(task)

        print(f"Agent {self.id} finished task: {task.description}")

    def _handle_simple_chat(self, task: Task) -> None:
        """
        Handles simple conversational interactions by creating and executing a plan.
        """
        print(f"Handling simple chat for task: {task.description}")

        # --- 1. Plan Generation (Simplified) ---
        # In this simple case, the plan is just to send a message back.
        # Later, an LLM call will generate this plan.
        # For now, we'll echo the task description.
        plan = [
            {
                "tool_name": "SEND_MESSAGE",
                "payload": {"message": f"Echoing your request: {task.description}"},
            }
        ]

        # --- 2. Plan Execution ---
        # The agent dispatches the plan to the orchestrator.
        results = orchestrator.execute_plan(
            plan=plan, agent=self, company=self.company, task=task
        )

        # --- 3. Process Results ---
        # Check if the plan execution was successful.
        if results and results[-1].status == ToolExecutionStatus.SUCCESS:
            task.status = TaskStatus.COMPLETED
        else:
            task.status = TaskStatus.FAILED
            # TODO: Add more sophisticated error handling or retry logic.

    def _handle_complex_task(self, task: Task) -> None:
        """Placeholder for the deep reasoning cognitive cycle."""
        pass
