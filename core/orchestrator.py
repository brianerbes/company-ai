from .vfs import FileSystemManager

# --- Tool Implementations ---

def create_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    if not path: return {"status": "error", "message": "Payload must include 'path'."}
    fs.write_file(path, "")
    return {"status": "success", "message": f"File created at '{path}'."}

def write_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    content = payload.get("content")
    if not path or content is None: return {"status": "error", "message": "Payload must include 'path' and 'content'."}
    fs.write_file(path, content, append=False)
    return {"status": "success", "message": f"Content written to '{path}'."}

def read_file(fs: FileSystemManager, payload: dict):
    path = payload.get("path") or payload.get("filepath")
    if not path: return {"status": "error", "message": "Payload must include 'path'."}
    content = fs.read_file(path)
    if content is None: return {"status": "error", "message": f"File not found at '{path}'."}
    return {"status": "success", "content": content}

# --- Tool Registry ---

TOOL_REGISTRY = {
    "CREATE_FILE": create_file,
    "WRITE_FILE": write_file,
    "READ_FILE": read_file,
}

# --- Orchestrator Execution Engine ---

def execute_actions(actions: list, fs: FileSystemManager) -> list:
    """
    Executes a list of actions and returns the results of each execution.
    """
    print("\n--- Orchestrator is executing actions ---")
    execution_results = []
    for i, action in enumerate(actions):
        tool_name = action.get("tool_name")
        payload = action.get("payload", {})
        
        print(f"Action {i+1}: Executing tool '{tool_name}'...")
        
        tool_function = TOOL_REGISTRY.get(tool_name)
        
        if not tool_function:
            result = {"status": "error", "message": f"Tool '{tool_name}' not found in registry."}
            print(f"  -> Result: {result['message']}")
        else:
            try:
                result = tool_function(fs, payload)
                # Omit large content from logs for readability
                log_result = result.copy()
                if 'content' in log_result and len(log_result['content']) > 100:
                    log_result['content'] = log_result['content'][:100] + '... (truncated)'
                print(f"  -> Result: {log_result}")
            except Exception as e:
                result = {"status": "fatal_error", "message": str(e)}
                print(f"  -> FATAL ERROR executing tool '{tool_name}': {e}")
        
        execution_results.append(result)
        # Stop execution if a fatal error occurred
        if result.get("status") == "fatal_error":
            break
            
    print("--- Orchestrator finished ---")
    return execution_results