#!/usr/bin/env python3
"""CLI for building graph.json from DOT files."""
from __future__ import annotations
import argparse
import sys

from complexity_visualizer.graph_builder import build_graph


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Build dependency graph from jdeps DOT files",
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
        required=True,
        help="Directory containing .dot files",
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
        default=None,
        help="Optional output path for DSM.json",
    )

    parser.add_argument(
        "--include-prefix",
        dest="include_prefixes",
        action="append",
        default=[],
        metavar="PREFIX",
        help="Keep only nodes starting with prefix (can specify multiple)",
    )

    parser.add_argument(
        "--no-enhanced",
        dest="enhanced",
        action="store_false",
        help="Disable enhanced metrics computation",
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        result = build_graph(
            dot_directory=args.from_directory,
            output_graph_path=args.output_graph,
            output_dsm_path=args.output_dsm,
            include_prefixes=args.include_prefixes if args.include_prefixes else None,
            enhanced=args.enhanced,
        )

        print(
            f"✅ Successfully processed {result['nodeCount']} nodes "
            f"and {result['edgeCount']} edges"
        )
        print(f"   Graph written to: {result['graphPath']}")

        if result['dsmPath']:
            print(f"   DSM written to: {result['dsmPath']}")

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())