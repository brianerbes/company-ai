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

    # --- Reflection Logic ---
    if "reflect on your work" in prompt_lower:
        if "chief technology officer" in prompt_lower and "delegate_task" in prompt.lower():
             return json.dumps(MOCK_RESPONSES["reflection_incomplete"])
        return json.dumps(MOCK_RESPONSES["reflection_complete"])

    # --- Planning Logic ---
    # This parser now understands both the initial prompt and the iteration prompt
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

# --- Main API Function ---
def generate_structured_response(prompt: str) -> str | None:
    if MOCK_MODE:
        return _get_mock_response(prompt)
    
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