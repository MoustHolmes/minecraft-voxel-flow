#!/usr/bin/env python3
"""
Properly framed view of the complete structure.
"""
import os
import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Structure bounds: X: 0-13, Y: 64-90, Z: 0-37
# Structure center and size
center_x, center_y, center_z = 6.5, 77.0, 18.5
size_x, size_y, size_z = 13, 26, 37

# Calculate diagonal size for camera distance
diagonal = math.sqrt(size_x**2 + size_y**2 + size_z**2)
print(f"Structure: {size_x}×{size_y}×{size_z} blocks")
print(f"Center: ({center_x}, {center_y}, {center_z})")
print(f"Diagonal: {diagonal:.1f} blocks")

# Position camera at a good distance - 1.5x diagonal
distance = diagonal * 1.5
angle = math.radians(45)  # 45 degrees southeast

camera_x = center_x + distance * math.cos(angle)
camera_y = center_y + distance * 0.4  # Slightly above
camera_z = center_z + distance * math.sin(angle)

# Calculate look direction
dx = center_x - camera_x
dy = center_y - camera_y
dz = center_z - camera_z

yaw = math.degrees(math.atan2(dz, dx))
if yaw < 0:
    yaw += 360
    
horizontal_dist = math.sqrt(dx**2 + dz**2)
pitch = math.degrees(math.atan2(dy, horizontal_dist))

print(f"\nCamera:")
print(f"  Position: ({camera_x:.1f}, {camera_y:.1f}, {camera_z:.1f})")
print(f"  Distance: {distance:.1f} blocks")
print(f"  Yaw: {yaw:.1f}° (looking northwest)")
print(f"  Pitch: {pitch:.1f}° (looking down)")

scene_dir = os.path.expanduser("~/.chunky/scenes/properly_framed")
os.makedirs(scene_dir, exist_ok=True)

scene_data = {
    "sdfVersion": 9,
    "name": "properly_framed",
    "width": 1200,  # Larger for more detail
    "height": 900,
    "exposure": 1.0,
    "postprocess": 1,
    "outputMode": "PNG",
    "spp": 0,
    "sppTarget": 200,  # Higher quality
    "pathTrace": True,
    "camera": {
        "position": {"x": camera_x, "y": camera_y, "z": camera_z},
        "orientation": {"pitch": pitch, "yaw": yaw, "roll": 0.0},
        "fov": 60.0  # Narrower FOV to zoom in on structure
    },
    "sun": {
        "altitude": 55.0,
        "azimuth": yaw + 180,  # Sun behind camera
        "intensity": 1.8,
        "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
    },
    "sky": {
        "skyLight": 1.5,
        "mode": "SIMULATED"
    },
    "chunkList": [[0, 0], [0, 1], [0, 2]],
    "world": {
        "path": "/Users/moustholmes/minecraft_voxel_flow/data/world_test_file/void",
        "dimension": 0
    },
    "yMin": 60,
    "yMax": 95,
    "yClipMin": 60,
    "yClipMax": 95,
    "emittersEnabled": True,
    "emitterIntensity": 13.0,
    "sunEnabled": True,
    "transparentSky": False
}

scene_file = os.path.join(scene_dir, "properly_framed.json")
with open(scene_file, 'w') as f:
    json.dump(scene_data, f, indent=2)

print(f"\nScene: {scene_file}")

from minecraft_voxel_flow.rendering import render_scene_with_chunky

print("\nRendering properly framed view...")
success = render_scene_with_chunky(
    chunky_launcher_path="./tools/chunky/ChunkyLauncher.jar",
    scene_dir=scene_dir,
    output_image_path="./test_PROPERLY_FRAMED.png",
    threads=4
)

if success:
    file_size = os.path.getsize("./test_PROPERLY_FRAMED.png")
    print(f"\n✓ Render: test_PROPERLY_FRAMED.png ({file_size:,} bytes)")
    print("  Structure should be clearly visible and well-lit in center of frame")
