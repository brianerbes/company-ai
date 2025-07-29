from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Agent


class Router:
    """
    Analyzes requests to determine their fundamental intent.

    This class is the "receptionist" of the system. It examines an incoming
    request and classifies it, allowing the receiving agent to decide which
    cognitive path to use (e.g., simple chat vs. complex planning).
    """

    def classify(self, text: str, target_agent: Agent) -> str:
        """
        Processes text through a multi-stage pipeline to determine its intent.

        For this initial implementation, the logic is very simple: we will
        always classify the intent as "simple_chat".

        In the future, this will evolve into the multi-stage pipeline described
        in the blueprint (rule-based, heuristic, and LLM fallback).

        Args:
            text: The input text from the user or another agent.
            target_agent: The agent who is the target of the request.

        Returns:
            A string representing the classified intent (e.g., "simple_chat").
        """
        # TODO: Implement Stage 1: Rule-based fast path (regex, keywords).
        # TODO: Implement Stage 2: Tool-based heuristics.
        # TODO: Implement Stage 3: LLM Classifier Fallback.

        return "simple_chat"
