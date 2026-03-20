"""Command: convert

Convert metrics file to CodeCharta visualization format.
"""

from __future__ import annotations

import sys
from pathlib import Path

from complexity_visualizer.exporters.codecharta import convert_to_codecharta


def cmd_convert(args) -> int:
    """
    Convert metrics to CodeCharta format.

    Args:
        args: Argparse namespace with:
            - input: Input file (metrics.json or graph.json)
            - output: Output file path
            - project: Project name for metadata

    Returns:
        Exit code (0 = success, 1 = error)
    """
    input_path = Path(args.input).resolve()

    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    # Determine output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        # Default: same directory as input, .cc.json extension
        output_path = input_path.parent / "codecharta.cc.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine project name
    project_name = args.project
    if not project_name:
        # Try to infer from input file location
        project_name = input_path.parent.name
        if project_name in ("dist", "output", "from"):
            project_name = input_path.parent.parent.name

    print(f"🎨 Converting to CodeCharta format...")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Project: {project_name}")

    try:
        convert_to_codecharta(str(input_path), str(output_path), project_name)
    except Exception as e:
        print(f"❌ Error converting file: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    print(f"✅ CodeCharta file created successfully")
    print(f"\n📁 Output:")
    print(f"   {output_path}")
    print(f"\n💡 Next step:")
    print(f"   complexity-viz visualize {output_path}")

    return 0
