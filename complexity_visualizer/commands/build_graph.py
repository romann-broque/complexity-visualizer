"""Command: build-graph

Build dependency graph and compute metrics from .dot files.
"""

from __future__ import annotations

import sys
from pathlib import Path

from complexity_visualizer.core.parsers import parse_dot_directory
from complexity_visualizer.core.metric_computation import compute_metrics
from complexity_visualizer.exporters.intermediate import export_intermediate
from complexity_visualizer.analyzers.java import analyze_source_directory
from complexity_visualizer.utils.auto_detect import auto_detect_source_root


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

    # Analyze source code if provided or auto-detect
    source_metrics = None
    source_dir = None

    if args.source:
        source_dir = Path(args.source).resolve()
    else:
        # Try to auto-detect source directory by searching upward from dot_dir
        # Common patterns: dot_dir might be in dist/project/dots or project/from
        search_paths = [
            dot_dir.parent.parent,  # dist/project/dots -> dist/project -> project
            dot_dir.parent,  # project/from -> project
            Path.cwd(),  # Current working directory
        ]

        for search_path in search_paths:
            if search_path.exists():
                detected = auto_detect_source_root(search_path)
                if detected:
                    source_dir = detected
                    print(f"📁 Auto-detected source directory: {source_dir}")
                    break

    if source_dir:
        if source_dir.exists():
            print(f"🔍 Analyzing source code: {source_dir}")
            try:
                # Filter only actual classes (not packages)
                # Classes typically start with uppercase, packages with lowercase
                all_fqns = [node.id for node in graph.nodes]
                class_fqns = [
                    fqn
                    for fqn in all_fqns
                    if fqn.split(".")[-1][
                        0
                    ].isupper()  # Last part starts with uppercase
                ]

                if len(class_fqns) < len(all_fqns):
                    package_count = len(all_fqns) - len(class_fqns)
                    print(
                        f"   Filtered: {len(class_fqns)} classes (excluded {package_count} packages)"
                    )

                verbose = getattr(args, "verbose", False)
                source_metrics = analyze_source_directory(
                    str(source_dir), class_fqns, verbose=verbose
                )

                # Check if analysis was successful
                successful = sum(1 for m in source_metrics.values() if m["loc"] > 0)
                if successful == 0:
                    print(f"\n⚠️  WARNING: No source files were found!")
                    print(f"   Provided path: {source_dir}")

                    # Suggest alternatives
                    candidates = [
                        source_dir / "main" / "java",
                        source_dir / "src" / "main" / "java",
                        source_dir.parent / "src" / "main" / "java",
                    ]

                    found_alternatives = []
                    for candidate in candidates:
                        if candidate.exists():
                            java_files = list(candidate.rglob("*.java"))
                            if java_files:
                                found_alternatives.append((candidate, len(java_files)))

                    if found_alternatives:
                        print(f"\n   💡 Detected Java sources nearby:")
                        for path, count in found_alternatives[:3]:  # Show max 3
                            print(f"      ✓ {path} ({count} .java files)")
                        print(f"\n   💡 Try: --source {found_alternatives[0][0]}")

                    print(
                        f"\n   Continuing with structural metrics only (loc=0, complexity=1)\n"
                    )
            except Exception as e:
                print(
                    f"⚠️  Warning: Could not analyze source code: {e}", file=sys.stderr
                )
                import traceback

                if getattr(args, "verbose", False):
                    traceback.print_exc()
        else:
            print(
                f"⚠️  Warning: Source directory not found: {source_dir}", file=sys.stderr
            )
    else:
        print("\n⚠️  Note: Running without source code analysis (--source not provided)")
        print("   Metrics affected: complexity=1, loc=0")
        print("   Use --source <path> to enable full code analysis\n")

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
