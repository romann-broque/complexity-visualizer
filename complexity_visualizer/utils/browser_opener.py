"""Utility to open CodeCharta visualization in browser."""

import platform
import subprocess
from pathlib import Path


CODECHARTA_URL = "https://codecharta.com/visualization/app/index.html"


def open_in_codecharta(cc_file_path: str, auto_open: bool = True) -> None:
    """
    Display instructions and optionally open CodeCharta in browser.

    Args:
        cc_file_path: Path to the generated .cc.json file
        auto_open: If True, attempt to open browser automatically
    """
    abs_path = Path(cc_file_path).resolve()

    print(f"\n{'=' * 60}")
    print("🎨 CodeCharta Visualization Ready!")
    print(f"{'=' * 60}")
    print(f"\n🌐 Open in browser:")
    print(f"   {CODECHARTA_URL}")
    print(f"\n📂 Load this file:")
    print(f"   {abs_path}")

    if auto_open:
        opened = _try_open_browser(CODECHARTA_URL)
        if opened:
            print("\n✅ Browser opened automatically!")
        else:
            print("\n⚠️  Could not auto-open browser. Please open manually.")

    print(f"\n📖 How to visualize:")
    print("   1. Open the URL above in your browser")
    print("   2. Click 'Load File' or drag & drop the .cc.json file")
    print("   3. Explore your codebase in 3D!")
    print(f"\n💡 What you'll see:")
    print("   • Buildings = Classes (height = complexity)")
    print("   • Districts = Packages")
    print("   • Red/Orange = Hotspots requiring attention")
    print(f"\n{'=' * 60}\n")


def _try_open_browser(url: str) -> bool:
    """
    Try to open URL in default browser.

    Returns:
        True if browser opened successfully, False otherwise
    """
    try:
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.run(["open", url], check=True, capture_output=True)
            return True
        elif system == "Linux":
            subprocess.run(["xdg-open", url], check=True, capture_output=True)
            return True
        elif system == "Windows":
            subprocess.run(["start", url], shell=True, check=True, capture_output=True)
            return True
        else:
            return False
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False
