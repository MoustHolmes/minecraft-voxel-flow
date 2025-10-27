#!/usr/bin/env python3
"""
Test render with proper sun position and emitters enabled.
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Structure at X:0-13, Y:64-90, Z:0-37, center:(6.5, 77, 18.5)
structure_center = (6.5, 77.0, 18.5)

# Position camera closer and looking directly at structure
camera_x = structure_center[0] + 25  # 25 blocks east
camera_y = structure_center[1] + 10  # 10 blocks above center
camera_z = structure_center[2] + 25  # 25 blocks south

# Calculate yaw to look back at structure
# Camera is southeast of structure, so look northwest
yaw = 225.0  # Northwest

camera_params = {
    'position': {
        'x': camera_x,
        'y': camera_y,
        'z': camera_z
    },
    'orientation': {
        'pitch': -15.0,  # Look down slightly
        'yaw': yaw,
        'roll': 0.0
    }
}

chunk_list = [[0, 0], [0, 1], [0, 2]]
scene_dir = os.path.expanduser("~/.chunky/scenes/void_lit")
os.makedirs(scene_dir, exist_ok=True)

world_path = "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void"

print(f"Structure center: {structure_center}")
print(f"Camera: ({camera_x:.1f}, {camera_y:.1f}, {camera_z:.1f})")
print(f"Looking: pitch={camera_params['orientation']['pitch']}°, yaw={yaw}°")

# Create scene file manually with better lighting
scene_data = {
    "sdfVersion": 9,
    "name": "void_lit",
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
        "altitude": 60.0,  # High sun
        "azimuth": 135.0,  # From southeast (lights northwest faces)
        "intensity": 1.25,
        "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
    },
    "sky": {
        "skyYaw": 0.0,
        "skyMirrored": False,
        "skyLight": 1.0,
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
    "transparentSky": False
}

scene_file = os.path.join(scene_dir, "void_lit.json")
with open(scene_file, 'w') as f:
    json.dump(scene_data, f, indent=2)

print(f"\nScene: {scene_file}")

# Render
from minecraft_voxel_flow.rendering import render_scene_with_chunky

print("\nRendering with bright lighting...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_VOID_LIT.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_VOID_LIT.png")
    print(f"\n✓ Render complete: test_VOID_LIT.png ({file_size:,} bytes)")
else:
    print("\n✗ Render failed")
