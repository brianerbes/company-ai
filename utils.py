# utils.py

"""
A utility module for helper functions that can be used across the project.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv


def configure_genai():
    """
    Loads the Gemini API key from the .env file and configures the
    Google Generative AI client.

    This function should be called once at the start of the application.

    Raises:
        ValueError: If the GEMINI_API_KEY is not found in the .env file.
    """
    # load_dotenv() will search for a .env file and load its variables
    # into the environment for os.getenv() to access.
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "FATAL: GEMINI_API_KEY not found.\n"
            "Please create a .env file in the root directory and add the line:\n"
            "GEMINI_API_KEY='your_api_key_here'"
        )

    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")