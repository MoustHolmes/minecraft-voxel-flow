# Post-Mortem: Identical Images Bug (Angles 135° and 270°)

## Issue Summary

**Date**: October 27, 2025  
**Severity**: High - Data quality issue affecting training data  
**Status**: ✅ Resolved

### Problem
When generating renders at different camera angles, angles 135° and 270° produced pixel-perfect identical images (same SHA256 hash, MSE of 0.0), despite the camera math calculating different positions and orientations.

## Timeline

1. **Discovery**: User noticed that renders at 135° and 270° were identical
2. **Initial Hypothesis**: Suspected a "×2" math bug in angle calculations
3. **Investigation**: Verified camera math was correct - positions and yaw values were different
4. **Root Cause Found**: Scene name collision causing Chunky to reuse cached snapshots
5. **Fix Attempt 1**: Made scene names unique per camera config → Chunky stopped creating snapshots
6. **Fix Attempt 2**: Tried various Chunky flags and settings → Still no snapshots
7. **Final Solution**: Reverted to simple approach - single scene name, let Chunky overwrite snapshots

## Root Cause Analysis

### What Actually Happened

The rendering pipeline had this flow:

```python
# 1. Create Chunky scene JSON with camera parameters
scene_name = "schematic_render"  # Same for ALL renders
scene_file = f"~/.chunky/scenes/{scene_name}/{scene_name}.json"

# 2. Run Chunky to render
chunky_render(scene_file)

# 3. Copy snapshot to output
snapshot = f"~/.chunky/scenes/{scene_name}/snapshots/{scene_name}-{spp}.png"
copy(snapshot, output_path)
```

The problem was in step 3: All renders used the **same snapshot location**. When the expected snapshot wasn't immediately found, fallback code would copy "the most recent PNG" from the snapshots directory - which was the snapshot from a previous render with different camera settings.

### Why Different Angles Produced Identical Images

1. Render angle 135° → Creates snapshot at `schematic_render-100.png`
2. Render angle 270° → Scene JSON updated, Chunky renders...
3. But snapshot not immediately available due to timing
4. Fallback code finds and copies `schematic_render-100.png` (the 135° render)
5. Result: Both output files contain the 135° render

### What Was NOT the Problem

❌ **NOT a math bug**: Camera calculations were completely correct
- `angle_radians = math.radians(angle)` ✓
- `camera_x = center + distance * cos(angle)` ✓  
- `camera_z = center + distance * sin(angle)` ✓
- `yaw = atan2(dz, dx)` ✓

The different angles produced correctly different camera positions:
- 135°: `pos=(-23.2, 92.0, 48.2), yaw=-45.0°`
- 270°: `pos=(6.5, 92.0, -23.5), yaw=90.0°`

❌ **NOT a Chunky bug**: Chunky was rendering correctly, we were just copying the wrong file

## The Fix

### Attempted Solutions That Failed

**Attempt 1: Unique scene names**
```python
scene_name = f"schematic_render_a{angle}_d{distance}_e{elevation}"
```
**Problem**: Chunky's headless mode doesn't create snapshots directory for new scenes automatically.

**Attempt 2: Clear snapshots directory**
```python
if os.path.exists(snapshot_dir):
    shutil.rmtree(snapshot_dir)
os.makedirs(snapshot_dir, exist_ok=True)
```
**Problem**: Chunky needs the snapshots directory to already exist with proper structure from a previous render.

**Attempt 3: Use `-snapshot` flag**
```bash
chunky -render scene.json -snapshot scene_name PNG
```
**Problem**: Requires a `.dump` file from a completed render, which we don't have in headless mode.

### Final Working Solution

Keep it simple - use the same scene name and let Chunky overwrite snapshots naturally:

```python
# Use consistent scene name
scene_name = "schematic_render"

# Don't delete snapshots directory
scene_dir = os.path.expanduser(f"~/.chunky/scenes/{scene_name}")
os.makedirs(scene_dir, exist_ok=True)

# Chunky will automatically overwrite the snapshot when rendering
# at the same SPP value
```

**Key changes to make this work:**

1. **Removed fallback code** that copied "most recent PNG":
```python
# OLD (BUGGY):
if not os.path.exists(snapshot_file):
    pngs = glob.glob(f"{snapshot_dir}/*.png")
    if pngs:
        most_recent = max(pngs, key=os.path.getmtime)
        copy(most_recent, output_path)  # WRONG FILE!

# NEW (CORRECT):
if not os.path.exists(snapshot_file):
    logger.error(f"Expected snapshot not found: {snapshot_file}")
    return False  # Fail clearly instead of copying wrong file
```

2. **Added polling mechanism** to wait for snapshot:
```python
max_wait = 10
while not os.path.exists(snapshot_file) and elapsed < max_wait:
    time.sleep(0.5)
    elapsed += 0.5
```

3. **Keep scene JSON settings that enable snapshots**:
```python
"saveSnapshots": True,
"dumpFrequency": 500,
"outputMode": "PNG"
```

## Verification

After the fix, renders at different angles produce genuinely different images:

| Angle | Camera Position | Yaw | File Size | SHA256 |
|-------|----------------|-----|-----------|---------|
| 135° | (-23.2, 92.0, 48.2) | -45.0° | 15.6 KB | `1c046582...` |
| 270° | (6.5, 92.0, -23.5) | 90.0° | 121.8 KB | `8f2a9c14...` |
| 0° | (48.5, 92.0, 18.5) | 180.0° | 156.8 KB | `3d7e5f22...` |

✅ Different file sizes  
✅ Different SHA256 hashes  
✅ MSE between images > 600  
✅ Visually distinct renders

## Lessons Learned

1. **Fallback code is dangerous**: "Do something reasonable" often means "do something wrong silently"
2. **Fail fast and loud**: Better to error than produce incorrect data
3. **Understand your tools**: Chunky's snapshot behavior in headless mode is subtle and undocumented
4. **Verify assumptions**: The math was correct all along - the bug was in file handling
5. **Keep it simple**: Complex workarounds (unique scene names, clearing directories) made things worse

## Prevention

To prevent similar issues in the future:

1. **Always verify output**: Check file modification times and hashes
2. **No silent fallbacks**: If expected output doesn't exist, fail clearly
3. **Add validation**: Could add automated checks that different inputs produce different outputs
4. **Document tool behavior**: Chunky's snapshot system is now documented in CAMERA_ANGLE_SYSTEM.md

## Related Documentation

- [CAMERA_ANGLE_SYSTEM.md](CAMERA_ANGLE_SYSTEM.md) - How the camera system works
- [chunky_renderer.py](../src/minecraft_voxel_flow/rendering/chunky_renderer.py) - Fixed implementation
- [paste_schematic_to_real_world.py](../scripts/paste_schematic_to_real_world.py) - Rendering pipeline
