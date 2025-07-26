# core/vfs.py

import os
from pathlib import Path

class FileSystemManager:
    """
    Manages file operations within a sandboxed company directory.

    This class ensures that all file access is restricted to the company's
    root folder, preventing directory traversal attacks. All paths are
    relative to the company root.
    """
    def __init__(self, company_root: Path):
        if not company_root.is_dir():
            raise FileNotFoundError(f"Company root directory does not exist: {company_root}")
        # Resolve the root path to an absolute, canonical path
        self.root = company_root.resolve()

    def _resolve_path(self, relative_path: str | Path) -> Path:
        """
        Safely resolves a relative path within the sandboxed root.

        Args:
            relative_path: The path relative to the company root.

        Returns:
            The resolved, absolute path.

        Raises:
            PermissionError: If the path attempts to access outside the root.
        """
        # Sanitize the input path string by removing leading slashes.
        # This prevents the path from being treated as absolute.
        # We also handle '.' as a special case for the root.
        path_str = str(relative_path).lstrip('/\\')
        if path_str == '.':
            path_str = '' # Treat '.' as the root.

        # Join the sanitized path with our secure root and resolve it.
        # This canonicalizes the path, handling '..' and other relatives.
        absolute_path = (self.root / path_str).resolve()

        # FINAL SECURITY CHECK: Use os.path.commonpath to verify that the
        # resulting path is genuinely inside our root directory.
        common_prefix = os.path.commonpath([self.root, absolute_path])
        if str(common_prefix) != str(self.root):
             raise PermissionError(f"Access denied: Path '{relative_path}' is outside the company sandbox.")

        return absolute_path

    def list_files(self, path: str = '.') -> list[str]:
        """Lists files and directories at a given relative path."""
        try:
            target_path = self._resolve_path(path)
            return os.listdir(target_path)
        except FileNotFoundError:
            return []

    def read_file(self, file_path: str) -> str | None:
        """Reads the content of a file at a given relative path."""
        try:
            target_path = self._resolve_path(file_path)
            if not target_path.is_file():
                return None
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, PermissionError):
            return None

    def write_file(self, file_path: str, content: str, append: bool = False):
        """Writes content to a file at a given relative path."""
        try:
            target_path = self._resolve_path(file_path)
            
            # Ensure the parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(target_path, mode, encoding='utf-8') as f:
                f.write(content)
        except PermissionError as e:
            # Re-raise to signal a security/access issue
            raise e