# core_logic/file_system_manager.py

"""
Manages all interactions with the virtual file system for the agents.

This module is a critical security layer. It ensures that agents can only
operate within their designated directory ('virtual_fs/') and only according
to the permissions explicitly granted to them.
"""

import os
import json

class FileSystemManager:
    """
    Handles file creation, reading, writing, and permission management within
    a sandboxed directory.
    """
    def __init__(self, base_path: str = "virtual_fs"):
        """
        Initializes the FileSystemManager.

        Args:
            base_path (str): The root directory for the virtual file system.
        """
        self.base_path = os.path.abspath(base_path)
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
        print(f"FileSystemManager initialized. Sandboxed to: {self.base_path}")

    def _get_safe_path(self, filename: str) -> str | None:
        """
        Validates and resolves a filename to a safe, absolute path within the sandbox.

        This is a crucial security function to prevent directory traversal attacks.
        An agent should NOT be able to provide a filename like '../../secret_file'.

        Args:
            filename (str): The requested filename from an agent.

        Returns:
            The absolute, safe path if valid, otherwise None.
        """
        # Normalize the path to resolve any '..' components.
        # e.g., 'folder/../file.txt' becomes 'file.txt'
        base_path = os.path.realpath(self.base_path)
        requested_path = os.path.realpath(os.path.join(base_path, filename))

        # Check if the resolved path is still within our sandboxed base_path.
        if os.path.commonprefix([requested_path, base_path]) != base_path:
            print(f"[SECURITY] Denied access to unsafe path: {filename}")
            return None
        
        return requested_path

    def _get_metadata_path(self, safe_path: str) -> str:
        """Generates the path for a file's corresponding metadata file."""
        return f"{safe_path}.meta.json"

    def _read_metadata(self, safe_path: str) -> dict:
        """Reads a file's metadata, returning a default if it doesn't exist."""
        meta_path = self._get_metadata_path(safe_path)
        if not os.path.exists(meta_path):
            return {"owner": None, "permissions": {}}
        with open(meta_path, 'r') as f:
            return json.load(f)

    def _write_metadata(self, safe_path: str, metadata: dict):
        """Writes metadata to a file."""
        meta_path = self._get_metadata_path(safe_path)
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def check_permission(self, filename: str, agent_id: str, permission: str) -> bool:
        """
        Checks if an agent has a specific permission for a file.

        Args:
            filename (str): The name of the file to check.
            agent_id (str): The ID of the agent requesting access.
            permission (str): The permission to check ('read', 'write', 'execute').

        Returns:
            True if the agent has permission, False otherwise.
        """
        safe_path = self._get_safe_path(filename)
        if not safe_path:
            return False
        
        metadata = self._read_metadata(safe_path)
        
        # The owner always has all permissions.
        if metadata.get("owner") == agent_id:
            return True
            
        # Check specific permissions for other agents.
        agent_perms = metadata.get("permissions", {}).get(agent_id, {})
        return agent_perms.get(permission, False)

    def create_file(self, filename: str, creator_agent_id: str) -> bool:
        """
        Creates a new file and its metadata, assigning ownership.

        Args:
            filename (str): The name of the file to create.
            creator_agent_id (str): The ID of the agent creating the file.

        Returns:
            True if creation was successful, False otherwise.
        """
        safe_path = self._get_safe_path(filename)
        if not safe_path or os.path.exists(safe_path):
            print(f"[FSM] Failed to create file: '{filename}' (unsafe or already exists).")
            return False
        
        # Create the actual file
        with open(safe_path, 'w') as f:
            f.write("") # Create an empty file
        
        # Create and write the metadata
        metadata = {
            "owner": creator_agent_id,
            "permissions": {} # No permissions for others by default
        }
        self._write_metadata(safe_path, metadata)
        print(f"[FSM] Agent '{creator_agent_id}' created file: '{filename}'")
        return True

    def write_file(self, filename: str, content: str, agent_id: str) -> bool:
        """Writes content to a file if the agent has permission."""
        if not self.check_permission(filename, agent_id, 'write'):
            print(f"[SECURITY] Agent '{agent_id}' denied WRITE access to '{filename}'.")
            return False
            
        safe_path = self._get_safe_path(filename)
        if not safe_path:
            return False
        
        with open(safe_path, 'w') as f:
            f.write(content)
        print(f"[FSM] Agent '{agent_id}' wrote to file: '{filename}'")
        return True

    def read_file(self, filename: str, agent_id: str) -> str | None:
        """Reads a file's content if the agent has permission."""
        if not self.check_permission(filename, agent_id, 'read'):
            print(f"[SECURITY] Agent '{agent_id}' denied READ access to '{filename}'.")
            return None
        
        safe_path = self._get_safe_path(filename)
        if not safe_path or not os.path.exists(safe_path):
            return None

        with open(safe_path, 'r') as f:
            return f.read()

    def set_permission(self, filename: str, owner_agent_id: str, target_agent_id: str, permission: str, value: bool) -> bool:
        """Sets a permission for a target agent on a file."""
        safe_path = self._get_safe_path(filename)
        if not safe_path:
            return False
            
        metadata = self._read_metadata(safe_path)

        # Only the owner can change permissions.
        if metadata.get("owner") != owner_agent_id:
            print(f"[SECURITY] Agent '{owner_agent_id}' is not the owner of '{filename}'. Permission change denied.")
            return False
        
        if target_agent_id not in metadata['permissions']:
            metadata['permissions'][target_agent_id] = {}
        
        metadata['permissions'][target_agent_id][permission] = value
        self._write_metadata(safe_path, metadata)
        print(f"[FSM] Owner '{owner_agent_id}' set '{permission}={value}' for '{target_agent_id}' on '{filename}'.")
        return True