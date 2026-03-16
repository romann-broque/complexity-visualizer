"""Analyze Java source files for complexity metrics."""
import re
from pathlib import Path
from typing import Dict, Optional


class JavaComplexityAnalyzer:
    """Calculate cyclomatic complexity and LOC from Java source."""

    # Complexity keywords
    COMPLEXITY_PATTERNS = [
        r'\bif\s*\(',
        r'\belse\s+if\s*\(',
        r'\bfor\s*\(',
        r'\bwhile\s*\(',
        r'\bcase\s+',
        r'\bcatch\s*\(',
        r'\b\?\s*',  # Ternary operator
        r'\&\&',     # Logical AND
        r'\|\|',     # Logical OR
    ]

    METHOD_PATTERN = re.compile(
        r'(public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{'
    )

    @staticmethod
    def analyze_file(file_path: Path) -> Dict[str, int]:
        """
        Analyze a Java file and return complexity metrics.

        Returns:
            {
                'complexity': cyclomatic complexity,
                'loc': lines of code (non-empty, non-comment),
                'methods': number of methods
            }
        """
        if not file_path.exists():
            return {'complexity': 0, 'loc': 0, 'methods': 0}

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return {'complexity': 0, 'loc': 0, 'methods': 0}

        # Remove comments
        content_no_comments = JavaComplexityAnalyzer._remove_comments(content)

        # Calculate metrics
        complexity = JavaComplexityAnalyzer._calculate_complexity(content_no_comments)
        loc = JavaComplexityAnalyzer._count_loc(content_no_comments)
        methods = len(JavaComplexityAnalyzer.METHOD_PATTERN.findall(content_no_comments))

        return {
            'complexity': complexity,
            'loc': loc,
            'methods': methods
        }

    @staticmethod
    def _remove_comments(content: str) -> str:
        """Remove single-line and multi-line comments."""
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
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
        lines = content.split('\n')
        return sum(1 for line in lines if line.strip())


def analyze_source_directory(
        source_root: str,
        class_fqns: list[str]
) -> Dict[str, Dict[str, int]]:
    """
    Analyze Java source files for all classes.

    Args:
        source_root: Root directory of Java sources (e.g., 'src/main/java')
        class_fqns: List of fully qualified class names from graph

    Returns:
        Dict mapping class FQN to metrics dict
    """
    root = Path(source_root)
    metrics = {}

    for fqn in class_fqns:
        # Convert FQN to file path: com.example.Foo -> com/example/Foo.java
        relative_path = fqn.replace('.', '/') + '.java'
        file_path = root / relative_path

        # Handle inner classes: com.example.Outer$Inner -> Outer.java
        if '$' in fqn:
            outer_class = fqn.split('$')[0]
            relative_path = outer_class.replace('.', '/') + '.java'
            file_path = root / relative_path

        metrics[fqn] = JavaComplexityAnalyzer.analyze_file(file_path)

    return metrics