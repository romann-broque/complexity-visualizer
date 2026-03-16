"""Command: run

Execute the full analysis pipeline (all-in-one command).
"""

from __future__ import annotations

import sys
from pathlib import Path
from argparse import Namespace

from complexity_visualizer.commands.generate_dots import cmd_generate_dots
from complexity_visualizer.commands.build_graph import cmd_build_graph
from complexity_visualizer.commands.convert import cmd_convert
from complexity_visualizer.commands.visualize import cmd_visualize
from complexity_visualizer.utils.auto_detect import find_dot_files


def cmd_run(args) -> int:
    """
    Execute full analysis pipeline.

    This orchestrates all steps:
    1. Generate .dot files (if needed)
    2. Build graph and compute metrics
    3. Convert to CodeCharta format
    4. Open visualization

    Args:
        args: Argparse namespace with:
            - path: Project path
            - source: Source code directory (optional)
            - output: Output directory
            - include_prefix: Package prefixes to filter
            - project: Project name
            - skip_dots: Skip .dot generation
            - no_open: Don't open browser

    Returns:
        Exit code (0 = success, 1 = error)
    """
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"❌ Error: Project path not found: {project_path}", file=sys.stderr)
        return 1

    print("=" * 60)
    print(f"🚀 Running full analysis pipeline: {project_path.name}")
    print("=" * 60)

    # Determine output directory
    output_dir = Path(args.output).resolve() if args.output else project_path / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine project name
    project_name = args.project if args.project else project_path.name

    # Step 1: Generate .dot files (unless skipped)
    dot_dir = None
    if not args.skip_dots:
        print("\n📍 Step 1/4: Generate .dot files")
        print("-" * 60)

        # Check if .dot files already exist
        existing_dots = find_dot_files(project_path)
        if existing_dots:
            print(f"   Found existing .dot files: {existing_dots}")
            use_existing = input("   Use existing .dot files? [Y/n]: ").lower()
            if use_existing in ("", "y", "yes"):
                dot_dir = existing_dots
                print("   Using existing .dot files")
            else:
                dot_dir = None

        if not dot_dir:
            # Generate new .dot files
            dot_output = project_path / "from" / project_name

            generate_args = Namespace(
                path=str(project_path),
                output=str(dot_output),
                classes=None,  # Auto-detect
                include_prefix=args.include_prefix,
            )

            result = cmd_generate_dots(generate_args)
            if result != 0:
                print("❌ Failed at step 1: generate-dots", file=sys.stderr)
                return result

            dot_dir = dot_output
    else:
        print("\n📍 Step 1/4: Generate .dot files (SKIPPED)")
        print("-" * 60)
        # Find existing .dot files
        dot_dir = find_dot_files(project_path)
        if not dot_dir:
            print(
                "❌ Error: No .dot files found. Remove --skip-dots to generate them.",
                file=sys.stderr,
            )
            return 1
        print(f"   Using existing .dot files: {dot_dir}")

    # Step 2: Build graph and compute metrics
    print("\n📍 Step 2/4: Build graph and compute metrics")
    print("-" * 60)

    build_args = Namespace(
        dot_dir=str(dot_dir),
        source=args.source,
        output=str(output_dir),
        include_prefix=args.include_prefix,
        project=project_name,
    )

    result = cmd_build_graph(build_args)
    if result != 0:
        print("❌ Failed at step 2: build-graph", file=sys.stderr)
        return result

    metrics_file = output_dir / "metrics.json"

    # Step 3: Convert to CodeCharta format
    print("\n📍 Step 3/4: Convert to CodeCharta format")
    print("-" * 60)

    convert_args = Namespace(
        input=str(metrics_file),
        output=str(output_dir / "codecharta.cc.json"),
        project=project_name,
    )

    result = cmd_convert(convert_args)
    if result != 0:
        print("❌ Failed at step 3: convert", file=sys.stderr)
        return result

    cc_file = output_dir / "codecharta.cc.json"

    # Step 4: Visualize (unless disabled)
    if not args.no_open:
        print("\n📍 Step 4/4: Open visualization")
        print("-" * 60)

        visualize_args = Namespace(file=str(cc_file), no_open=False)

        result = cmd_visualize(visualize_args)
        if result != 0:
            print("⚠️  Warning: Could not open visualization", file=sys.stderr)
            # Don't fail the whole pipeline for this
    else:
        print("\n📍 Step 4/4: Open visualization (SKIPPED)")
        print("-" * 60)
        print(f"   File ready: {cc_file}")
        print(f"   Open manually with: complexity-viz visualize {cc_file}")

    # Success summary
    print("\n" + "=" * 60)
    print("✅ Pipeline completed successfully!")
    print("=" * 60)
    print(f"\n📁 Generated files:")
    print(f"   .dot files: {dot_dir}")
    print(f"   Metrics:    {metrics_file}")
    print(f"   CodeCharta: {cc_file}")

    return 0
