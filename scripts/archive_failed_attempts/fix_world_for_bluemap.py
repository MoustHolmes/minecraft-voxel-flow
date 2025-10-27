"""
Fix the anvil-generated world to be BlueMap compatible using Amulet.
This loads the world with Amulet and re-saves it, which should add proper metadata.
"""

import sys
from pathlib import Path
import amulet

def fix_world(world_path: str):
    """
    Load and re-save world with Amulet to add proper chunk metadata.
    """
    try:
        print("=" * 70)
        print("Fixing World for BlueMap")
        print("=" * 70)
        print()
        
        world_path = Path(world_path)
        if not world_path.exists():
            print(f"❌ World not found: {world_path}")
            return False
        
        print(f"🌍 Loading world: {world_path}")
        world = amulet.load_level(str(world_path))
        
        print(f"   Dimensions: {world.dimensions}")
        
        # Get all chunks
        dimension = "minecraft:overworld"
        chunks = list(world.all_chunk_coords(dimension))
        print(f"   Found {len(chunks)} chunks")
        
        if len(chunks) == 0:
            print("   No chunks found - world appears empty")
            world.close()
            return False
        
        # Touch each chunk to mark it as modified
        print(f"🔧 Refreshing {len(chunks)} chunks...")
        for i, (cx, cz) in enumerate(chunks):
            try:
                chunk = world.get_chunk(cx, cz, dimension)
                # Mark chunk as changed
                world.put_chunk(chunk, dimension)
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(chunks)} chunks...", end="\r")
            except Exception as e:
                print(f"   Warning: Could not process chunk ({cx}, {cz}): {e}")
        
        print(f"   Processed {len(chunks)}/{len(chunks)} chunks    ")
        print()
        
        print("💾 Saving world...")
        world.save()
        world.close()
        
        print()
        print("=" * 70)
        print("✅ World Fixed!")
        print("=" * 70)
        print()
        print("Now try BlueMap:")
        print(f"  java -jar tools/bluemap/bluemap-cli.jar -w {world_path} -rw")
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
    parser.add_argument("world", help="World directory to fix")
    
    args = parser.parse_args()
    
    fix_world(args.world)
