"""
Convert Schematic to Minecraft World for BlueMap

BlueMap renders Minecraft worlds, not schematics directly.
This script converts schematics to minimal Minecraft worlds that BlueMap can render.
"""

import sys
from pathlib import Path
import shutil
import tempfile
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import amulet
    from amulet.api.level import World
    from amulet.api.data_types import Dimension
except ImportError:
    print("Error: amulet-core required. Install with: pip install amulet-core")
    sys.exit(1)


def convert_schematic_to_world(
    schematic_path: str,
    output_world_dir: str,
    spawn_offset: Tuple[int, int, int] = (0, 64, 0)
) -> bool:
    """Convert a schematic file to a minimal Minecraft world.
    
    Args:
        schematic_path: Path to the schematic file
        output_world_dir: Directory to create the world in
        spawn_offset: (x, y, z) offset to place the schematic
        
    Returns:
        True if successful
    """
    try:
        print(f"Loading schematic: {schematic_path}")
        
        # Load the schematic
        schematic = amulet.load_level(schematic_path)
        
        # Create a new world
        print(f"Creating world: {output_world_dir}")
        output_path = Path(output_world_dir)
        
        # If world exists, remove it
        if output_path.exists():
            shutil.rmtree(output_path)
        
        # Create minimal world structure
        output_path.mkdir(parents=True)
        
        # Get schematic dimensions
        selection = schematic.bounds(Dimension.overworld)
        print(f"Schematic bounds: {selection}")
        
        # Create a basic Minecraft world
        # We'll use Amulet to create a flat world and paste the schematic
        
        # For now, just copy the schematic structure
        # This is simplified - a full implementation would create proper world files
        
        print("⚠️  Note: Full world conversion requires creating proper Minecraft world structure")
        print("This is a placeholder. BlueMap expects a complete Minecraft world directory.")
        
        return False
        
    except Exception as e:
        print(f"Error converting schematic: {e}")
        return False


def render_schematic_with_bluemap(
    schematic_path: str,
    output_image: str,
    bluemap_jar: str = "tools/bluemap/bluemap-cli.jar",
    resolution: Tuple[int, int] = (1920, 1080)
) -> bool:
    """Render a schematic using BlueMap (full pipeline).
    
    Args:
        schematic_path: Path to schematic
        output_image: Output image path
        bluemap_jar: Path to BlueMap CLI jar
        resolution: Image resolution
        
    Returns:
        True if successful
    """
    import subprocess
    import json
    
    # Create temporary world
    with tempfile.TemporaryDirectory() as temp_dir:
        world_dir = Path(temp_dir) / "world"
        
        # Convert schematic to world
        if not convert_schematic_to_world(schematic_path, str(world_dir)):
            print("❌ Failed to convert schematic to world")
            return False
        
        # Create BlueMap config
        config = {
            "accept-download": True,
            "data": str(Path(temp_dir) / "bluemap_data"),
            "maps": [{
                "id": "schematic",
                "name": "Schematic",
                "world": str(world_dir),
                "dimension": "minecraft:overworld"
            }],
            "webserver": {
                "enabled": True,
                "port": 8100
            }
        }
        
        config_path = Path(temp_dir) / "bluemap.conf"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run BlueMap
        try:
            cmd = ["java", "-jar", str(bluemap_jar), "-c", str(config_path), "-r"]
            
            print(f"Running BlueMap render...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"BlueMap error: {result.stderr}")
                return False
            
            print("✅ BlueMap render complete")
            
            # TODO: Extract rendered tiles and combine into single image
            # This requires implementing tile stitching
            
            return True
            
        except Exception as e:
            print(f"Error running BlueMap: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert schematics to worlds for BlueMap rendering"
    )
    parser.add_argument("schematic", help="Path to schematic file")
    parser.add_argument("--output", "-o", help="Output world directory")
    
    args = parser.parse_args()
    
    if not args.output:
        args.output = f"temp_world_{Path(args.schematic).stem}"
    
    success = convert_schematic_to_world(args.schematic, args.output)
    
    if success:
        print(f"\n✅ World created: {args.output}")
        print("\nTo render with BlueMap:")
        print(f"  java -jar tools/bluemap/bluemap-cli.jar -w {args.output} -r")
    else:
        print("\n❌ Conversion failed")
        print("\nNote: Direct schematic to BlueMap rendering is complex.")
        print("Consider using the matplotlib-based preview generator instead:")
        print("  python scripts/generate_previews.py")
