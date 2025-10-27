"""
Launch Amulet Editor to view and screenshot Minecraft schematics.

This script opens a schematic file in Amulet Editor's GUI, allowing you to:
- View the schematic in 3D
- Take screenshots
- Export renders
"""

import sys
from pathlib import Path
import subprocess


def launch_amulet(schematic_path: str):
    """Launch Amulet Editor with a schematic file.
    
    Args:
        schematic_path: Path to the schematic file to open
    """
    schematic_path = Path(schematic_path)
    
    if not schematic_path.exists():
        print(f"❌ Error: Schematic file not found: {schematic_path}")
        return
    
    print(f"Opening {schematic_path.name} in Amulet Editor...")
    print("\nNote: Amulet Editor will open in a new window.")
    print("You can:")
    print("  - Navigate in 3D view")
    print("  - Take screenshots (usually Ctrl+Shift+S or menu option)")
    print("  - Export renders")
    print("  - Close the window when done\n")
    
    try:
        # Try to import and run Amulet GUI
        from amulet_editor import main as amulet_main
        
        # Run Amulet with the schematic file
        sys.argv = ['amulet_editor', str(schematic_path)]
        amulet_main()
        
    except ImportError:
        print("❌ Amulet Editor not installed.")
        print("\nInstall with: pip install amulet-editor")
        print("\nAlternatively, you can:")
        print("  1. Download Amulet Editor: https://www.amuletmc.com/")
        print("  2. Run it manually and open the schematic file")
        
    except Exception as e:
        print(f"❌ Error launching Amulet: {e}")
        print("\nTrying alternative method...")
        
        # Try command line launch
        try:
            subprocess.run(['amulet', str(schematic_path)])
        except FileNotFoundError:
            print("❌ Could not find amulet command.")
            print("\nPlease install Amulet Editor:")
            print("  pip install amulet-editor")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        schematic_file = sys.argv[1]
    else:
        # Default: open first schematic in data/schematics
        schematics_dir = Path("../data/schematics")
        schematic_files = list(schematics_dir.glob("*.schematic"))
        
        if schematic_files:
            schematic_file = str(schematic_files[0])
            print(f"No file specified, using: {schematic_file}")
        else:
            print("❌ No schematic files found in data/schematics")
            print("\nUsage: python view_schematic.py <path_to_schematic>")
            sys.exit(1)
    
    launch_amulet(schematic_file)
