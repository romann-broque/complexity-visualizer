#!/usr/bin/env python3
"""CLI for building graph.json from DOT files."""
import argparse
import sys

from complexity_visualizer.graph_builder import build_graph


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build dependency graph from jdeps DOT files"
    )
    parser.add_argument("--from", dest="dot_dir", required=True, help="Directory containing .dot files")
    parser.add_argument("--out", default="dist/graph.json", help="Output path (default: dist/graph.json)")
    parser.add_argument("--include-prefix", dest="prefixes", action="append", help="Filter by package prefix")
    parser.add_argument("--source", dest="source_dir", help="Java source root (e.g., src/main/java) for complexity analysis")

    args = parser.parse_args()

    try:
        result = build_graph(args.dot_dir, args.out, args.prefixes, args.source_dir)
        print(f"✅ {result['nodeCount']} nodes, {result['edgeCount']} edges → {args.out}")
        if args.source_dir:
            print(f"   📊 Source code complexity analyzed")
        return 0
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())