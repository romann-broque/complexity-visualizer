#!/usr/bin/env python3
"""Command-line interface for the complexity visualizer.

This script provides the main entry point for parsing jdeps DOT files
and generating dependency graphs with metrics.
"""
from __future__ import annotations
import argparse
import sys

from complexity_visualizer.build_graph import build_graph


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Complexity Visualizer - Convert jdeps DOT files to dependency graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s --from ./dot_files/ --out ./dist/graph.json
  
  # With DSM output
  %(prog)s --from ./dot_files/ --out ./dist/graph.json --dsm ./dist/dsm.json
  
  # Filter by package prefix
  %(prog)s --from ./dot_files/ --out ./dist/graph.json --include-prefix com.myapp
        """
    )

    parser.add_argument(
        "--from",
        dest="from_directory",
        default="from/poseidon",
        help="Directory containing .dot files (default: from/)",
    )

    parser.add_argument(
        "--out",
        dest="output_graph",
        default="dist/graph.json",
        help="Output path for graph.json (default: dist/graph.json)",
    )

    parser.add_argument(
        "--dsm",
        dest="output_dsm",
        default="dist/dsm.json",
        help="Output path for DSM matrix (default: dist/dsm.json)",
    )

    parser.add_argument(
        "--include-prefix",
        dest="include_prefixes",
        action="append",
        default=[],
        metavar="PREFIX",
        help=(
            "Keep only nodes whose ID starts with this prefix. "
            "Can be specified multiple times. "
            "Example: --include-prefix com.myapp --include-prefix org.myapp"
        ),
    )

    return parser


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        result = build_graph(
            dot_directory=args.from_directory,
            output_graph_path=args.output_graph,
            output_dsm_path=args.output_dsm,
            include_prefixes=args.include_prefixes if len(args.include_prefixes) > 0 else None,
        )

        # Print success message
        print(
            f"✅ Successfully processed {result['nodeCount']} nodes "
            f"and {result['edgeCount']} edges"
        )
        print(f"   Graph written to: {result['graphPath']}")

        if result['dsmPath']:
            print(f"   DSM written to: {result['dsmPath']}")

        return 0

    except FileNotFoundError as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        return 1
    # except Exception as error:
    #     print(f"❌ Unexpected error: {error}", file=sys.stderr)
    #     return 2


if __name__ == "__main__":
    sys.exit(main())