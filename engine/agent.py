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

        # --- Cognitive Path Selection ---
        # Use the company's router to classify the task's intent.
        intent = self.company.router.classify(task.description, self)
        print(f"Router classified intent as: '{intent}'")

        if intent == "simple_chat":
            self._handle_simple_chat(task)
        else:
            # For now, other intents will be handled as complex tasks.
            self._handle_complex_task(task)

        print(f"Agent {self.id} finished task: {task.description}")

    def _handle_simple_chat(self, task: Task) -> None:
        """
        Handles simple conversational interactions by calling the LLM
        and then executing a plan to send the response.
        """
        print(f"Handling simple chat for task: {task.description}")

        # --- 1. Generate Response using LLM ---
        prompt = f"{self.system_prompt}\n\nUser command: {task.description}"
        llm_response = self.company.llm_adapter.generate_text(prompt)

        # --- 2. Plan Generation ---
        plan = [
            {
                "tool_name": "SEND_MESSAGE",
                "payload": {"message": llm_response},
            }
        ]

        # --- 3. Plan Execution ---
        results = orchestrator.execute_plan(
            plan=plan, agent=self, company=self.company, task=task
        )

        # --- 4. Process Results ---
        if results and results[-1].status == ToolExecutionStatus.SUCCESS:
            task.status = TaskStatus.COMPLETED
        else:
            task.status = TaskStatus.FAILED

    def _handle_complex_task(self, task: Task) -> None:
        """
        Placeholder for the deep reasoning cognitive cycle.
        For now, it sends a message indicating the feature is not implemented.
        """
        print(f"Handling complex task for task: {task.description}")
        plan = [
            {
                "tool_name": "SEND_MESSAGE",
                "payload": {
                    "message": "I understand this is a complex task, but that "
                    "cognitive path is still under development."
                },
            }
        ]
        orchestrator.execute_plan(
            plan=plan, agent=self, company=self.company, task=task
        )
        task.status = TaskStatus.COMPLETED
