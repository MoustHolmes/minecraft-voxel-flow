#!/usr/bin/env python3
"""
Test rendering the schematic in the void world with correct camera position.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.rendering import (
    generate_scene_file,
    render_scene_with_chunky
)

# Structure is at X:0-13, Y:64-90, Z:0-37
# Center: (6.5, 77, 18.5)
structure_center = (6.5, 77.0, 18.5)

# Position camera to look at the structure from southeast (like isometric view)
# Distance of 40 blocks from center
distance = 40
camera_x = structure_center[0] + distance * 0.707  # Southeast: +X, +Z
camera_y = structure_center[1] + 15  # Slightly above
camera_z = structure_center[2] + distance * 0.707

camera_params = {
    'position': {
        'x': camera_x,
        'y': camera_y,
        'z': camera_z
    },
    'orientation': {
        'pitch': -20.0,  # Look slightly down
        'yaw': 225.0,    # Face northwest (back toward structure)
        'roll': 0.0
    }
}

# The chunks we know exist (from previous render)
chunk_list = [[0, 0], [0, 1], [0, 2]]

# Generate scene
scene_dir = os.path.expanduser("~/.chunky/scenes/void_test")
os.makedirs(scene_dir, exist_ok=True)

world_path = "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void"

print(f"Structure center: {structure_center}")
print(f"Camera position: ({camera_x:.1f}, {camera_y:.1f}, {camera_z:.1f})")
print(f"Camera orientation: pitch={camera_params['orientation']['pitch']}°, yaw={camera_params['orientation']['yaw']}°")
print(f"Chunks: {chunk_list}")

scene_file = generate_scene_file(
    scene_dir=scene_dir,
    world_path=world_path,
    camera_params=camera_params,
    chunk_list=chunk_list,
    width=800,
    height=600,
    spp=100,
    transparent_sky=False
)

print(f"\nScene file: {scene_file}")

# Render
print("\nRendering...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_VOID_FIXED.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_VOID_FIXED.png")
    print(f"\n✓ Render complete: test_VOID_FIXED.png ({file_size:,} bytes)")
else:
    print("\n✗ Render failed")
    sys.exit(1)
