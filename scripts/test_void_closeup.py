#!/usr/bin/env python3
"""
Render close-up view of the schematic.
"""
import os
import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# We know blocks exist at (0,64,0) to (13,90,37)
# Let's look at the middle of the structure
look_at = [6.5, 77.0, 18.5]  # Center of structure

# Position camera MUCH closer - only 20 blocks away
distance = 20
camera_x = look_at[0] + distance
camera_y = look_at[1] + 5  # Slightly above
camera_z = look_at[2] + distance

# Calculate exact angles to look AT look_at point
dx = look_at[0] - camera_x
dy = look_at[1] - camera_y
dz = look_at[2] - camera_z

yaw_rad = math.atan2(dz, dx)
yaw = math.degrees(yaw_rad)
if yaw < 0:
    yaw += 360

horizontal_dist = math.sqrt(dx*dx + dz*dz)
pitch_rad = math.atan2(dy, horizontal_dist)
pitch = math.degrees(pitch_rad)

print(f"Looking at: ({look_at[0]:.1f}, {look_at[1]:.1f}, {look_at[2]:.1f})")
print(f"Camera at: ({camera_x:.1f}, {camera_y:.1f}, {camera_z:.1f})")
print(f"Distance: {math.sqrt(dx*dx + dy*dy + dz*dz):.1f} blocks")
print(f"Angles: yaw={yaw:.1f}°, pitch={pitch:.1f}°")

camera_params = {
    'position': {'x': camera_x, 'y': camera_y, 'z': camera_z},
    'orientation': {'pitch': pitch, 'yaw': yaw, 'roll': 0.0}
}

chunk_list = [[0, 0], [0, 1], [0, 2]]
scene_dir = os.path.expanduser("~/.chunky/scenes/void_closeup")
os.makedirs(scene_dir, exist_ok=True)

world_path = "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void"

scene_data = {
    "sdfVersion": 9,
    "name": "void_closeup",
    "width": 800,
    "height": 600,
    "exposure": 1.0,
    "postprocess": 1,
    "outputMode": "PNG",
    "spp": 0,
    "sppTarget": 100,
    "pathTrace": True,
    "camera": camera_params,
    "sun": {
        "altitude": 60.0,
        "azimuth": 45.0,  # Sun from northeast
        "intensity": 1.5,
        "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
    },
    "sky": {
        "skyLight": 1.5,
        "mode": "SIMULATED"
    },
    "chunkList": chunk_list,
    "world": {"path": world_path, "dimension": 0},
    "yMin": 60,  # Clip to focus on structure height
    "yMax": 95,
    "yClipMin": 60,
    "yClipMax": 95,
    "emittersEnabled": True,
    "emitterIntensity": 13.0,
    "sunEnabled": True,
    "transparentSky": False
}

scene_file = os.path.join(scene_dir, "void_closeup.json")
with open(scene_file, 'w') as f:
    json.dump(scene_data, f, indent=2)

print(f"\nScene: {scene_file}")

from minecraft_voxel_flow.rendering import render_scene_with_chunky

print("\nRendering close-up view...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_VOID_CLOSEUP.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_VOID_CLOSEUP.png")
    print(f"\n✓ Render complete: test_VOID_CLOSEUP.png ({file_size:,} bytes)")
    
    from PIL import Image
    img = Image.open("./test_VOID_CLOSEUP.png")
    pixels = list(img.getdata())
    from collections import Counter
    colors = Counter(pixels)
    print(f"  Unique colors: {len(colors):,}")
    print(f"  Top color: RGB{colors.most_common(1)[0][0]} ({colors.most_common(1)[0][1]} pixels)")
else:
    print("\n✗ Render failed")
