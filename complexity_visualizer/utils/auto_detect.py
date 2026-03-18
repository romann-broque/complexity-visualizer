"""Auto-detection of project type and structure.

Automatically detects Maven/Gradle projects and locates source/class directories.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Default package prefixes for application code (excludes infrastructure)
DEFAULT_PACKAGE_PREFIXES = ["com.", "org.", "io."]


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


def auto_detect_source_root(path: Path) -> Optional[Path]:
    """
    Auto-detect Java source root directory.

    Searches for common Java source directory structures
    (Maven/Gradle: src/main/java, plain: src/).

    Args:
        path: Project root directory

    Returns:
        Path to source root containing .java files, or None if not found
    """
    # Common Java source locations (in order of preference)
    candidates = [
        path / "src" / "main" / "java",  # Maven/Gradle standard
        path / "src" / "main" / "kotlin",  # Kotlin projects
        path / "src",  # Plain Java projects
        path / "java",  # Alternative structure
    ]

    for candidate in candidates:
        if candidate.exists() and list(candidate.rglob("*.java")):
            return candidate

    return None


def detect_main_package(source_root: Path) -> Optional[str]:
    """
    Detect the main application package by finding the most common root package.

    Args:
        source_root: Java source root directory (e.g., src/main/java)

    Returns:
        Main package prefix (e.g., 'com.company.project'), or None if not found
    """
    if not source_root or not source_root.exists():
        return None

    package_counts = {}

    # Find all .java files and extract their packages
    for java_file in source_root.rglob("*.java"):
        # Read first 20 lines to find package declaration
        try:
            with open(java_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("package "):
                        # Extract package name
                        package = line[8:].rstrip(";").strip()

                        # Get first 3 levels (e.g., com.company.project)
                        parts = package.split(".")
                        if len(parts) >= 3:
                            root_package = ".".join(parts[:3])
                            package_counts[root_package] = (
                                package_counts.get(root_package, 0) + 1
                            )
                        break
        except Exception:
            continue

    if not package_counts:
        return None

    # Return the most common root package
    main_package = max(package_counts.items(), key=lambda x: x[1])[0]
    return main_package


def resolve_include_prefixes(
    include_prefix: Optional[List[str]], source_root: Optional[Path] = None
) -> Optional[List[str]]:
    """
    Resolve package prefixes to use for filtering.

    Logic:
    - If --include-prefix is provided: Use user-specified prefixes
    - Otherwise: Try to auto-detect main package from source code
    - If detection fails: Return None (no filtering)

    Args:
        include_prefix: User-specified prefixes (can be None or empty list)
        source_root: Source root for auto-detection (optional)

    Returns:
        List of prefixes to include, or None for no filtering
    """
    if include_prefix:
        # User specified custom prefixes
        return include_prefix

    # Try to auto-detect main package
    if source_root:
        detected = detect_main_package(source_root)
        if detected:
            return [detected]

    # Default: no filtering (show everything)
    return None
