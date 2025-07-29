from __future__ import annotations

from typing import Any

from .base_tool import BaseTool, ToolResult, ToolStatus


class SendMessageTool(BaseTool):
    """A tool for an agent to send a message to the user or another agent."""

    # --- Tool Contract ---
    name: str = "SEND_MESSAGE"
    description: str = (
        "Sends a message to the user or another agent. "
        "Use this to communicate results, ask for clarification, or provide status updates."
    )
    is_high_risk: bool = False

    def __init__(self, **kwargs: Any) -> None:
        """Initializes the SendMessageTool."""
        super().__init__(**kwargs)

    def execute(self, message: str, **kwargs: Any) -> ToolResult:
        """
        Executes the tool to send a message.

        Args:
            message: The content of the message to be sent.
            **kwargs: Catches any unexpected arguments.

        Returns:
            A ToolResult indicating the outcome of the execution.
        """
        if not isinstance(message, str) or not message:
            return ToolResult(
                status=ToolStatus.FATAL_ERROR,
                error_message="Message must be a non-empty string.",
            )

        try:
            # In this initial version, we just print to the console.
            # Later, this will be replaced with a call to a Pub/Sub client
            # to send the message to the UI or other agents.
            print(f"[MESSAGE TO USER]: {message}")

            return ToolResult(
                status=ToolStatus.SUCCESS,
                payload={"message_sent": message},
            )
        except Exception as e:
            # Catch any unexpected errors during execution.
            return ToolResult(
                status=ToolStatus.FATAL_ERROR,
                error_message=f"An unexpected error occurred: {e}",
            )
