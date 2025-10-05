#!/usr/bin/env python3
from __future__ import annotations
import argparse
from complexity_visualizer.convert_codecharta import convert_file

def main() -> None:
    ap = argparse.ArgumentParser(description="Convert graph.json → codecharta.json")
    ap.add_argument("--in", dest="in_file", required=True, help="path to graph.json")
    ap.add_argument("--out", dest="out_file", default="dist/codecharta.json", help="output codecharta.json")
    ap.add_argument("--project", dest="project_name", default=None, help="project name (root node)")
    args = ap.parse_args()

    convert_file(args.in_file, args.out_file, args.project_name)
    print(f"✔ Wrote {args.out_file}")

if __name__ == "__main__":
    main()
