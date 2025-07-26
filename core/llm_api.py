import os
import time
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
    Sends a prompt to the Gemini model with a retry mechanism for rate limiting.

    Args:
        prompt: The complete prompt to send to the model.

    Returns:
        The text content of the model's response, or None if an error occurs.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Check if the exception is a rate limit error (often a 429 status)
            if "429" in str(e):
                print(f"  -> WARNING: Rate limit exceeded. Waiting for a moment... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(5 * (attempt + 1)) # Exponential backoff: 5s, 10s, 15s
                continue # Retry the loop
            else:
                print(f"ERROR: An unhandled error occurred while calling the Gemini API: {e}")
                return None # For other errors, fail immediately
    
    print("ERROR: Failed to get a response from Gemini API after multiple retries.")
    return None