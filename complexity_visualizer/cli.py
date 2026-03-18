#!/usr/bin/env python3
"""Unified CLI for Complexity Visualizer v2.

Clean, modular command structure:
- generate-dots: Generate .dot files using jdeps
- build-graph: Build dependency graph and compute metrics
- convert: Convert to CodeCharta format
- visualize: Open CodeCharta visualization
- run: Execute full pipeline (all-in-one)
"""

from __future__ import annotations

import argparse
import sys

from complexity_visualizer.commands.generate_dots import cmd_generate_dots
from complexity_visualizer.commands.build_graph import cmd_build_graph
from complexity_visualizer.commands.convert import cmd_convert
from complexity_visualizer.commands.visualize import cmd_visualize
from complexity_visualizer.commands.run import cmd_run


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="complexity-viz",
        description="Analyze and visualize software complexity with CodeCharta",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ========================================================================
    # Command: generate-dots
    # ========================================================================
    generate_parser = subparsers.add_parser(
        "generate-dots", help="Generate .dot dependency files using jdeps"
    )
    generate_parser.add_argument("path", help="Project root directory")
    generate_parser.add_argument(
        "--output",
        "-o",
        help="Output directory for .dot files (default: ./from/<project-name>)",
    )
    generate_parser.add_argument(
        "--classes", help="Compiled classes directory (auto-detected if not specified)"
    )
    generate_parser.add_argument(
        "--include-prefix",
        action="append",
        help="Filter packages by prefix (can be used multiple times)",
    )
    generate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )
    generate_parser.set_defaults(func=cmd_generate_dots)

    # ========================================================================
    # Command: build-graph
    # ========================================================================
    build_parser = subparsers.add_parser(
        "build-graph", help="Build dependency graph and compute metrics"
    )
    build_parser.add_argument("dot_dir", help="Directory containing .dot files")
    build_parser.add_argument(
        "--source", "-s", help="Source code directory (for complexity analysis)"
    )
    build_parser.add_argument(
        "--include-prefix", action="append", help="Filter packages by prefix"
    )
    build_parser.add_argument("--project", help="Project name for metadata")
    build_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed analysis progress"
    )
    build_parser.set_defaults(func=cmd_build_graph)

    # ========================================================================
    # Command: convert
    # ========================================================================
    convert_parser = subparsers.add_parser(
        "convert", help="Convert metrics to CodeCharta format"
    )
    convert_parser.add_argument("input", help="Input file (metrics.json or graph.json)")
    convert_parser.add_argument(
        "--output", "-o", help="Output file (default: <input-dir>/codecharta.cc.json)"
    )
    convert_parser.add_argument(
        "--project", help="Project name for CodeCharta metadata"
    )
    convert_parser.set_defaults(func=cmd_convert)

    # ========================================================================
    # Command: visualize
    # ========================================================================
    visualize_parser = subparsers.add_parser(
        "visualize", help="Open CodeCharta visualization"
    )
    visualize_parser.add_argument("file", help="CodeCharta file (.cc.json)")
    visualize_parser.add_argument(
        "--no-open",
        action="store_true",
        help="Show instructions only, don't open browser",
    )
    visualize_parser.set_defaults(func=cmd_visualize)

    # ========================================================================
    # Command: run (all-in-one)
    # ========================================================================
    run_parser = subparsers.add_parser(
        "run", help="Execute full pipeline (generate → build → convert → visualize)"
    )
    run_parser.add_argument("path", help="Project root directory")
    run_parser.add_argument(
        "--source", "-s", help="Source code directory (auto-detected if not specified)"
    )
    run_parser.add_argument(
        "--include-prefix",
        action="append",
        help="Filter packages by prefix (recommended)",
    )
    run_parser.add_argument("--project", help="Project name")
    run_parser.add_argument(
        "--skip-dots",
        action="store_true",
        help="Skip .dot generation (use existing files)",
    )
    run_parser.add_argument(
        "--no-open", action="store_true", help="Don't open browser after completion"
    )
    run_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed analysis progress"
    )
    run_parser.set_defaults(func=cmd_run)

    # Parse and execute
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
