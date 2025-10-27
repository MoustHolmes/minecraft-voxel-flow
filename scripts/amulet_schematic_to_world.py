"""
Convert schematic to BlueMap-compatible world using Amulet.

This requires a template Minecraft world to work with.
To create a template:
1. Open Minecraft Java Edition
2. Create new world → Superflat → Create
3. Let it generate (just spawn in)
4. Close and copy the world folder to templates/minecraft_template/
"""

import sys
from pathlib import Path
import shutil
import amulet
from amulet.api.selection import SelectionBox

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def convert_schematic_to_world(
    schematic_path: str,
    output_world: str,
    template_world: str = "templates/minecraft_template",
    center_x: int = 0,
    center_y: int = 70,
    center_z: int = 0
):
    """
    Convert a schematic to a BlueMap-compatible Minecraft world.
    
    Args:
        schematic_path: Path to the schematic file
        output_world: Path to output world directory  
        template_world: Path to template Minecraft world
        center_x, center_y, center_z: Where to place the schematic
    """
    template_path = Path(template_world)
    if not template_path.exists():
        print(f"❌ Template world not found at: {template_path}")
        print()
        print("To create a template world:")
        print("1. Open Minecraft Java Edition")
        print("2. Create New World → Superflat → Create New World")
        print("3. Let it load (just spawn in)")
        print("4. Close Minecraft")
        print("5. Copy the world folder to templates/minecraft_template/")
        print()
        print("The template only needs to be created once.")
        return False
    
    try:
        print("=" * 70)
        print("Converting Schematic to Minecraft World (Using Amulet)")
        print("=" * 70)
        print()
        
        # Load schematic
        print(f"📦 Loading schematic: {Path(schematic_path).name}")
        schematic = amulet.load_level(schematic_path)
        bounds = schematic.bounds(schematic.dimensions[0])
        print(f"   Size: {bounds}")
        print()
        
        # Copy template world
        output_path = Path(output_world)
        if output_path.exists():
            print(f"🗑️  Removing existing world...")
            shutil.rmtree(output_path)
        
        print(f"📋 Copying template world...")
        shutil.copytree(template_path, output_path)
        print()
        
        # Load world
        print(f"🌍 Loading world...")
        world = amulet.load_level(str(output_path))
        print()
        
        # Paste schematic
        print(f"📍 Pasting schematic at ({center_x}, {center_y}, {center_z})...")
        
        # Get schematic dimension and selection
        schem_dim = schematic.dimensions[0]
        selection = bounds
        
        # Paste into world
        print("   Copying blocks...")
        world.paste(
            schematic,
            schem_dim,
            selection,
            "minecraft:overworld",
            (center_x, center_y, center_z),
            include_blocks=True,
            include_entities=False
        )
        
        print("💾 Saving world...")
        world.save()
        world.close()
        schematic.close()
        
        print()
        print("=" * 70)
        print("✅ World Created Successfully!")
        print("=" * 70)
        print()
        print(f"World location: {output_path.absolute()}")
        print()
        print("Next steps:")
        print("1. Start BlueMap:")
        print(f"   java -jar tools/bluemap/bluemap-cli.jar -w {output_path} -rw")
        print()
        print("2. Take screenshot:")
        print("   python scripts/test_bluemap_screenshot.py")
        print()
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert schematic to Minecraft world for BlueMap")
    parser.add_argument("schematic", help="Schematic file to convert")
    parser.add_argument("--output", default="bluemap_test_world", help="Output world directory")
    parser.add_argument("--template", default="templates/minecraft_template", help="Template world directory")
    parser.add_argument("--x", type=int, default=0, help="Center X coordinate")
    parser.add_argument("--y", type=int, default=70, help="Center Y coordinate")
    parser.add_argument("--z", type=int, default=0, help="Center Z coordinate")
    
    args = parser.parse_args()
    
    convert_schematic_to_world(
        args.schematic,
        args.output,
        args.template,
        args.x,
        args.y,
        args.z
    )
