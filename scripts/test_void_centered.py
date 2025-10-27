#!/usr/bin/env python3
"""
Render the schematic centered and well-lit.
"""
import os
import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Structure at X:0-13, Y:64-90, Z:0-37
# Center: (6.5, 77, 18.5)
structure_center = [6.5, 77.0, 18.5]

# Camera setup - position to look AT the center from southeast
distance = 50  # Distance from structure
angle_horizontal = math.radians(45)  # 45 degrees = southeast

# Calculate camera position (southeast of structure)
camera_x = structure_center[0] + distance * math.cos(angle_horizontal)
camera_y = structure_center[1] + 20  # 20 blocks above structure center
camera_z = structure_center[2] + distance * math.sin(angle_horizontal)

# Calculate exact yaw and pitch to look AT the structure center
dx = structure_center[0] - camera_x
dy = structure_center[1] - camera_y
dz = structure_center[2] - camera_z

# Yaw: angle in XZ plane (where we look horizontally)
yaw_rad = math.atan2(dz, dx)
yaw = math.degrees(yaw_rad)
# Normalize yaw to 0-360 range
if yaw < 0:
    yaw += 360

# Pitch: angle up/down
horizontal_dist = math.sqrt(dx*dx + dz*dz)
pitch_rad = math.atan2(dy, horizontal_dist)
pitch = math.degrees(pitch_rad)

print(f"Structure center: ({structure_center[0]:.1f}, {structure_center[1]:.1f}, {structure_center[2]:.1f})")
print(f"Camera position: ({camera_x:.1f}, {camera_y:.1f}, {camera_z:.1f})")
print(f"Camera angles: pitch={pitch:.1f}° (negative=down), yaw={yaw:.1f}°")
print(f"Distance to target: {math.sqrt(dx*dx + dy*dy + dz*dz):.1f} blocks")

camera_params = {
    'position': {
        'x': camera_x,
        'y': camera_y,
        'z': camera_z
    },
    'orientation': {
        'pitch': pitch,
        'yaw': yaw,
        'roll': 0.0
    }
}

chunk_list = [[0, 0], [0, 1], [0, 2]]
scene_dir = os.path.expanduser("~/.chunky/scenes/void_centered")
os.makedirs(scene_dir, exist_ok=True)

world_path = "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void"

# Create scene with good lighting
scene_data = {
    "sdfVersion": 9,
    "name": "void_centered",
    "width": 800,
    "height": 600,
    "exposure": 1.0,
    "postprocess": 1,
    "outputMode": "PNG",
    "renderTime": 0,
    "spp": 0,
    "sppTarget": 100,
    "pathTrace": True,
    "camera": camera_params,
    "sun": {
        "altitude": 50.0,  # Sun at 50 degrees up
        "azimuth": yaw - 180,  # Sun behind camera (lights the structure from our viewpoint)
        "intensity": 1.5,
        "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
    },
    "sky": {
        "skyYaw": 0.0,
        "skyMirrored": False,
        "skyLight": 1.2,
        "mode": "SIMULATED",
        "horizonOffset": 0.0
    },
    "chunkList": chunk_list,
    "world": {
        "path": world_path,
        "dimension": 0
    },
    "yMin": 0,
    "yMax": 256,
    "yClipMin": 0,
    "yClipMax": 256,
    "emittersEnabled": True,
    "emitterIntensity": 13.0,
    "sunEnabled": True,
    "transparentSky": False,
    "fog": {
        "enable": False
    }
}

scene_file = os.path.join(scene_dir, "void_centered.json")
with open(scene_file, 'w') as f:
    json.dump(scene_data, f, indent=2)

print(f"\nScene: {scene_file}")

# Render
from minecraft_voxel_flow.rendering import render_scene_with_chunky

print("\nRendering centered view with front lighting...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_VOID_CENTERED.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_VOID_CENTERED.png")
    print(f"\n✓ Render complete: test_VOID_CENTERED.png ({file_size:,} bytes)")
    
    # Quick analysis
    from PIL import Image
    img = Image.open("./test_VOID_CENTERED.png")
    pixels = list(img.getdata())
    bright = sum(1 for r,g,b in pixels if max(r,g,b) > 100)
    print(f"  Bright pixels: {bright:,} / {len(pixels):,} ({bright/len(pixels)*100:.1f}%)")
else:
    print("\n✗ Render failed")
