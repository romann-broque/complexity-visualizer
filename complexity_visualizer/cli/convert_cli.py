#!/usr/bin/env python3
"""CLI for converting graph.json to codecharta.json."""
import argparse
import sys

from complexity_visualizer.codecharta_converter.converter import convert_to_codecharta


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert graph.json to CodeCharta format")
    parser.add_argument("--in", dest="input", required=True, help="Path to graph.json")
    parser.add_argument("--out", default="dist/codecharta.json", help="Output path")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    try:
        convert_to_codecharta(args.input, args.out, args.project)
        print(f"✅ Converted → {args.out}")
        return 0
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())