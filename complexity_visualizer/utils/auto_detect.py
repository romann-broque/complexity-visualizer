"""Auto-detection of project type and structure.

Automatically detects Maven/Gradle projects and locates source/class directories.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Optional


def detect_project_type(path: Path) -> Dict:
    """
    Detect project type and structure.

    Args:
        path: Project root directory

    Returns:
        Dictionary with:
        - type: "maven", "gradle", or "unknown"
        - source_dirs: List of source directories
        - class_dirs: List of compiled class directories
        - has_jdeps: Whether jdeps is available
    """
    result = {
        "type": "unknown",
        "source_dirs": [],
        "class_dirs": [],
        "has_jdeps": shutil.which("jdeps") is not None,
    }

    # Detect Maven
    if (path / "pom.xml").exists():
        result["type"] = "maven"
        result["source_dirs"] = ["src/main/java", "src/main/kotlin"]
        result["class_dirs"] = ["target/classes"]

    # Detect Gradle
    elif (path / "build.gradle").exists() or (path / "build.gradle.kts").exists():
        result["type"] = "gradle"
        result["source_dirs"] = ["src/main/java", "src/main/kotlin"]
        result["class_dirs"] = ["build/classes/java/main", "build/classes/kotlin/main"]

    # Verify directories actually exist
    result["source_dirs"] = [
        str(d) for d in result["source_dirs"] if (path / d).exists()
    ]
    result["class_dirs"] = [str(d) for d in result["class_dirs"] if (path / d).exists()]

    return result


def find_dot_files(path: Path) -> Optional[Path]:
    """
    Search for .dot files in common locations.

    Args:
        path: Project root directory

    Returns:
        Path to directory containing .dot files, or None
    """
    # First check if the path itself contains .dot files
    if path.exists() and list(path.glob("*.dot")):
        return path

    # Then check common subdirectories
    common_locations = [
        path / "from",
        path / ".complexity-viz" / "dot",
        path / "dot",
        path / "deps",
    ]

    for location in common_locations:
        if location.exists() and list(location.glob("*.dot")):
            return location

    return None


def needs_compilation(path: Path, project_type: str) -> bool:
    """
    Check if project needs to be compiled.

    Args:
        path: Project root directory
        project_type: "maven", "gradle", or "unknown"

    Returns:
        True if compilation is needed
    """
    if project_type == "maven":
        target_classes = path / "target" / "classes"
        return not target_classes.exists() or not list(target_classes.rglob("*.class"))

    elif project_type == "gradle":
        build_classes = path / "build" / "classes" / "java" / "main"
        return not build_classes.exists() or not list(build_classes.rglob("*.class"))

    return False


def get_compile_command(project_type: str) -> Optional[str]:
    """
    Get the compile command for the project type.

    Args:
        project_type: "maven", "gradle", or "unknown"

    Returns:
        Compile command string, or None
    """
    if project_type == "maven":
        return "mvn compile"
    elif project_type == "gradle":
        return (
            "./gradlew compileJava"
            if Path("gradlew").exists()
            else "gradle compileJava"
        )
    return None


def find_compiled_classes(path: Path) -> Optional[Path]:
    """
    Find the directory containing compiled .class files.

    Args:
        path: Project root directory

    Returns:
        Path to classes directory, or None if not found
    """
    project_info = detect_project_type(path)

    # Check detected class directories
    for class_dir in project_info["class_dirs"]:
        class_path = path / class_dir
        if class_path.exists() and list(class_path.rglob("*.class")):
            return class_path

    # Fallback: search common locations
    common_locations = [
        path / "target" / "classes",
        path / "build" / "classes" / "java" / "main",
        path / "build" / "classes" / "kotlin" / "main",
        path / "out" / "production",
        path / "bin",
    ]

    for location in common_locations:
        if location.exists() and list(location.rglob("*.class")):
            return location

    return None
