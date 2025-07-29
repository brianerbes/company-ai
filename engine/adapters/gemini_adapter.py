from __future__ import annotations

import os
from typing import Any, Dict, List

import google.generativeai as genai

from .base_adapter import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    """The concrete adapter for interacting with the Google Gemini API."""

    def __init__(
        self,
        generative_model_name: str = "gemini-1.5-flash-latest",
        embedding_model_name: str = "text-embedding-004",
    ):
        """
        Initializes the Gemini adapter.

        It configures the `genai` library using credentials from the environment.
        The blueprint specifies using GOOGLE_APPLICATION_CREDENTIALS, which the
        library handles automatically when `genai.configure()` is called without
        an api_key.

        Args:
            generative_model_name: The specific Gemini model for text generation.
            embedding_model_name: The specific model for text embeddings.
        """
        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            raise EnvironmentError(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable not set."
            )
        genai.configure()
        self.generative_model = genai.GenerativeModel(generative_model_name)
        self.embedding_model_name = embedding_model_name

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """Generates a simple text response using the Gemini API."""
        try:
            response = self.generative_model.generate_content(prompt, **kwargs)
            return response.text
        except Exception as e:
            # Handle potential API errors gracefully.
            print(f"Error during Gemini API call: {e}")
            return f"Error: Could not generate text due to an API error. Details: {e}"

    def generate_structured_json(
        self, prompt: str, json_schema: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generates a structured JSON object using Gemini's JSON mode.
        """
        # TODO: Implement proper JSON mode generation.
        print(
            "Warning: generate_structured_json is not fully implemented. "
            "Returning a placeholder."
        )
        return {
            "plan": [
                {
                    "tool_name": "SEND_MESSAGE",
                    "payload": {"message": "JSON mode not implemented yet."},
                }
            ]
        }

    def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """
        Generates a numerical vector embedding for a given text.
        """
        try:
            # Use the dedicated embedding API from the genai library.
            result = genai.embed_content(
                model=self.embedding_model_name, content=text, **kwargs
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error during Gemini embedding API call: {e}")
            # Return a zero vector as a fallback to prevent crashes.
            # A more robust system might use a specific error-handling strategy.
            return [0.0] * 768
