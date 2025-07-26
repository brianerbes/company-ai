# core/orchestrator.py

from .vfs import FileSystemManager

# --- Tool Implementations ---
# Each tool is a function that takes the company's VFS and a payload.
# This ensures all actions are sandboxed.

def create_file(fs: FileSystemManager, payload: dict):
    """Tool to create an empty file."""
    path = payload.get("path") or payload.get("filepath")
    if not path:
        return {"status": "error", "message": "Payload must include 'path'."}
    
    # Writing an empty string creates the file.
    fs.write_file(path, "")
    return {"status": "success", "message": f"File created at '{path}'."}

def write_file(fs: FileSystemManager, payload: dict):
    """Tool to write content to a file."""
    path = payload.get("path") or payload.get("filepath")
    content = payload.get("content")
    if not path or content is None:
        return {"status": "error", "message": "Payload must include 'path' and 'content'."}
    
    fs.write_file(path, content, append=False)
    return {"status": "success", "message": f"Content written to '{path}'."}

def read_file(fs: FileSystemManager, payload: dict):
    """Tool to read the content of a file."""
    path = payload.get("path") or payload.get("filepath")
    if not path:
        return {"status": "error", "message": "Payload must include 'path'."}
        
    content = fs.read_file(path)
    if content is None:
        return {"status": "error", "message": f"File not found at '{path}'."}
    return {"status": "success", "content": content}

# --- Tool Registry ---
# This dictionary maps the tool names (as strings) to their functions.
# The Orchestrator uses this to find the correct tool to execute.

TOOL_REGISTRY = {
    "CREATE_FILE": create_file,
    "WRITE_FILE": write_file,
    "READ_FILE": read_file,
}

# --- Orchestrator Execution Engine ---

def execute_actions(actions: list, fs: FileSystemManager):
    """
    Iterates through a list of actions and executes them using the tool registry.

    Args:
        actions: The list of action objects from the agent's plan.
        fs: The sandboxed FileSystemManager for the current company.
    """
    print("\n--- Orchestrator is executing actions ---")
    for i, action in enumerate(actions):
        tool_name = action.get("tool_name")
        payload = action.get("payload", {})
        
        print(f"Action {i+1}: Executing tool '{tool_name}'...")
        
        tool_function = TOOL_REGISTRY.get(tool_name)
        
        if not tool_function:
            print(f"  -> ERROR: Tool '{tool_name}' not found in registry. Skipping.")
            continue
            
        try:
            result = tool_function(fs, payload)
            print(f"  -> Result: {result.get('message') or result.get('status')}")
            # In the future, we would handle errors and potentially stop execution.
        except Exception as e:
            print(f"  -> FATAL ERROR executing tool '{tool_name}': {e}")
            # Stop execution on fatal error
            break
    print("--- Orchestrator finished ---")