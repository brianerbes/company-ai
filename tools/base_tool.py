from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ToolStatus(Enum):
    """Enumeration for the possible outcomes of a tool's execution."""

    SUCCESS = "SUCCESS"
    FATAL_ERROR = "FATAL_ERROR"  # The action failed and should not be retried.
    RETRYABLE_ERROR = (
        "RETRYABLE_ERROR"  # The action failed but might succeed on a retry.
    )


@dataclass(frozen=True)
class ToolResult:
    """A structured object to represent the outcome of a tool's execution."""

    status: ToolStatus
    payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BaseTool(ABC):
    """
    The abstract contract that all tool classes MUST implement.
    It standardizes how tools are defined, configured, and executed.
    """

    # These must be defined by any concrete tool subclass.
    name: str
    description: str
    is_high_risk: bool = False

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        """
        A generic constructor to accept injected dependencies (e.g., managers).
        """
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """
        The core logic of the tool lives here.
        It receives specific arguments for its operation.
        It MUST return a ToolResult object.
        """
        pass
