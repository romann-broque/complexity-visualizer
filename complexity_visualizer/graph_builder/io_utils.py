from __future__ import annotations
import json
import os
from typing import Any


class FileWriter:
    """Handles file writing operations."""

    @staticmethod
    def ensure_parent_directory(file_path: str) -> None:
        """Create parent directories if they don't exist."""
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

    @staticmethod
    def write_json(file_path: str, data: Any) -> None:
        """Write data to JSON file with formatting."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)