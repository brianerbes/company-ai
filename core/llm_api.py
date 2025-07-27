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
        "reasoning": "MOCK: My task is to design and document the API. I will create the file and write a detailed specification for all necessary endpoints. I will not message the user directly.",
        "actions": [
            {"tool_name": "CREATE_FILE", "payload": {"path": "docs/api_spec.md"}},
            {"tool_name": "WRITE_FILE", "payload": {"path": "docs/api_spec.md", "content": "# MOCK API Specification\n\n- POST /tasks\n- GET /tasks/{id}\n"}}
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
            },
            {
                "tool_name": "SEND_MESSAGE_TO_USER",
                "payload": {
                    "text": "My team has completed their assignments and I have assembled the final technical specification. The project is complete."
                }
            },
        ]
    },
    "simple_chat_plan": {
        "reasoning": "MOCK: The user sent a simple message. I will respond with a polite and helpful greeting.",
        "actions": [
            {
                "tool_name": "SEND_MESSAGE_TO_USER",
                "payload": {"text": "Hello! How can I help you today?"}
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

    # --- Reflection Logic (Unchanged) ---
    if "reflect on your work" in prompt_lower:
        if "chief technology officer" in prompt_lower and "delegate_task" in prompt.lower():
             return json.dumps(MOCK_RESPONSES["reflection_incomplete_delegated"])
        return json.dumps(MOCK_RESPONSES["reflection_complete"])

    # Use the unique system prompt text to identify the agent and its task
    if "you are the chief technology officer" in prompt_lower:
        # If the task is the specific delegated one, use the complex plan
        if "oversee the creation" in prompt_lower:
            if "review your previous attempts" in prompt_lower:
                return json.dumps(MOCK_RESPONSES["cto_plan_assemble"])
            else:
                return json.dumps(MOCK_RESPONSES["cto_plan_delegate"])
        else: # Otherwise, use the simple chat plan
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])
            
    elif "you are the lead programmer" in prompt_lower:
        # If the task is the specific delegated one, use the complex plan
        if "design the restful api" in prompt_lower:
            return json.dumps(MOCK_RESPONSES["programmer_plan"])
        else: # Otherwise, use the simple chat plan
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])
        
    elif "you are the database architect" in prompt_lower:
        # If the task is the specific delegated one, use the complex plan
        if "design the database schema" in prompt_lower:
            return json.dumps(MOCK_RESPONSES["dba_plan"])
        else: # Otherwise, use the simple chat plan
            return json.dumps(MOCK_RESPONSES["simple_chat_plan"])

    # Default fallback
    return json.dumps(MOCK_RESPONSES["simple_chat_plan"])

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