# Camera Angle System Documentation

## Overview

The schematic rendering pipeline supports flexible camera positioning using a polar coordinate system. This allows you to render Minecraft schematics from any angle around the structure.

## Camera Parameters

The camera system provides four main parameters:

### `--camera-angle` (default: 45°)
The horizontal angle around the schematic, measured in degrees:
- `0°` = View from the East (+X direction)
- `90°` = View from the South (+Z direction)  
- `180°` = View from the West (-X direction)
- `270°` = View from the North (-Z direction)
- `225°` = Default viewing angle (Southwest perspective)

### `--camera-distance` (default: 42 blocks)
The horizontal distance from the camera to the center of the schematic. Larger values show more context but make the structure smaller in frame.

### `--camera-elevation` (default: 15 blocks)
The vertical height of the camera above the schematic's center point. Positive values look down from above, negative values look up from below.

### `--camera-pitch` (default: -20°)
The vertical tilt angle of the camera:
- Negative values (e.g., -20°) = Looking down
- 0° = Looking straight ahead (horizontal)
- Positive values = Looking up

## How It Works

The camera positioning uses polar coordinates:

```python
# Convert angle to radians
angle_radians = math.radians(camera_angle)

# Calculate camera position in a circle around the schematic center
camera_x = center_x + distance * math.cos(angle_radians)
camera_z = center_z + distance * math.sin(angle_radians)
camera_y = center_y + elevation

# Calculate yaw to look at the center
dx = center_x - camera_x
dz = center_z - camera_z
yaw = math.degrees(math.atan2(dz, dx))
```

The camera is positioned at the calculated coordinates and oriented to look at the schematic's center point.

## Usage Examples

### Basic render from default angle (225° Southwest):
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output render.png \
    --spp 100
```

### Render from the North (looking South):
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output north_view.png \
    --camera-angle 270 \
    --spp 100
```

### Render from the East at greater distance:
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output east_far.png \
    --camera-angle 0 \
    --camera-distance 60 \
    --spp 100
```

### Top-down view (bird's eye):
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output top_down.png \
    --camera-angle 45 \
    --camera-elevation 50 \
    --camera-pitch -60 \
    --spp 100
```

### Low angle view (looking up):
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output low_angle.png \
    --camera-angle 180 \
    --camera-elevation -10 \
    --camera-pitch 10 \
    --spp 100
```

### Generate multiple angles (360° turnaround):
```bash
for angle in 0 45 90 135 180 225 270 315; do
    python scripts/paste_schematic_to_real_world.py \
        data/schematics/10234.schematic \
        --world data/world_test_file/void \
        --output "renders/angle_${angle}.png" \
        --camera-angle $angle \
        --spp 100
done
```

## Lighting Configuration

The renders use optimized lighting settings:

- **Sun Altitude**: 70° (high sun, minimal shadows)
- **Sun Azimuth**: Matches camera yaw for consistent lighting
- **Sun Intensity**: 2.5 (bright, clear lighting)
- **Sky Light**: 2.0 (enhanced ambient lighting)
- **Sky Mode**: Simulated (realistic sky gradient)

These settings were chosen to provide clear, well-lit renders suitable for training neural networks.

## Troubleshooting

### Issue: "Snapshots directory doesn't exist"
**Solution**: Ensure you've run at least one successful render first. Chunky creates the snapshots directory on the first successful render.

### Issue: Renders look identical despite different angles
**Solution**: Verify that the snapshot file is being updated. Check the modification time:
```bash
ls -lh ~/.chunky/scenes/schematic_render/snapshots/
```
The snapshot should have a recent timestamp matching your render time.

### Issue: Schematic not visible in frame
**Solution**: Adjust `--camera-distance` to increase or decrease the viewing distance. For larger schematics, try values between 60-100.

### Issue: Schematic too dark
**Solution**: The lighting is already optimized, but you can increase SPP (samples per pixel) for cleaner, brighter renders:
```bash
--spp 200  # or higher for better quality
```

## Technical Notes

### Why Use the Same Scene Name?

The rendering system uses a consistent scene name (`schematic_render`) for all renders. This is intentional:

1. **Chunky Snapshot Behavior**: Chunky's headless mode only saves snapshots for scenes that already have a snapshots directory
2. **Efficiency**: Reusing the scene directory allows Chunky to cache octree data
3. **Reliability**: Chunky properly overwrites snapshots when rendering the same scene at the same SPP

### Camera Math Verification

The camera positioning math has been verified to be correct:
- No "×2" bugs or angle doubling
- Proper radian/degree conversions
- Correct polar-to-Cartesian coordinate transformation
- Accurate yaw calculation using `atan2`

Different camera angles produce genuinely different renders with different file sizes and content.

## See Also

- [Chunky Documentation](https://chunky-dev.github.io/docs/)
- [SCHEMATIC_LOADING_PLAN.md](SCHEMATIC_LOADING_PLAN.md) - How schematics are loaded
- [SCREENSHOT_GENERATION.md](SCREENSHOT_GENERATION.md) - Overview of the rendering pipeline
