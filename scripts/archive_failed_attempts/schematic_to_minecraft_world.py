"""
Convert a schematic to a proper Minecraft world that BlueMap can render.

Uses Amulet to create a real Minecraft world with proper structure.
"""

import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import amulet
from amulet.api.level import World
from amulet.api.data_types import Dimension, VersionNumberTuple
from amulet.level.formats.anvil_world import AnvilFormat
import amulet_nbt


def create_minecraft_world_from_schematic(
    schematic_path: str,
    output_world_path: str = "bluemap_test_world",
    offset_y: int = 64
) -> bool:
    """Convert a schematic to a proper Minecraft world.
    
    Args:
        schematic_path: Path to schematic file
        output_world_path: Where to create the world
        offset_y: Y position to place the schematic
        
    Returns:
        True if successful
    """
    try:
        print(f"📦 Loading schematic: {schematic_path}")
        schematic = amulet.load_level(schematic_path)
        
        # Get schematic bounds
        dimension = schematic.dimensions[0]
        bounds = schematic.bounds(dimension)
        
        size_x = bounds.max_x - bounds.min_x
        size_y = bounds.max_y - bounds.min_y
        size_z = bounds.max_z - bounds.min_z
        
        print(f"   Size: {size_x} × {size_y} × {size_z}")
        print(f"   Bounds: X[{bounds.min_x}:{bounds.max_x}] Y[{bounds.min_y}:{bounds.max_y}] Z[{bounds.min_z}:{bounds.max_z}]")
        
        output_path = Path(output_world_path)
        
        # Remove existing world
        if output_path.exists():
            print(f"🗑️  Removing existing world...")
            shutil.rmtree(output_path)
        
        print(f"🌍 Creating new Minecraft world...")
        
        # Create a new world using Amulet
        # This creates a proper Java Edition world structure
        world = amulet.load_level(
            str(output_path),
            create=True
        )
        
        print(f"📋 Copying blocks from schematic to world...")
        
        # Copy all blocks from schematic to world
        block_count = 0
        for x in range(bounds.min_x, bounds.max_x):
            for y in range(bounds.min_y, bounds.max_y):
                for z in range(bounds.min_z, bounds.max_z):
                    # Get block from schematic
                    block, block_entity = schematic.get_version_block(
                        x, y, z,
                        dimension,
                        ("java", (1, 20, 1))
                    )
                    
                    # Place in world at offset position
                    world_x = x - bounds.min_x
                    world_y = y - bounds.min_y + offset_y
                    world_z = z - bounds.min_z
                    
                    world.set_version_block(
                        world_x, world_y, world_z,
                        "minecraft:overworld",
                        ("java", (1, 20, 1)),
                        block,
                        block_entity
                    )
                    
                    block_count += 1
                    
                    if block_count % 10000 == 0:
                        print(f"   Copied {block_count:,} blocks...")
        
        print(f"✅ Copied {block_count:,} blocks total")
        
        # Save the world
        print(f"💾 Saving world...")
        world.save()
        world.close()
        
        print(f"✅ World created at: {output_path}")
        print(f"   World structure:")
        for item in sorted(output_path.iterdir()):
            print(f"   - {item.name}")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert schematic to Minecraft world for BlueMap"
    )
    parser.add_argument(
        "schematic",
        help="Path to schematic file"
    )
    parser.add_argument(
        "--output",
        default="bluemap_test_world",
        help="Output world directory"
    )
    parser.add_argument(
        "--offset-y",
        type=int,
        default=64,
        help="Y position to place schematic"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Schematic to Minecraft World Converter")
    print("=" * 70)
    print()
    
    success = create_minecraft_world_from_schematic(
        args.schematic,
        args.output,
        args.offset_y
    )
    
    if success:
        print()
        print("=" * 70)
        print("✅ Success! Next steps:")
        print("=" * 70)
        print()
        print("1. Start BlueMap server:")
        print(f"   java -jar tools/bluemap/bluemap-cli.jar -w {args.output} -rw")
        print()
        print("2. In another terminal, take screenshot:")
        print("   python scripts/bluemap_screenshot_demo.py")
        print()
        print("3. Or visit in browser:")
        print("   open http://localhost:8100")
    else:
        print()
        print("❌ World creation failed")
