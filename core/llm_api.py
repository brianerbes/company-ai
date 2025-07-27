import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() in ('true', '1', 't')

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
    "cto_plan_delegate": {
        "reasoning": "MOCK: As the CTO, my first step is to delegate the detailed work to my specialized team members. I will assign the API design to the Lead Programmer and the database schema to the Database Architect. My own task will then be blocked until they complete their work.",
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
        "reasoning": "MOCK: My task is to design the API. I will create the file, write the spec, and then inform the user that I am done.",
        "actions": [
            {"tool_name": "CREATE_FILE", "payload": {"path": "docs/api_spec.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/api_spec.md", "content": "# MOCK API Specification\n\n- POST /tasks\n- GET /tasks/{id}\n"}},
            {"tool_name": "SEND_MESSAGE_TO_USER", "payload": {"text": "I have completed the draft for the API specification. You can find it at 'docs/api_spec.md'."}}
        ]
    },
    "dba_plan": {
        "reasoning": "MOCK: My task is to design the database schema. I will create a file and write the schema using SQL DDL.",
        "actions": [
            {"tool_name": "CREATE_FILE", "payload": {"path": "docs/db_schema.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/db_schema.md", "content": "-- MOCK Database Schema\n\nCREATE TABLE tasks (...);\n"}}
        ]
    },
    "cto_plan_assemble": {
        "reasoning": "MOCK: My team has completed their work. I will read their files, MEMORIZE the key information, RECALL it to ensure it's in my memory, and then write the final specification.",
        "actions": [
            {
                "tool_name": "MEMORIZE_THIS", 
                "payload": {
                    "text": "The API spec was created by the Lead Programmer.",
                    "metadata": {"source": "CTO's thought"}
                }
            },
            {
                "tool_name": "RECALL_CONTEXT", 
                "payload": {
                    "query": "Who created the API spec?"
                }
            },
            {
                "tool_name": "WRITE_FILE", 
                "payload": {
                    "path": "docs/final_spec.md", 
                    "content": "# MOCK FINAL SPECIFICATION\n\nAssembled by the CTO."
                }
            }
        ]
    },
    "reflection_incomplete_delegated": {
        "critique": "MOCK: I have successfully delegated the sub-tasks for the API and database design. My own work is now blocked pending their completion. The task is therefore not complete.",
        "is_complete": False
    },
    "reflection_complete": {
        "critique": "MOCK: The execution was flawless and the results perfectly match the plan. The task is fully complete.",
        "is_complete": True
    }
}

def _get_mock_response(prompt: str) -> str:
    """
    Selects an appropriate mock response based on more specific keywords in the prompt.
    """
    print("  -> MOCK MODE: Generating mock response...")
    prompt_lower = prompt.lower()
    
    # Use the unique system prompt text to identify the agent and its task
    if "you are the chief technology officer" in prompt_lower:
        if "reflect on your work" in prompt_lower:
            # If the CTO just delegated, the critique should say it's incomplete
            if any("delegate_task" in str(action).lower() for action in prompt.split("actions")[1]):
                return json.dumps(MOCK_RESPONSES["reflection_incomplete_delegated"])
            else: # Otherwise, the final assembly is complete
                 return json.dumps(MOCK_RESPONSES["reflection_complete"])

        if "review your previous attempts" in prompt_lower:
            return json.dumps(MOCK_RESPONSES["cto_plan_assemble"])
        else:
            return json.dumps(MOCK_RESPONSES["cto_plan_delegate"])
            
    # For other agents, the reflection is always complete for now
    elif "reflect on your work" in prompt_lower:
        return json.dumps(MOCK_RESPONSES["reflection_complete"])
        
    elif "you are the lead programmer" in prompt_lower:
        return json.dumps(MOCK_RESPONSES["programmer_plan"])
        
    elif "you are the database architect" in prompt_lower:
        return json.dumps(MOCK_RESPONSES["dba_plan"])

    # Default fallback if no specific prompt is matched
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