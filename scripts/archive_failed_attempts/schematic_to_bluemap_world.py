"""
Create a proper Minecraft world from a schematic using Amulet.
This creates a world that BlueMap can actually render.
"""

import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import amulet
from amulet.api.block import Block
from amulet.utils import block_coords_to_chunk_coords
from minecraft_voxel_flow.loaders.schematic_loader import SchematicLoader
import numpy as np


def create_world_from_schematic(
    schematic_path: str,
    output_world: str,
    center_x: int = 0,
    center_y: int = 70,
    center_z: int = 0
):
    """
    Create a Minecraft world from a schematic using Amulet.
    
    Args:
        schematic_path: Path to the schematic file
        output_world: Path to output world directory
        center_x, center_y, center_z: Where to place the schematic center
    """
    try:
        print("=" * 70)
        print("Creating Minecraft World from Schematic (Using Amulet)")
        print("=" * 70)
        print()
        
        # Load schematic
        print(f"📦 Loading: {Path(schematic_path).name}")
        loader = SchematicLoader()
        voxels, palette_reverse, palette = loader.load(schematic_path)
        
        print(f"   Size: {voxels.shape[0]} × {voxels.shape[1]} × {voxels.shape[2]}")
        print(f"   Blocks: {np.count_nonzero(voxels):,}")
        print(f"   Block types: {len(palette)}")
        print()
        
        # Remove existing world
        world_path = Path(output_world)
        if world_path.exists():
            print("🗑️  Removing existing world...")
            shutil.rmtree(world_path)
        
        # Create new world using Amulet
        print(f"🌍 Creating world at: {world_path}")
        
        # Create a new world with Amulet
        # Use 'java' platform for Minecraft Java Edition
        level = amulet.level.formats.anvil_world.AnvilFormat(str(world_path))
        level.open()
        
        # Calculate starting position (center the schematic)
        start_x = center_x - voxels.shape[0] // 2
        start_y = center_y
        start_z = center_z - voxels.shape[2] // 2
        
        print(f"📍 Placing schematic at: ({start_x}, {start_y}, {start_z})")
        print()
        print("🔨 Building world (this may take a minute)...")
        
        # Track chunks we've modified
        modified_chunks = set()
        block_count = 0
        
        # Place blocks
        for x in range(voxels.shape[0]):
            for y in range(voxels.shape[1]):
                for z in range(voxels.shape[2]):
                    block_id = voxels[x, y, z]
                    
                    # Skip air
                    if block_id == 0:
                        continue
                    
                    # Get block name
                    block_name = palette_reverse[block_id]
                    
                    # Convert universal name to java format
                    # Remove "universal_minecraft:" prefix if present
                    if block_name.startswith("universal_minecraft:"):
                        block_name = block_name.replace("universal_minecraft:", "minecraft:")
                    elif not block_name.startswith("minecraft:"):
                        block_name = f"minecraft:{block_name}"
                    
                    # Calculate world position
                    world_x = start_x + x
                    world_y = start_y + y
                    world_z = start_z + z
                    
                    # Create Amulet block
                    try:
                        amulet_block = Block("java", block_name.split(":")[1])
                        
                        # Set block in world
                        level.set_version_block(
                            world_x, world_y, world_z,
                            "minecraft:overworld",
                            ("java", (1, 20, 1)),
                            amulet_block
                        )
                        
                        # Track modified chunk
                        chunk_coords = block_coords_to_chunk_coords(world_x, world_z)
                        modified_chunks.add(chunk_coords)
                        
                        block_count += 1
                        
                        if block_count % 1000 == 0:
                            print(f"   Placed {block_count:,} blocks...", end="\r")
                            
                    except Exception as e:
                        if block_count == 0:
                            print(f"   Warning: Could not place block {block_name}: {e}")
        
        print(f"   Placed {block_count:,} blocks total    ")
        print()
        
        # Save modified chunks
        print(f"💾 Saving {len(modified_chunks)} modified chunks...")
        for chunk_x, chunk_z in modified_chunks:
            level.save_chunk(chunk_x, chunk_z, "minecraft:overworld")
        
        level.close()
        
        print("✅ Saved world")
        print()
        print("=" * 70)
        print("✅ World Created Successfully!")
        print("=" * 70)
        print()
        print(f"World location: {world_path.absolute()}")
        print(f"Blocks placed: {block_count:,}")
        print()
        print("Next steps:")
        print("1. Start BlueMap:")
        print(f"   java -jar tools/bluemap/bluemap-cli.jar -w {world_path} -rw")
        print()
        print("2. Wait for it to render and start web server")
        print()
        print("3. Take screenshot:")
        print("   python scripts/bluemap_screenshot_demo.py")
        print()
        print("4. Or visit in browser:")
        print("   open http://localhost:8100")
        print()
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("schematic", help="Schematic file to convert")
    parser.add_argument("--output", default="bluemap_test_world", help="Output world directory")
    parser.add_argument("--x", type=int, default=0, help="Center X coordinate")
    parser.add_argument("--y", type=int, default=70, help="Center Y coordinate")
    parser.add_argument("--z", type=int, default=0, help="Center Z coordinate")
    
    args = parser.parse_args()
    
    create_world_from_schematic(
        args.schematic,
        args.output,
        args.x,
        args.y,
        args.z
    )
