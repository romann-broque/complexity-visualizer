"""Input/Output utilities for file operations.

This module provides helper functions for file system operations,
particularly for JSON file writing with proper error handling.
"""
from __future__ import annotations
import json
import os
from typing import Any


class FileWriter:
    """Handles file writing operations."""

    @staticmethod
    def ensure_parent_directory(file_path: str) -> None:
        """Create parent directories for a file path if they don't exist.
        
        Args:
            file_path: Path to a file whose parent directories should be created
        """
        parent_directory = os.path.dirname(file_path)
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory, exist_ok=True)

    @staticmethod
    def write_json(file_path: str, data: Any) -> None:
        """Write data to a JSON file with proper formatting.
        
        Args:
            file_path: Path where the JSON file should be written
            data: Python object to serialize to JSON
        """
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


# Convenience functions for backward compatibility
def ensure_parent_dir(file_path: str) -> None:
    """Create parent directories if they don't exist."""
    FileWriter.ensure_parent_directory(file_path)


def write_json(file_path: str, data: Any) -> None:
    """Write data to a JSON file."""
    FileWriter.write_json(file_path, data)