#!/usr/bin/env python3
"""
Ultra-simple test: camera extremely close, looking directly at known block location.
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# We KNOW there are blocks at (5, 70, 20) - planks block confirmed
look_at = [5.0, 70.0, 20.0]

# Put camera VERY close - only 10 blocks away
camera = [15.0, 70.0, 20.0]  # 10 blocks east of the block

# Calculate yaw to look back at the block
import math
dx = look_at[0] - camera[0]
dz = look_at[2] - camera[2]
yaw = math.degrees(math.atan2(dz, dx))
if yaw < 0:
    yaw += 360

print(f"Looking at block: ({look_at[0]}, {look_at[1]}, {look_at[2]})")
print(f"Camera at: ({camera[0]}, {camera[1]}, {camera[2]})")
print(f"Yaw: {yaw:.1f}° (should be 180° = looking west)")
print(f"Distance: 10 blocks")

scene_dir = os.path.expanduser("~/.chunky/scenes/ultra_close")
os.makedirs(scene_dir, exist_ok=True)

scene_data = {
    "sdfVersion": 9,
    "name": "ultra_close",
    "width": 800,
    "height": 600,
    "exposure": 1.0,
    "postprocess": 1,
    "outputMode": "PNG",
    "spp": 0,
    "sppTarget": 100,
    "pathTrace": True,
    "camera": {
        "position": {"x": camera[0], "y": camera[1], "z": camera[2]},
        "orientation": {"pitch": 0.0, "yaw": yaw, "roll": 0.0},
        "fov": 70.0
    },
    "sun": {
        "altitude": 60.0,
        "azimuth": 90.0,  # From east
        "intensity": 2.0,  # Extra bright
        "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
    },
    "sky": {
        "skyLight": 2.0,
        "mode": "SIMULATED"
    },
    "chunkList": [[0, 1]],  # Only chunk containing our block
    "world": {
        "path": "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void",
        "dimension": 0
    },
    "yMin": 60,
    "yMax": 80,
    "yClipMin": 60,
    "yClipMax": 80,
    "emittersEnabled": True,
    "emitterIntensity": 15.0,
    "sunEnabled": True,
    "transparentSky": False
}

scene_file = os.path.join(scene_dir, "ultra_close.json")
with open(scene_file, 'w') as f:
    json.dump(scene_data, f, indent=2)

print(f"\nScene: {scene_file}")

from minecraft_voxel_flow.rendering import render_scene_with_chunky

print("\nRendering ultra-close view...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_ULTRA_CLOSE.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_ULTRA_CLOSE.png")
    print(f"\n✓ Render: test_ULTRA_CLOSE.png ({file_size:,} bytes)")
