"""Command: generate-dots

Generate .dot dependency files using jdeps on compiled Java classes.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from complexity_visualizer.utils.auto_detect import (
    detect_project_type,
    find_compiled_classes,
    get_compile_command,
    resolve_include_prefixes,
)
from complexity_visualizer.utils.jdeps_runner import run_jdeps, check_jdeps_available


def cmd_generate_dots(args) -> int:
    """
    Generate .dot files using jdeps.

    Args:
        args: Argparse namespace with:
            - path: Project path
            - output: Output directory for .dot files
            - classes: Compiled classes directory (optional)
            - include_prefix: Package prefixes to filter

    Returns:
        Exit code (0 = success, 1 = error)
    """
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"❌ Error: Project path not found: {project_path}", file=sys.stderr)
        return 1

    # Resolve package filtering (always applies filtering)
    include_prefixes = resolve_include_prefixes(args.include_prefix, project_path)

    print(f"🔍 Generating .dot files for: {project_path.name}")

    if args.include_prefix:
        # User explicitly provided prefixes
        print(f"   Filtering packages: {', '.join(include_prefixes)}")
    elif include_prefixes:
        # Auto-detected or default prefixes
        print(f"   Auto-detected filtering: {', '.join(include_prefixes)}")
    else:
        # No filtering (analyze everything)
        print("   ⚠️  No package filtering applied (will analyze ALL dependencies)")
        print("   Tip: Use --include-prefix to focus analysis")

    # Check if jdeps is available
    if not check_jdeps_available():
        print("❌ Error: jdeps not found", file=sys.stderr)
        print("   Please install Java JDK >= 11", file=sys.stderr)
        print("   Verify with: java -version", file=sys.stderr)
        return 1

    # Detect project type
    print("   Auto-detecting project structure...")
    project_info = detect_project_type(project_path)
    print(f"   Project type: {project_info['type']}")

    # Find compiled classes
    if args.classes:
        classes_dir = Path(args.classes).resolve()
    else:
        classes_dir = find_compiled_classes(project_path)

    if not classes_dir:
        print("❌ Error: No compiled classes found", file=sys.stderr)
        print("   Please compile your project first:", file=sys.stderr)
        compile_cmd = get_compile_command(project_info["type"])
        if compile_cmd:
            print(f"   Run: {compile_cmd}", file=sys.stderr)
        else:
            print("   Compile your project using your build tool", file=sys.stderr)
        print(
            "\n   Or specify classes directory with: --classes <dir>", file=sys.stderr
        )
        return 1

    print(f"   Classes directory: {classes_dir}")

    # Determine output directory
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = project_path / "from" / project_path.name

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   Output directory: {output_dir}")

    # Run jdeps
    print("\n📊 Running jdeps...")
    result = run_jdeps(
        str(classes_dir),
        str(output_dir),
        prefixes=include_prefixes,
        verbose=args.verbose if hasattr(args, "verbose") else False,
    )

    # Display results
    if result["success"]:
        print(f"✅ Generated {result['files_generated']} .dot files")
        print(f"   Location: {output_dir}")

        if result["errors"]:
            print("\n⚠️  Warnings:")
            for error in result["errors"]:
                print(f"   {error}")

        return 0
    else:
        print(f"❌ Failed to generate .dot files", file=sys.stderr)
        for error in result["errors"]:
            print(f"   {error}", file=sys.stderr)
        return 1
