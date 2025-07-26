from typing import TYPE_CHECKING
from .vfs import FileSystemManager

# This import now only runs for type-checking, not at runtime, breaking the cycle.
if TYPE_CHECKING:
    from .company import Company 

# --- Tool Implementations ---

def create_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    if not path: return {"status": "error", "message": "Payload must include 'path'."}
    fs.write_file(path, "")
    return {"status": "success", "message": f"File created at '{path}'."}

def write_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    content = payload.get("content")
    should_append = payload.get("append", False)
    if not path or content is None: return {"status": "error", "message": "Payload must include 'path' and 'content'."}
    fs.write_file(path, content, append=should_append)
    if should_append: return {"status": "success", "message": f"Content appended to '{path}'."}
    else: return {"status": "success", "message": f"Content written to '{path}'."}

def read_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    if not path: return {"status": "error", "message": "Payload must include 'path'."}
    content = fs.read_file(path)
    if content is None: return {"status": "error", "message": f"File not found at '{path}'."}
    return {"status": "success", "content": content}

# Note the forward reference string "Company" in the type hint
def delegate_task(company: "Company", payload: dict):
    """Tool to delegate a new task to another agent."""
    assignee_id = payload.get("assignee_id")
    description = payload.get("description")

    if not assignee_id or not description:
        return {"status": "error", "message": "Payload must include 'assignee_id' and 'description'."}
    
    try:
        new_task = company.create_task(description=description, assignee_id=assignee_id)
        return {"status": "success", "message": f"Task '{new_task.task_id}' delegated to '{assignee_id}'."}
    except ValueError as e:
        return {"status": "error", "message": str(e)}

# --- Tool Registry ---
TOOL_REGISTRY = {
    "CREATE_FILE": create_file,
    "WRITE_FILE": write_file,
    "READ_FILE": read_file,
    "DELEGATE_TASK": delegate_task,
}

# --- Orchestrator Execution Engine ---
def execute_actions(actions: list, company: "Company"):
    """Executes actions, now passing the company instance to tools."""
    print("\n--- Orchestrator is executing actions ---")
    execution_results = []
    for i, action in enumerate(actions):
        tool_name = action.get("tool_name")
        payload = action.get("payload", {})
        
        print(f"Action {i+1}: Executing tool '{tool_name}'...")
        tool_function = TOOL_REGISTRY.get(tool_name)
        
        if not tool_function:
            result = {"status": "error", "message": f"Tool '{tool_name}' not found in registry."}
        else:
            try:
                if tool_name == "DELEGATE_TASK":
                    result = tool_function(company, payload)
                else:
                    result = tool_function(company.fs, payload)
            except Exception as e:
                result = {"status": "fatal_error", "message": str(e)}

        log_result = result.copy()
        if 'content' in log_result and len(log_result.get('content', '')) > 100:
            log_result['content'] = log_result['content'][:100] + '... (truncated)'
        print(f"  -> Result: {log_result}")
        execution_results.append(result)
        if result.get("status") == "fatal_error": break
            
    print("--- Orchestrator finished ---")
    return execution_results