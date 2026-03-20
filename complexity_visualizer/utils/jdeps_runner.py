"""Execute jdeps to generate .dot files from compiled Java classes."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def check_jdeps_available() -> bool:
    """Check if jdeps command is available in PATH."""
    return shutil.which("jdeps") is not None


def run_jdeps(
    classes_dir: str,
    output_dir: str,
    prefixes: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict:
    """
    Execute jdeps on compiled classes to generate .dot dependency files.

    Args:
        classes_dir: Directory containing compiled .class files
        output_dir: Directory where .dot files will be saved
        prefixes: Optional list of package prefixes to filter
        verbose: Print detailed progress

    Returns:
        Dict with summary: {
            'success': bool,
            'files_processed': int,
            'files_generated': int,
            'errors': List[str]
        }
    """
    if not check_jdeps_available():
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": ["jdeps not found. Please install Java JDK >= 11"],
        }

    classes_path = Path(classes_dir)
    if not classes_path.exists():
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": [f"Classes directory not found: {classes_dir}"],
        }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all .class files or directories to analyze
    class_files = list(classes_path.rglob("*.class"))

    if not class_files:
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": [
                f"No .class files found in {classes_dir}. Did you compile the project?"
            ],
        }

    # Build jdeps command
    cmd = ["jdeps", "-dotoutput", str(output_path), "-verbose:class"]

    # Add package filters if provided
    if prefixes:
        for prefix in prefixes:
            cmd.extend(["-include", f"{prefix}.*"])

    # Add all class files or the directory
    cmd.append(str(classes_path))

    if verbose:
        print(f"Executing: {' '.join(cmd)}")

    errors = []
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            errors.append(f"jdeps failed: {result.stderr}")
            return {
                "success": False,
                "files_processed": len(class_files),
                "files_generated": 0,
                "errors": errors,
            }

        # Count generated .dot files
        dot_files = list(output_path.glob("*.dot"))

        return {
            "success": True,
            "files_processed": len(class_files),
            "files_generated": len(dot_files),
            "errors": [],
        }

    except Exception as e:
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": [f"Unexpected error: {str(e)}"],
        }


def find_jar_files(project_path: str) -> List[Path]:
    """
    Find JAR files in common Maven/Gradle locations.

    Args:
        project_path: Root directory of the project

    Returns:
        List of Path objects for found JAR files
    """
    project = Path(project_path)
    jar_locations = [
        project / "target",  # Maven
        project / "build" / "libs",  # Gradle
    ]

    jar_files = []
    for location in jar_locations:
        if location.exists():
            jar_files.extend(location.glob("*.jar"))

    return jar_files


def run_jdeps_on_jars(
    jar_files: List[Path], output_dir: str, verbose: bool = False
) -> Dict:
    """
    Execute jdeps on JAR files.

    Args:
        jar_files: List of JAR file paths
        output_dir: Directory where .dot files will be saved
        verbose: Print detailed progress

    Returns:
        Dict with summary (same format as run_jdeps)
    """
    if not check_jdeps_available():
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": ["jdeps not found. Please install Java JDK >= 11"],
        }

    if not jar_files:
        return {
            "success": False,
            "files_processed": 0,
            "files_generated": 0,
            "errors": ["No JAR files provided"],
        }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    errors = []
    total_dots_before = len(list(output_path.glob("*.dot")))

    for jar in jar_files:
        if not jar.exists():
            errors.append(f"JAR not found: {jar}")
            continue

        cmd = ["jdeps", "-dotoutput", str(output_path), "-verbose:class", str(jar)]

        if verbose:
            print(f"Processing {jar.name}...")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                errors.append(f"jdeps failed for {jar.name}: {result.stderr}")

        except Exception as e:
            errors.append(f"Error processing {jar.name}: {str(e)}")

    total_dots_after = len(list(output_path.glob("*.dot")))
    files_generated = total_dots_after - total_dots_before

    return {
        "success": len(errors) == 0 or files_generated > 0,
        "files_processed": len(jar_files),
        "files_generated": files_generated,
        "errors": errors,
    }
