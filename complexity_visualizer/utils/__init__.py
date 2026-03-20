"""Utils Module

Utility functions for project detection, jdeps execution, and CodeCharta integration.
"""

from __future__ import annotations

from .browser_opener import open_in_codecharta, CODECHARTA_URL

__all__ = ["open_in_codecharta", "CODECHARTA_URL"]
