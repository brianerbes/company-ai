# core_logic/audit_log.py

"""
This module provides a secure AuditLogger for creating an immutable trail
of all significant actions taken by human agents.
"""

import datetime
import os

class AuditLogger:
    """
    Handles writing timestamped, append-only logs for accountability.
    """
    def __init__(self, log_directory: str = "logs"):
        """
        Initializes the AuditLogger.

        Args:
            log_directory (str): The directory where log files will be stored.
        """
        self.log_directory = os.path.abspath(log_directory)
        os.makedirs(self.log_directory, exist_ok=True)
        
        # Define a specific log file for human actions
        self.log_file = os.path.join(self.log_directory, "human_actions_audit.log")
        print(f"AuditLogger initialized. Logging human actions to: {self.log_file}")

    def log_action(self, human_agent_id: str, action: str, details: str = ""):
        """
        Writes a new entry to the audit log.

        The log is append-only, meaning we never overwrite previous entries.

        Args:
            human_agent_id (str): The ID of the human agent performing the action.
            action (str): A short description of the action (e.g., 'EXECUTE_APPROVAL').
            details (str, optional): A more detailed description of the action.
                                     e.g., "Approved execution of script.py for agent qa_tester".
                                     Defaults to "".
        """
        # Get the current timestamp in ISO 8601 format
        timestamp = datetime.datetime.now().isoformat()
        
        # Format the log entry
        log_entry = f"[{timestamp}] [ACTOR: {human_agent_id}] [ACTION: {action}]"
        if details:
            log_entry += f" [DETAILS: {details}]"
        
        # Open the file in 'append' mode ('a') and write the new entry
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            # Basic error handling in case the log file can't be written to.
            print(f"[CRITICAL] Failed to write to audit log: {e}")