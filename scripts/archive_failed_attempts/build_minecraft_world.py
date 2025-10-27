"""
Create a proper Minecraft Java Edition world from a schematic.

This creates a minimal but valid world that BlueMap can render.
"""

import sys
from pathlib import Path
import shutil
import struct
import gzip
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anvil import EmptyRegion, EmptyChunk, Block
from nbtlib.tag import Int, Long, Byte, String, Double, Compound
from nbtlib import File
import numpy as np
from minecraft_voxel_flow.loaders.schematic_loader import SchematicLoader


def create_level_dat(world_path: Path):
    """Create a minimal level.dat file."""
    
    level_dat = File({
        "": Compound({
            "Data": Compound({
                "version": Int(19133),
                "DataVersion": Int(3465),  # 1.20.1
                "LevelName": String("BlueMap Test"),
                "SpawnX": Int(0),
                "SpawnY": Int(64),
                "SpawnZ": Int(0),
                "Time": Long(0),
                "DayTime": Long(1000),
                "GameType": Int(1),  # Creative
                "MapFeatures": Byte(0),
                "generatorName": String("flat"),
                "generatorOptions": String(""),
                "generatorVersion": Int(1),
                "Difficulty": Byte(2),
                "DifficultyLocked": Byte(0),
                "BorderCenterX": Double(0.0),
                "BorderCenterZ": Double(0.0),
                "BorderSize": Double(60000000.0),
                "BorderSafeZone": Double(5.0),
                "BorderWarningBlocks": Double(5.0),
                "BorderWarningTime": Double(15.0),
                "BorderSizeLerpTarget": Double(60000000.0),
                "BorderSizeLerpTime": Long(0),
                "raining": Byte(0),
                "rainTime": Int(0),
                "thundering": Byte(0),
                "thunderTime": Int(0),
                "clearWeatherTime": Int(0),
                "initialized": Byte(1),
                "allowCommands": Byte(1),
            })
        })
    })
    
    level_dat_path = world_path / "level.dat"
    level_dat.save(str(level_dat_path), gzipped=True)
    print(f"✅ Created level.dat")


def create_world_from_schematic(
    schematic_path: str,
    world_path: str = "bluemap_test_world",
    center_x: int = 0,
    center_y: int = 70,
    center_z: int = 0
) -> bool:
    """Create a Minecraft world from a schematic.
    
    Args:
        schematic_path: Path to schematic
        world_path: Output world directory
        center_x, center_y, center_z: Where to place the schematic center
        
    Returns:
        True if successful
    """
    try:
        print("=" * 70)
        print("Creating Minecraft World from Schematic")
        print("=" * 70)
        print()
        
        # Load schematic
        print(f"📦 Loading: {Path(schematic_path).name}")
        loader = SchematicLoader()
        voxels, palette_reverse, palette = loader.load(schematic_path)
        
        print(f"   Size: {voxels.shape[0]} × {voxels.shape[1]} × {voxels.shape[2]}")
        print(f"   Blocks: {np.sum(voxels > 0):,}")
        print(f"   Block types: {len(palette_reverse)}")
        
        # Create world directory
        world_path = Path(world_path)
        if world_path.exists():
            print(f"🗑️  Removing existing world...")
            shutil.rmtree(world_path)
        
        world_path.mkdir(parents=True)
        (world_path / "region").mkdir()
        (world_path / "data").mkdir()
        
        print(f"🌍 Creating world at: {world_path}")
        
        # Create level.dat
        create_level_dat(world_path)
        
        # Calculate schematic placement
        start_x = center_x
        start_y = center_y
        start_z = center_z
        
        print(f"📍 Placing schematic at: ({start_x}, {start_y}, {start_z})")
        print()
        print("🔨 Building world (this may take a minute)...")
        
        # Create regions and chunks
        region_dict = {}  # (region_x, region_z) -> EmptyRegion
        
        block_count = 0
        for x in range(voxels.shape[0]):
            for y in range(voxels.shape[1]):
                for z in range(voxels.shape[2]):
                    block_id = voxels[x, y, z]
                    
                    # Skip air
                    if block_id == 0:
                        continue
                    
                    # World coordinates
                    world_x = start_x + x
                    world_y = start_y + y
                    world_z = start_z + z
                    
                    # Get block name
                    block_name = palette_reverse.get(block_id, "minecraft:stone")
                    
                    # Simplify block name for Anvil
                    if ":" in block_name:
                        block_name = block_name.split(":")[-1]
                    # Remove properties
                    if "[" in block_name:
                        block_name = block_name.split("[")[0]
                    
                    # Map to valid minecraft block
                    block_name = f"minecraft:{block_name}"
                    
                    # Get absolute chunk coordinates
                    abs_chunk_x = world_x // 16
                    abs_chunk_z = world_z // 16
                    
                    # Get region coordinates
                    region_x = abs_chunk_x // 32
                    region_z = abs_chunk_z // 32
                    
                    # Create region if needed
                    region_key = (region_x, region_z)
                    if region_key not in region_dict:
                        region_dict[region_key] = EmptyRegion(region_x, region_z)
                    
                    region = region_dict[region_key]
                    
                    # Get chunk coordinates within region (0-31)
                    chunk_x = abs_chunk_x % 32
                    chunk_z = abs_chunk_z % 32
                    
                    # Create chunk if needed
                    if region.get_chunk(chunk_x, chunk_z) is None:
                        chunk = EmptyChunk(abs_chunk_x, abs_chunk_z)
                        region.add_chunk(chunk)
                    
                    # Place block (chunk.set_block needs chunk-relative coordinates 0-15)
                    chunk = region.get_chunk(chunk_x, chunk_z)
                    
                    # Convert world coords to chunk-relative coords (0-15)
                    block_x = world_x % 16
                    block_z = world_z % 16
                    
                    try:
                        chunk.set_block(Block(block_name), block_x, world_y, block_z)
                        block_count += 1
                        
                        if block_count % 1000 == 0:
                            print(f"   Placed {block_count:,} blocks...", end="\r")
                    except Exception as e:
                        # Debug first error
                        if block_count == 0:
                            print(f"   First error: {e}")
                        pass
        
        print(f"   Placed {block_count:,} blocks total    ")
        print()
        
        # Save all regions
        print("💾 Saving regions...")
        region_path = world_path / "region"
        for (rx, rz), region in region_dict.items():
            filename = f"r.{rx}.{rz}.mca"
            region.save(str(region_path / filename))
        
        print(f"✅ Saved {len(region_dict)} region file(s)")
        
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
        print("   python scripts/take_bluemap_screenshot.py")
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
