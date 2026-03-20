"""Command: visualize

Open CodeCharta visualization with the generated file.
"""

from __future__ import annotations

import sys
from pathlib import Path

from complexity_visualizer.utils.browser_opener import open_in_codecharta


def cmd_visualize(args) -> int:
    """
    Open CodeCharta visualization.

    Args:
        args: Argparse namespace with:
            - file: Path to .cc.json file
            - no_open: Don't open browser (just show instructions)

    Returns:
        Exit code (0 = success, 1 = error)
    """
    file_path = Path(args.file).resolve()

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        print("   Run 'complexity-viz convert' first", file=sys.stderr)
        return 1

    # Check file extension
    if not file_path.suffix == ".json":
        print(
            f"⚠️  Warning: Expected .json file, got {file_path.suffix}", file=sys.stderr
        )

    # Open in CodeCharta
    auto_open = not args.no_open if hasattr(args, "no_open") else True
    open_in_codecharta(str(file_path), auto_open=auto_open)

    return 0
