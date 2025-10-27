"""
Download BlueMap CLI

Simple script to download the latest BlueMap CLI jar file.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bluemap_screenshots import download_bluemap_cli


if __name__ == "__main__":
    print("=" * 60)
    print("BlueMap CLI Downloader")
    print("=" * 60)
    print()
    
    output_path = "tools/bluemap/bluemap-cli.jar"
    
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    success = download_bluemap_cli(output_path)
    
    if success:
        print("\n✅ Installation complete!")
        print("\nNext steps:")
        print("1. Test with: python scripts/bluemap_screenshots.py")
        print("2. Or use in notebook: notebooks/bluemap_screenshots.ipynb")
    else:
        print("\n❌ Installation failed")
        print("\nManual installation:")
        print("1. Visit: https://github.com/BlueMap-Minecraft/BlueMap/releases")
        print(f"2. Download the CLI jar file")
        print(f"3. Save to: {output_path}")
