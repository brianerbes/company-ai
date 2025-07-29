from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseLLMAdapter(ABC):
    """
    The abstract contract for all Large Language Model (LLM) adapters.

    This class ensures that the application can interact with different LLM providers
    (like Google Gemini, Anthropic Claude, etc.) through a consistent, unified interface,
    making the core engine model-agnostic.
    """

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generates a simple, unstructured text response from a prompt.

        Args:
            prompt: The input text prompt for the model.
            **kwargs: Provider-specific options (e.g., temperature, max_tokens).

        Returns:
            The generated text as a string.
        """
        pass

    @abstractmethod
    def generate_structured_json(
        self, prompt: str, json_schema: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generates a structured JSON object that conforms to a specific schema.

        This is used for tasks that require reliable, machine-readable output,
        such as generating plans or tool arguments.

        Args:
            prompt: The input text prompt for the model.
            json_schema: A dictionary representing the desired JSON output schema.
            **kwargs: Provider-specific options.

        Returns:
            The generated JSON object as a dictionary.
        """
        pass

    @abstractmethod
    def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """
        Converts a string of text into a numerical vector embedding.

        This is used by the MemoryManager for semantic search.

        Args:
            text: The text to be embedded.
            **kwargs: Provider-specific options.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass
