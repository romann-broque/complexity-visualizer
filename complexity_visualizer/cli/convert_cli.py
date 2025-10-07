#!/usr/bin/env python3
"""CLI for converting graph.json to codecharta.json."""
from __future__ import annotations
import argparse
import sys

from complexity_visualizer.codecharta_converter import convert_file


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert graph.json to CodeCharta format",
        epilog="""
Examples:
  # Basic conversion
  %(prog)s --in dist/graph.json --out dist/codecharta.json
  
  # With custom project name
  %(prog)s --in dist/graph.json --out dist/codecharta.json --project MyProject
        """
    )

    parser.add_argument(
        "--in",
        dest="input_file",
        required=True,
        help="Path to graph.json",
    )

    parser.add_argument(
        "--out",
        dest="output_file",
        default="dist/codecharta.json",
        help="Output path for codecharta.json (default: dist/codecharta.json)",
    )

    parser.add_argument(
        "--project",
        dest="project_name",
        default=None,
        help="Project name (root node in visualization)",
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        convert_file(args.input_file, args.output_file, args.project_name)
        print(f"✅ Converted to CodeCharta format")
        print(f"   Output: {args.output_file}")
        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())