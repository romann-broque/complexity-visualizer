"""Base interface for language analyzers.

This module defines the abstract interface that all language-specific
analyzers must implement to support multi-language analysis.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific code analyzers."""

    @abstractmethod
    def detect_project(self, path: Path) -> bool:
        """
        Detect if the given path contains a project of this language.

        Args:
            path: Project root directory

        Returns:
            True if this language's project is detected
        """
        pass

    @abstractmethod
    def get_source_directories(self, path: Path) -> list[Path]:
        """
        Get source code directories for this project.

        Args:
            path: Project root directory

        Returns:
            List of source directories
        """
        pass

    @abstractmethod
    def get_class_directories(self, path: Path) -> list[Path]:
        """
        Get compiled class/bytecode directories for this project.

        Args:
            path: Project root directory

        Returns:
            List of class directories (may be empty for interpreted languages)
        """
        pass

    @abstractmethod
    def analyze_file(self, file_path: Path) -> Dict[str, int]:
        """
        Analyze a single source file for complexity metrics.

        Args:
            file_path: Path to source file

        Returns:
            Dictionary with metrics: {'complexity': int, 'loc': int, 'methods': int}
        """
        pass

    @abstractmethod
    def extract_dependencies(self, path: Path) -> Optional[Path]:
        """
        Extract dependency information from the project.

        Args:
            path: Project root directory

        Returns:
            Path to directory containing dependency files (.dot, .json, etc.)
            or None if extraction failed
        """
        pass
