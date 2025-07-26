import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_structured_response(prompt: str) -> str | None:
    """
    Sends a prompt to the Gemini model and gets a response.

    Args:
        prompt: The complete prompt to send to the model.

    Returns:
        The text content of the model's response, or None if an error occurs.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"ERROR: An error occurred while calling the Gemini API: {e}")
        return None