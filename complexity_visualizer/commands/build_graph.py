"""Command: build-graph

Build dependency graph and compute metrics from .dot files.
"""

from __future__ import annotations

import sys
from pathlib import Path

from complexity_visualizer.core.parsers import parse_dot_directory
from complexity_visualizer.core.metrics import compute_metrics
from complexity_visualizer.exporters.intermediate import export_intermediate
from complexity_visualizer.analyzers.java import analyze_source_directory


def cmd_build_graph(args) -> int:
    """
    Build dependency graph and compute metrics.

    Args:
        args: Argparse namespace with:
            - dot_dir: Directory containing .dot files
            - source: Source code directory (optional)
            - output: Output directory
            - include_prefix: Package prefixes to filter
            - project: Project name
            - metrics_filename: Custom metrics filename (optional, default: "metrics.json")

    Returns:
        Exit code (0 = success, 1 = error)
    """
    dot_dir = Path(args.dot_dir).resolve()

    if not dot_dir.exists():
        print(f"❌ Error: .dot directory not found: {dot_dir}", file=sys.stderr)
        print("   Run 'complexity-viz generate-dots' first", file=sys.stderr)
        return 1

    # Check for .dot files
    dot_files = list(dot_dir.glob("*.dot"))
    if not dot_files:
        print(f"❌ Error: No .dot files found in {dot_dir}", file=sys.stderr)
        return 1

    print(f"📊 Building dependency graph from {len(dot_files)} .dot files...")

    # Parse .dot files with filtering
    include_prefix = getattr(args, "include_prefix", None)
    try:
        graph = parse_dot_directory(str(dot_dir), include_prefixes=include_prefix)
    except Exception as e:
        print(f"❌ Error parsing .dot files: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    print(f"   Found {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Analyze source code if provided
    source_metrics = None
    if args.source:
        source_dir = Path(args.source).resolve()
        if source_dir.exists():
            print(f"🔍 Analyzing source code: {source_dir}")
            try:
                class_fqns = [node.id for node in graph.nodes]
                source_metrics = analyze_source_directory(str(source_dir), class_fqns)
                print(f"   Analyzed {len(source_metrics)} classes")
            except Exception as e:
                print(
                    f"⚠️  Warning: Could not analyze source code: {e}", file=sys.stderr
                )
        else:
            print(
                f"⚠️  Warning: Source directory not found: {source_dir}", file=sys.stderr
            )

    # Compute metrics
    print("📈 Computing metrics...")
    try:
        metrics = compute_metrics(graph, source_metrics)
    except Exception as e:
        print(f"❌ Error computing metrics: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Set up output directory
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Add project name to metadata
    if args.project:
        graph.meta["projectName"] = args.project

    # Determine metrics filename
    metrics_filename = getattr(args, "metrics_filename", None) or "metrics.json"

    # Export to intermediate format
    metrics_path = output_dir / metrics_filename
    print(f"💾 Saving metrics: {metrics_path}")
    try:
        export_intermediate(graph, metrics, str(metrics_path))
    except Exception as e:
        print(f"❌ Error saving metrics: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    print(f"✅ Metrics saved successfully")
    print(f"\n📁 Output:")
    print(f"   {metrics_path}")
    print(f"\n💡 Next step:")
    print(f"   complexity-viz convert {metrics_path}")

    return 0
