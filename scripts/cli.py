#!/usr/bin/env python3
from __future__ import annotations
import argparse
from complexity_visualizer.build_graph import build_graph

def main() -> None:
    ap = argparse.ArgumentParser(description="Complexity Visualizer (jdeps DOT → graph.json/DSM)")
    ap.add_argument("--from", dest="from_dir", default="from/", help="DOT directory")
    ap.add_argument("--out", dest="out_graph", default="dist/graph.json", help="Output graph.json")
    ap.add_argument("--dsm", dest="out_dsm", default=None, help="Output DSM json (optional)")
    ap.add_argument(
        "--include-prefix",
        dest="include_prefixes",
        action="append",
        default=[],
        help="Keep only nodes whose id starts with this prefix (repeatable). Example: --include-prefix com.organisation.project",
    )
    args = ap.parse_args()

    result = build_graph(
        args.from_dir,
        args.out_graph,
        args.out_dsm,
        args.include_prefixes
    )
    print(f"✅ nodes={result['nodeCount']} edges={result['edgeCount']} → {result['graphPath']}"
          + (f" | DSM={result['dsmPath']}" if result['dsmPath'] else ""))

if __name__ == "__main__":
    main()
