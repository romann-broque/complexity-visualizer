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
    Supports multi-module projects by searching recursively.

    Args:
        path: Project root directory

    Returns:
        Path to classes directory, or None if not found
    """
    project_info = detect_project_type(path)

    # Check detected class directories at root level
    for class_dir in project_info["class_dirs"]:
        class_path = path / class_dir
        if class_path.exists() and list(class_path.rglob("*.class")):
            return class_path

    # Fallback: search common locations at root level
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

    # Multi-module support: search in subdirectories
    # Pattern: */build/classes/java/main or */target/classes
    multi_module_patterns = [
        "*/build/classes/java/main",
        "*/build/classes/kotlin/main",
        "*/target/classes",
        "*/out/production",
    ]

    candidates = []
    for pattern in multi_module_patterns:
        for candidate in path.glob(pattern):
            if candidate.is_dir():
                class_files = list(candidate.rglob("*.class"))
                if class_files:
                    candidates.append((candidate, len(class_files)))

    # Return the directory with the most .class files
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    return None


def auto_detect_source_root(path: Path) -> Optional[Path]:
    """
    Auto-detect Java source root directory.

    Searches for common Java source directory structures
    (Maven/Gradle: src/main/java, plain: src/).
    Supports multi-module projects by searching recursively.

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

    # First try direct paths
    for candidate in candidates:
        if candidate.exists() and list(candidate.rglob("*.java")):
            return candidate

    # If not found, search for multi-module structure (e.g., */src/main/java)
    # This handles projects like: project-root/domain/src/main/java
    multi_module_candidates = []

    for pattern in ["*/src/main/java", "*/src/main/kotlin", "*/src"]:
        for candidate in path.glob(pattern):
            if candidate.is_dir():
                java_files = list(candidate.rglob("*.java"))
                if java_files:
                    multi_module_candidates.append((candidate, len(java_files)))

    # Return the source root with the most Java files
    if multi_module_candidates:
        multi_module_candidates.sort(key=lambda x: x[1], reverse=True)
        return multi_module_candidates[0][0]

    return None


def find_all_source_roots(path: Path) -> List[Path]:
    """
    Find all Java source roots in a project (for multi-module projects).

    Args:
        path: Project root directory

    Returns:
        List of source root paths containing .java files
    """
    source_roots = []

    # Search for all src/main/java directories in subdirectories
    for pattern in ["src/main/java", "*/src/main/java", "*/*/src/main/java"]:
        for candidate in path.glob(pattern):
            if candidate.is_dir() and list(candidate.rglob("*.java")):
                source_roots.append(candidate)

    # Also try src/main/kotlin
    for pattern in ["src/main/kotlin", "*/src/main/kotlin"]:
        for candidate in path.glob(pattern):
            if candidate.is_dir() and list(candidate.rglob("*.java")):
                source_roots.append(candidate)

    return source_roots


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


def detect_main_package_from_multiple_roots(source_roots: List[Path]) -> Optional[str]:
    """
    Detect the main application package from multiple source roots.
    Aggregates package counts across all source roots.

    Args:
        source_roots: List of Java source root directories

    Returns:
        Main package prefix (e.g., 'com.company.project'), or None if not found
    """
    if not source_roots:
        return None

    package_counts = {}

    # Aggregate packages from all source roots
    for source_root in source_roots:
        for java_file in source_root.rglob("*.java"):
            try:
                with open(java_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("package "):
                            package = line[8:].rstrip(";").strip()
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
    include_prefix: Optional[List[str]], project_path: Optional[Path] = None
) -> List[str]:
    """
    Resolve package prefixes to use for filtering.

    Logic:
    1. If --include-prefix is provided: Use user-specified prefixes
    2. Try to auto-detect main package from source code (supports multi-module)
    3. If detection fails: Use default prefixes (com.*, org.*, io.*)

    Args:
        include_prefix: User-specified prefixes (can be None or empty list)
        project_path: Project root path for auto-detection (optional)

    Returns:
        List of prefixes to include (never returns None)
    """
    if include_prefix:
        # User specified custom prefixes
        return include_prefix

    # Try to auto-detect main package from source code
    if project_path:
        # Find all source roots (supports multi-module projects)
        source_roots = find_all_source_roots(project_path)

        if source_roots:
            # Detect main package from all source roots
            detected = detect_main_package_from_multiple_roots(source_roots)
            if detected:
                return [detected]

        # Fallback: try single source root detection
        source_root = auto_detect_source_root(project_path)
        if source_root:
            detected = detect_main_package(source_root)
            if detected:
                return [detected]

    # Fallback: use default prefixes (excludes infrastructure like Spring, Azure, JDK)
    return DEFAULT_PACKAGE_PREFIXES
