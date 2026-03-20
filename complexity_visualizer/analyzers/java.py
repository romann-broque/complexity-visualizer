"""Analyze Java source files for complexity metrics."""

import re
from pathlib import Path
from typing import Dict, Optional


class JavaComplexityAnalyzer:
    """Calculate cyclomatic complexity and LOC from Java source."""

    # Complexity keywords
    COMPLEXITY_PATTERNS = [
        r"\bif\s*\(",
        r"\belse\s+if\s*\(",
        r"\bfor\s*\(",
        r"\bwhile\s*\(",
        r"\bcase\s+",
        r"\bcatch\s*\(",
        r"\b\?\s*",  # Ternary operator
        r"\&\&",  # Logical AND
        r"\|\|",  # Logical OR
    ]

    # Pattern to detect abstract classes and interfaces
    ABSTRACT_PATTERN = re.compile(
        r"^\s*(?:public\s+)?(?:abstract\s+class|interface)\s+", re.MULTILINE
    )

    @staticmethod
    def analyze_file(file_path: Path) -> Dict[str, int]:
        """
        Analyze a Java file and return complexity metrics.

        Returns:
            {
                'complexity': cyclomatic complexity,
                'loc': lines of code (non-empty, non-comment),
                'is_abstract': 1 if interface or abstract class, 0 otherwise
            }
        """
        if not file_path.exists():
            return {"complexity": 0, "loc": 0, "is_abstract": 0}

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return {"complexity": 0, "loc": 0, "is_abstract": 0}

        # Remove comments
        content_no_comments = JavaComplexityAnalyzer._remove_comments(content)

        # Calculate metrics
        complexity = JavaComplexityAnalyzer._calculate_complexity(content_no_comments)
        loc = JavaComplexityAnalyzer._count_loc(content_no_comments)
        is_abstract = (
            1
            if JavaComplexityAnalyzer.ABSTRACT_PATTERN.search(content_no_comments)
            else 0
        )

        return {"complexity": complexity, "loc": loc, "is_abstract": is_abstract}

    @staticmethod
    def _remove_comments(content: str) -> str:
        """Remove single-line and multi-line comments."""
        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # Remove single-line comments
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
        return content

    @staticmethod
    def _calculate_complexity(content: str) -> int:
        """
        Calculate cyclomatic complexity.
        Base complexity = 1, +1 for each decision point.
        """
        complexity = 1  # Base complexity

        for pattern in JavaComplexityAnalyzer.COMPLEXITY_PATTERNS:
            matches = re.findall(pattern, content)
            complexity += len(matches)

        return complexity

    @staticmethod
    def _count_loc(content: str) -> int:
        """Count non-empty lines."""
        lines = content.split("\n")
        return sum(1 for line in lines if line.strip())


def analyze_source_directory(
    source_root: str, class_fqns: list[str], verbose: bool = False
) -> Dict[str, Dict[str, int]]:
    """
    Analyze Java source files for all classes.

    Automatically detects Maven/Gradle structure (src/main/java/).

    Args:
        source_root: Root directory of Java sources (e.g., 'src/' or 'src/main/java')
        class_fqns: List of fully qualified class names from graph
        verbose: Show detailed per-file analysis progress

    Returns:
        Dict mapping class FQN to metrics dict
    """
    root = Path(source_root)

    # 🔍 Auto-detection: Try multiple candidate roots
    candidate_roots = [
        root,  # As provided
        root / "main" / "java",  # Maven/Gradle from src/
        root / "src" / "main" / "java",  # Maven/Gradle from project root
    ]

    # Find best root by testing a sample of FQNs
    detected_root = _detect_source_root(candidate_roots, class_fqns)

    if detected_root != root:
        rel_path = (
            detected_root.relative_to(root)
            if detected_root.is_relative_to(root)
            else detected_root
        )
        print(f"   📁 Auto-detected source root: {root.name}/{rel_path}")

    metrics = {}
    files_found = 0
    files_not_found = []

    for fqn in class_fqns:
        # Convert FQN to file path: com.example.Foo -> com/example/Foo.java
        relative_path = fqn.replace(".", "/") + ".java"

        # Handle inner classes: com.example.Outer$Inner -> Outer.java
        if "$" in fqn:
            outer_class = fqn.split("$")[0]
            relative_path = outer_class.replace(".", "/") + ".java"

        file_path = detected_root / relative_path
        result = JavaComplexityAnalyzer.analyze_file(file_path)

        # Track statistics
        if result["loc"] > 0 or file_path.exists():
            files_found += 1
            if verbose:
                print(
                    f"      ✓ {fqn} → {file_path.name} ({result['loc']} loc, {result['complexity']} complexity)"
                )
        else:
            files_not_found.append(fqn)
            if verbose:
                print(f"      ✗ {fqn} → {file_path.name} (not found)")

        metrics[fqn] = result

    # 📊 Report analysis results
    total = len(class_fqns)
    print(
        f"   ✅ Successfully analyzed: {files_found}/{total} classes ({files_found * 100 // total if total > 0 else 0}%)"
    )

    if files_not_found:
        not_found_count = len(files_not_found)
        if not_found_count <= 5:
            print(f"   ⚠️  Not found: {', '.join(files_not_found)}")
        else:
            print(
                f"   ⚠️  Not found: {not_found_count} classes (likely generated/inner classes)"
            )

    # Calculate totals
    total_loc = sum(m["loc"] for m in metrics.values())
    total_complexity = sum(m["complexity"] for m in metrics.values())

    if total_loc > 0:
        print(f"   📊 Total: {total_loc:,} LOC, {total_complexity:,} complexity")

    return metrics


def _detect_source_root(candidates: list[Path], sample_fqns: list[str]) -> Path:
    """
    Detect the correct source root by testing which candidate
    can resolve the most FQNs.

    Args:
        candidates: List of possible source root directories
        sample_fqns: List of fully qualified class names to test

    Returns:
        The best matching source root
    """
    # Test with first 10 FQNs (sample)
    sample = sample_fqns[: min(10, len(sample_fqns))]

    best_root = candidates[0]
    best_score = 0

    for candidate in candidates:
        if not candidate.exists():
            continue

        score = 0
        for fqn in sample:
            # Handle inner classes: Outer$Inner -> Outer
            test_fqn = fqn.split("$")[0] if "$" in fqn else fqn

            relative_path = test_fqn.replace(".", "/") + ".java"
            file_path = candidate / relative_path

            if file_path.exists():
                score += 1

        if score > best_score:
            best_score = score
            best_root = candidate

    return best_root
