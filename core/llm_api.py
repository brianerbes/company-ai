import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() in ('true', '1', 't')

# Configure the real API client only if not in mock mode
if not MOCK_MODE:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- Mock Responses ---
# A library of pre-written responses for different agents and phases.
MOCK_RESPONSES = {
    "cto_plan": {
        "reasoning": "As the CTO, my first step is to delegate the detailed work to my specialized team members. I will assign the API design to the Lead Programmer and the database schema to the Database Architect. My own task will then be blocked until they complete their work.",
        "actions": [
            {
                "tool_name": "DELEGATE_TASK",
                "payload": {
                    "assignee_id": "agent_id_programmer_001",
                    "description": "Design the RESTful API for the Dynamic Task Graph feature. The deliverable is a markdown file named 'api_spec.md' in the 'docs/' directory.",
                    "block_self": True
                }
            },
            {
                "tool_name": "DELEGATE_TASK",
                "payload": {
                    "assignee_id": "agent_id_dba_001",
                    "description": "Design the database schema for the Dynamic Task Graph. The deliverable is a markdown file named 'db_schema.md' in the 'docs/' directory.",
                    "block_self": True
                }
            }
        ]
    },
    "programmer_plan": {
        "reasoning": "My task is to design and document the API. I will create the file and write a detailed specification for all necessary endpoints, including data structures and error codes.",
        "actions": [
            {"tool_name": "CREATE_FILE", "payload": {"path": "docs/api_spec.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/api_spec.md", "content": "# API Specification\n\n## Endpoints\n- POST /tasks\n- GET /tasks/{id}\n"}}
        ]
    },
    "dba_plan": {
        "reasoning": "My task is to design the database schema. I will create a file and write the schema using SQL DDL, including tables for tasks and dependencies.",
        "actions": [
            {"tool_name": "CREATE_FILE", "payload": {"path": "docs/db_schema.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/db_schema.md", "content": "-- Database Schema\n\nCREATE TABLE tasks (...);\n"}}
        ]
    },
    "reflection_complete": {
        "critique": "The execution was flawless and the results perfectly match the plan. The task is fully complete to a professional standard.",
        "is_complete": True
    }
}

def _get_mock_response(prompt: str) -> str:
    """
    Selects an appropriate mock response based on keywords in the prompt.
    This simulates different agents having different thoughts.
    """
    print("  -> MOCK MODE: Generating mock response...")
    prompt = prompt.lower()
    
    # All reflection phases will be successful for now
    if "reflect on your work" in prompt:
        return json.dumps(MOCK_RESPONSES["reflection_complete"])
    
    # Planning phases for different agents
    if "lead programmer" in prompt:
        return json.dumps(MOCK_RESPONSES["programmer_plan"])
    if "database architect" in prompt:
        return json.dumps(MOCK_RESPONSES["dba_plan"])
    if "chief technology officer" in prompt:
        return json.dumps(MOCK_RESPONSES["cto_plan"])

    # Default fallback
    return json.dumps(MOCK_RESPONSES["reflection_complete"])

# --- Main API Function ---
def generate_structured_response(prompt: str) -> str | None:
    """
    Main function to get a response. Switches between real and mock mode.
    """
    if MOCK_MODE:
        return _get_mock_response(prompt)

    # --- Real API Call with Retry Logic ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = 5 * (attempt + 1)
                print(f"  -> WARNING: Rate limit exceeded. Waiting for {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"ERROR: An unhandled error occurred while calling the Gemini API: {e}")
                return None 
    
    print("ERROR: Failed to get a response from Gemini API after multiple retries.")
    return None