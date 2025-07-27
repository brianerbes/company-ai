import os
import time
import json
from collections import deque
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() in ('true', '1', 't')

# --- NEW: API Rate Limiter ---
class APIRateLimiter:
    """A simple client-side rate limiter to stay within API quotas."""
    def __init__(self, max_requests: int, per_seconds: int):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.request_timestamps = deque()

    def wait_if_needed(self):
        """Checks recent requests and waits if the rate limit is exceeded."""
        now = time.monotonic()
        
        while self.request_timestamps and self.request_timestamps[0] <= now - self.per_seconds:
            self.request_timestamps.popleft()
            
        if len(self.request_timestamps) >= self.max_requests:
            oldest_request_time = self.request_timestamps[0]
            time_to_wait = oldest_request_time - (now - self.per_seconds)
            
            if time_to_wait > 0:
                print(f"--- Rate Limiter: Pausing for {time_to_wait:.2f} seconds to stay within quota. ---")
                time.sleep(time_to_wait)
        
        self.request_timestamps.append(time.monotonic())

# --- Initialize the Limiter ---
rate_limiter = APIRateLimiter(max_requests=10, per_seconds=60)

print(f"--- MOCK MODE status: {MOCK_MODE} ---")

if not MOCK_MODE:
    print("--- Configuring REAL Gemini API client ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("--- Mock mode is active. Real API will not be used. ---")


# --- Mock Responses ---
MOCK_RESPONSES = {
    "simple_chat_plan": {
        "reasoning": "MOCK: The user sent a simple message. I will respond with a polite and helpful greeting.",
        "actions": [{"tool_name": "SEND_MESSAGE_TO_USER", "payload": {"text": "Hello! How can I help you today?"}}]
    },
    "cto_plan_delegate": {
        "reasoning": "MOCK: The user wants me to oversee a project. I will delegate the work to my team and block myself until they are done.",
        "actions": [
            {"tool_name": "DELEGATE_TASK", "payload": {"assignee_id": "agent_id_programmer_001", "description": "Please design the RESTful API for the new feature.", "block_self": True}},
            {"tool_name": "DELEGATE_TASK", "payload": {"assignee_id": "agent_id_dba_001", "description": "Please design the database schema for the new feature.", "block_self": True}}
        ]
    },
    "programmer_plan": {
        "reasoning": "MOCK: My task is to design the API. I will create the file and write the spec.",
        "actions": [{"tool_name": "WRITE_FILE", "payload": {"path": "docs/api_spec.md", "content": "# MOCK API Specification\n..."}}]
    },
    "dba_plan": {
        "reasoning": "MOCK: My task is to design the database schema. I will create a file and write the schema.",
        "actions": [{"tool_name": "WRITE_FILE", "payload": {"path": "docs/db_schema.md", "content": "-- MOCK Database Schema\n..."}}]
    },
    "cto_plan_assemble": {
        "reasoning": "MOCK: My team has completed their work. I will read their files and assemble the final spec, then inform the user.",
        "actions": [
            {"tool_name": "READ_FILE", "payload": {"path": "docs/api_spec.md"}},
            {"tool_name": "READ_FILE", "payload": {"path": "docs/db_schema.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/final_spec.md", "content": "# MOCK FINAL SPECIFICATION"}},
            {"tool_name": "SEND_MESSAGE_TO_USER", "payload": {"text": "My team has completed their assignments and I have assembled the final technical specification."}}
        ]
    },
    "reflection_incomplete": {
        "critique": "MOCK: I have successfully delegated the sub-tasks. My own work is now pending their completion.",
        "is_complete": False
    },
    "reflection_complete": {
        "critique": "MOCK: The execution was flawless and the results perfectly match the plan.",
        "is_complete": True
    }
}

def _get_mock_response(prompt: str) -> str:
    """Selects an appropriate mock response based on the agent and task."""
    print("  -> MOCK MODE: Generating mock response...")
    prompt_lower = prompt.lower()

    if "reflect on your work" in prompt_lower:
        if "chief technology officer" in prompt_lower and "delegate_task" in prompt.lower():
             return json.dumps(MOCK_RESPONSES["reflection_incomplete"])
        return json.dumps(MOCK_RESPONSES["reflection_complete"])

    task_description = ""
    if "your assigned task is:" in prompt_lower:
        task_description = prompt_lower.split("your assigned task is:")[1].split("your available tools are:")[0]
    elif "the original task is:" in prompt_lower:
        task_description = prompt_lower.split("the original task is:")[1].split("review your previous attempts:")[0]

    if "you are the chief technology officer" in prompt_lower:
        if "oversee" in task_description or "specification" in task_description:
            if "review your previous attempts" in prompt_lower:
                return json.dumps(MOCK_RESPONSES["cto_plan_assemble"])
            else:
                return json.dumps(MOCK_RESPONSES["cto_plan_delegate"])
        else:
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])
            
    elif "you are the lead programmer" in prompt_lower:
        if "design the restful api" in task_description:
            return json.dumps(MOCK_RESPONSES["programmer_plan"])
        else:
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])
        
    elif "you are the database architect" in prompt_lower:
        if "design the database schema" in task_description:
            return json.dumps(MOCK_RESPONSES["dba_plan"])
        else:
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])

    return json.dumps(MOCK_RESPONSES["simple_chat_plan"])

def generate_structured_response(prompt: str) -> str | None:
    """
    Main function to get a response. Switches between real and mock mode,
    and now includes both client-side rate limiting and server-side error retries.
    """
    if MOCK_MODE:
        return _get_mock_response(prompt)

    rate_limiter.wait_if_needed()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print("--- Calling Gemini API... ---")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = 5 * (attempt + 1)
                print(f"  -> WARNING: Server responded with 429 Rate Limit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"ERROR: An unhandled error occurred while calling the Gemini API: {e}")
                return None 
    
    print("ERROR: Failed to get a response from Gemini API after multiple retries.")
    return None