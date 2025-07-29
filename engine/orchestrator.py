from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from tools.base_tool import ToolResult, ToolStatus
from tools.communication_tools import SendMessageTool

if TYPE_CHECKING:
    from .agent import Agent
    from .company import Company
    from .task import Task


# --- Tool Registry ---
# At startup, we instantiate all available tools and register them here.
# This registry maps the tool's `name` to its instance.
# Dependency injection will be used here later to provide tools with necessary managers.
TOOL_REGISTRY = {
    "SEND_MESSAGE": SendMessageTool(),
    # Future tools like "WRITE_FILE" would be registered here.
}


def execute_plan(
    plan: List[Dict[str, Any]], agent: Agent, company: Company, task: Task
) -> List[ToolResult]:
    """
    Securely processes a list of actions from an agent's plan.

    This is the central function for dispatching all tool-based actions. It
    validates permissions and executes the corresponding tool.

    Args:
        plan: A list of dictionaries, where each dict represents a single step (tool call).
        agent: The agent executing the plan.
        company: The company context in which the execution happens.
        task: The parent task for this plan.

    Returns:
        A list of ToolResult objects, one for each step in the plan.
    """
    final_results: List[ToolResult] = []

    for step in plan:
        tool_name = step.get("tool_name")
        payload = step.get("payload", {})

        # --- 1. Tool Lookup ---
        tool_instance = TOOL_REGISTRY.get(tool_name)
        if tool_instance is None:
            error_result = ToolResult(
                status=ToolStatus.FATAL_ERROR,
                error_message=f"Tool '{tool_name}' not found in registry.",
            )
            final_results.append(error_result)
            break  # Stop processing the plan if a tool is not found.

        # --- 2. Security Validation (Placeholder) ---
        # TODO: Implement Layer 2: Check agent.capabilities for `tool_name`.
        # TODO: Implement Layer 2: Validate payload against capability constraints.
        # TODO: Implement Layer 4: Check tool_instance.is_high_risk and trigger approval flow.

        # --- 3. Dispatch & Execute ---
        try:
            # Use dictionary unpacking to pass payload as keyword arguments
            result = tool_instance.execute(**payload)
            final_results.append(result)
        except Exception as e:
            # Catch unexpected crashes within the tool's execute method.
            error_result = ToolResult(
                status=ToolStatus.FATAL_ERROR,
                error_message=f"Tool '{tool_name}' crashed with an unexpected error: {e}",
            )
            final_results.append(error_result)
            # Stop the plan if a tool crashes.
            break

        # --- 4. Process Results ---
        # If the action failed, stop processing the rest of the plan.
        if result.status is not ToolStatus.SUCCESS:
            break

    return final_results
