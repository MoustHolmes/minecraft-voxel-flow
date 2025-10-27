#!/usr/bin/env python3
"""
Paste a schematic into a real Minecraft world and render with Chunky.

This script:
1. Loads a real Minecraft world (not Amulet-created)
2. Pastes a schematic into it at a specific location
3. Calculates the chunks occupied by the schematic
4. Generates a Chunky scene with proper camera and chunk list
5. Renders the scene
"""

import os
import sys
import argparse
import logging
import shutil
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.rendering import (
    load_schematic,
    get_schematic_bounds,
    get_chunks_for_bounds,
    calculate_camera_parameters,
    ISOMETRIC_VECTORS,
    generate_scene_file,
    render_scene_with_chunky
)
import amulet
from amulet.api.selection import SelectionBox

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def paste_schematic_into_world(world_path: str, schematic_path: str, paste_location: tuple) -> SelectionBox:
    """
    Paste a schematic into an existing real Minecraft world.
    
    Args:
        world_path: Path to the real Minecraft world
        schematic_path: Path to the schematic file
        paste_location: (x, y, z) tuple for where to paste
        
    Returns:
        SelectionBox of the pasted schematic in world coordinates
    """
    logger.info(f"Loading world: {world_path}")
    world = amulet.load_level(world_path)
    
    logger.info(f"Loading schematic: {schematic_path}")
    schematic = load_schematic(schematic_path)
    schematic_bounds = get_schematic_bounds(schematic)
    
    logger.info(f"Schematic size: ({schematic_bounds.size_x}, {schematic_bounds.size_y}, {schematic_bounds.size_z})")
    logger.info(f"Pasting at location: {paste_location}")
    
    # Calculate world bounds for the pasted schematic
    paste_x, paste_y, paste_z = paste_location
    world_bounds = SelectionBox(
        (paste_x, paste_y, paste_z),
        (paste_x + schematic_bounds.size_x, 
         paste_y + schematic_bounds.size_y, 
         paste_z + schematic_bounds.size_z)
    )
    
    # Paste the schematic block by block
    logger.info("Pasting blocks...")
    blocks_pasted = 0
    chunks_modified = set()
    
    for x in range(schematic_bounds.min_x, schematic_bounds.max_x):
        for y in range(schematic_bounds.min_y, schematic_bounds.max_y):
            for z in range(schematic_bounds.min_z, schematic_bounds.max_z):
                try:
                    # Get block from schematic
                    block = schematic.get_block(x, y, z, "minecraft:overworld")
                    
                    # Skip air blocks to preserve existing world
                    if block.base_name == "air":
                        continue
                    
                    # Paste to world at offset location
                    world_x = paste_x + (x - schematic_bounds.min_x)
                    world_y = paste_y + (y - schematic_bounds.min_y)
                    world_z = paste_z + (z - schematic_bounds.min_z)
                    
                    world.set_version_block(
                        world_x, world_y, world_z,
                        "minecraft:overworld",
                        ("java", (1, 20, 1)),
                        block
                    )
                    
                    blocks_pasted += 1
                    # Track which chunks we modified
                    chunk_x = world_x // 16
                    chunk_z = world_z // 16
                    chunks_modified.add((chunk_x, chunk_z))
                    
                except Exception as e:
                    # Skip errors for individual blocks
                    pass
    
    logger.info(f"Pasted {blocks_pasted} blocks")
    logger.info(f"Modified {len(chunks_modified)} chunks: {sorted(chunks_modified)}")
    
    # CRITICAL: Mark all modified chunks as changed so they get saved
    logger.info("Marking chunks as changed...")
    for chunk_x, chunk_z in chunks_modified:
        try:
            chunk = world.get_chunk(chunk_x, chunk_z, "minecraft:overworld")
            chunk.changed = True
            logger.info(f"  Marked chunk ({chunk_x}, {chunk_z}) as changed")
        except Exception as e:
            logger.warning(f"  Failed to mark chunk ({chunk_x}, {chunk_z}): {e}")
    
    logger.info("Saving world...")
    world.save()
    world.close()
    schematic.close()
    
    logger.info(f"✓ Schematic pasted successfully")
    logger.info(f"  World bounds: {world_bounds.min} to {world_bounds.max}")
    
    return world_bounds


def main():
    parser = argparse.ArgumentParser(
        description="Paste a schematic into a real Minecraft world and render it"
    )
    parser.add_argument(
        "schematic",
        help="Path to the schematic file"
    )
    parser.add_argument(
        "--world",
        default="./data/world_test_file/void",
        help="Path to the real Minecraft world"
    )
    parser.add_argument(
        "--location",
        default="0,64,0",
        help="Paste location as x,y,z (default: 0,64,0)"
    )
    parser.add_argument(
        "--output",
        default="./schematic_render.png",
        help="Output image path"
    )
    parser.add_argument(
        "--chunky_path",
        default="./tools/chunky/ChunkyLauncher.jar",
        help="Path to ChunkyLauncher.jar"
    )
    parser.add_argument(
        "--spp",
        type=int,
        default=100,
        help="Samples per pixel for rendering"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of world before pasting"
    )
    parser.add_argument(
        "--camera-angle",
        type=float,
        default=45.0,
        help="Camera angle in degrees (0=East, 90=South, 180=West, 270=North). Default: 45 (Northeast)"
    )
    parser.add_argument(
        "--camera-distance",
        type=float,
        default=42.0,
        help="Camera distance from structure center in blocks. Default: 42"
    )
    parser.add_argument(
        "--camera-elevation",
        type=float,
        default=15.0,
        help="Camera elevation above structure center in blocks. Default: 15"
    )
    parser.add_argument(
        "--camera-pitch",
        type=float,
        default=-20.0,
        help="Camera pitch angle in degrees (negative=down, positive=up). Default: -20"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only calculate camera and chunk information without modifying the world or rendering"
    )
    
    args = parser.parse_args()
    
    # Parse paste location
    try:
        paste_x, paste_y, paste_z = map(int, args.location.split(','))
        paste_location = (paste_x, paste_y, paste_z)
    except:
        logger.error(f"Invalid location format: {args.location}. Use x,y,z format.")
        sys.exit(1)
    
    # Validate inputs
    if not os.path.exists(args.schematic):
        logger.error(f"Schematic not found: {args.schematic}")
        sys.exit(1)
    
    if not os.path.exists(args.world):
        logger.error(f"World not found: {args.world}")
        sys.exit(1)
    
    # Backup world if requested
    if args.backup:
        backup_path = f"{args.world}_backup"
        logger.info(f"Creating backup: {backup_path}")
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(args.world, backup_path)
    
    try:
        if args.dry_run:
            logger.info("Dry run enabled - calculating bounds without modifying world")
            schematic = load_schematic(args.schematic)
            schematic_bounds = get_schematic_bounds(schematic)
            schematic_width = schematic_bounds.size_x
            schematic_height = schematic_bounds.size_y
            schematic_depth = schematic_bounds.size_z
            schematic.close()

            world_bounds = SelectionBox(
                (paste_x, paste_y, paste_z),
                (paste_x + schematic_width, paste_y + schematic_height, paste_z + schematic_depth)
            )
        else:
            # Paste schematic into world
            world_bounds = paste_schematic_into_world(args.world, args.schematic, paste_location)

            # Get schematic dimensions from world_bounds
            schematic_width = world_bounds.max_x - world_bounds.min_x
            schematic_height = world_bounds.max_y - world_bounds.min_y
            schematic_depth = world_bounds.max_z - world_bounds.min_z

        # Calculate chunks (useful for both real renders and dry runs)
        chunk_list = get_chunks_for_bounds(world_bounds)
        logger.info(f"Schematic occupies {len(chunk_list)} chunks")
        
        # Calculate structure center
        center_x = paste_x + schematic_width / 2
        center_y = paste_y + schematic_height / 2
        center_z = paste_z + schematic_depth / 2
        
        # Camera positioning: rotate around structure at specified angle and distance
        import math
        
        # Convert angle to radians (0=East, 90=South, 180=West, 270=North)
        angle_radians = math.radians(args.camera_angle)
        
        # Calculate camera position at specified distance and angle
        camera_x = center_x + args.camera_distance * math.cos(angle_radians)
        camera_z = center_z + args.camera_distance * math.sin(angle_radians)
        camera_y = center_y + args.camera_elevation
        
        # Calculate yaw to look back at center
        dx = center_x - camera_x
        dz = center_z - camera_z
        yaw = math.degrees(math.atan2(dz, dx))
        
        # Use specified pitch (or calculate to look at center if needed)
        pitch = args.camera_pitch
        
        camera_params = {
            "position": {
                "x": camera_x,
                "y": camera_y,
                "z": camera_z
            },
            "orientation": {
                "yaw": yaw,
                "pitch": pitch,
                "roll": 0.0
            }
        }
        
        logger.info(
            "Camera: pos=(%.1f, %.1f, %.1f), yaw=%.1f°, pitch=%.1f°",
            camera_params['position']['x'],
            camera_params['position']['y'],
            camera_params['position']['z'],
            camera_params['orientation']['yaw'],
            camera_params['orientation']['pitch']
        )

        if args.dry_run:
            logger.info("Dry run complete - no world modifications or renders were performed")
            logger.info(
                "Summary: size=(%.1f, %.1f, %.1f), center=(%.1f, %.1f, %.1f), chunks=%s",
                schematic_width,
                schematic_height,
                schematic_depth,
                center_x,
                center_y,
                center_z,
                chunk_list
            )
            return

        # Generate scene using EXACT settings from working test_VOID_FIXED
        # Use consistent scene name - Chunky will update the existing scene and snapshots
        scene_name = "schematic_render"
        scene_dir = os.path.expanduser(f"~/.chunky/scenes/{scene_name}")
        os.makedirs(scene_dir, exist_ok=True)

        scene_data = {
            "sdfVersion": 9,
            "name": scene_name,
            "width": 800,  # Same as test_VOID_FIXED
            "height": 600,
            "exposure": 1.0,
            "postprocess": "NONE",
            "outputMode": "PNG",
            "spp": 0,
            "sppTarget": args.spp,
            "pathTrace": True,
            "dumpFrequency": 500,  # Match working scene
            "saveSnapshots": True,  # Explicitly enable
            "rayDepth": 5,  # Match working scene
            "camera": {
                **camera_params,
                "fov": 70.0  # Same as test_VOID_FIXED
            },
            "sun": {
                "altitude": 70.0,  # High sun, well above horizon
                "azimuth": 225.0,  # Same as camera yaw
                "intensity": 2.5,  # Bright lighting
                "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
            },
            "sky": {
                "skyYaw": 0.0,
                "skyMirrored": False,
                "skyLight": 2.0,  # Brighter ambient light
                "mode": "SIMULATED",  # Same as test_VOID_FIXED
                "horizonOffset": 0.1
            },
            "chunkList": chunk_list,
            "world": {"path": os.path.abspath(args.world), "dimension": 0},
            "yMin": 0,  # Full range like test_VOID_FIXED
            "yMax": 256,
            "yClipMin": 0,
            "yClipMax": 256,
            "emittersEnabled": True,
            "emitterIntensity": 13.0,
            "sunEnabled": True,
            "transparentSky": False  # Same as test_VOID_FIXED
        }

        scene_file = os.path.join(scene_dir, f"{scene_name}.json")
        with open(scene_file, 'w') as f:
            json.dump(scene_data, f, indent=2)

        logger.info(f"Scene file created: {scene_file}")
        
        # Render
        logger.info("Starting Chunky render...")
        success = render_scene_with_chunky(
            chunky_launcher_path=args.chunky_path,
            scene_dir=scene_dir,
            output_image_path=os.path.abspath(args.output),
            threads=4
        )
        
        if success:
            logger.info(f"✓ Render completed successfully!")
            logger.info(f"  Output: {args.output}")
            file_size = os.path.getsize(args.output)
            logger.info(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        else:
            logger.error("✗ Render failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
