# Chunky Rendering Issue - Troubleshooting Guide

## Problem Summary

When attempting to render scenes using Chunky 2.4.6, the rendering fails with:
```
Failed to load the dump file found for this scene
```

This error occurs even though:
- ✅ No dump files exist in the scene directory
- ✅ Scene JSON has `"saveDumps": false` and `"dumpFrequency": 0`
- ✅ The world data is correctly formatted and accessible
- ✅ Scene.json is properly structured with correct camera parameters
- ✅ The `-reload-chunks` flag is used

## What's Working

All pipeline components except the final Chunky rendering:

1. **Amulet Operations** ✅
   - Loading schematics from .schem files
   - Creating void worlds in Anvil format
   - Pasting schematics into worlds
   - Saving world data correctly

2. **Camera Calculation** ✅
   - Automatic camera positioning based on bounding box
   - Isometric view vector calculations
   - Correct pitch/yaw angle computation

3. **Scene Generation** ✅
   - Valid scene.json files created
   - Correct world path references
   - Proper camera configuration

## Commands Tested

All of these produce the same error:

```bash
# With scene name (copied to ~/.chunky/scenes/)
java -jar tools/chunky/ChunkyLauncher.jar -threads 2 -reload-chunks -snapshot test_scene output.png

# With full JSON path
java -jar tools/chunky/ChunkyLauncher.jar -threads 2 -reload-chunks -snapshot /full/path/to/scene.json output.png

# With UUID-generated scene name (no history)
java -jar tools/chunky/ChunkyLauncher.jar -threads 2 -reload-chunks -snapshot scene_UUID.json output.png

# With -f flag (force)
java -jar tools/chunky/ChunkyLauncher.jar -threads 2 -f -reload-chunks -snapshot scene.json output.png

# With -render instead of -snapshot
java -jar tools/chunky/ChunkyLauncher.jar -threads 2 -reload-chunks -render scene.json
# Result: Different error about missing octree2 file
```

## Investigation Results

### File System Check
```bash
# No dump files anywhere
find ~/.chunky temp_test -name "*dump*"
# (no results)

# No octree files
find ~/.chunky temp_test -name "*.octree*"
# (no results)

# Scene directory only contains scene.json
ls temp_test/test_scene/
# test_scene.json
```

### Scene JSON Configuration
```json
{
  "dumpFrequency": 0,
  "saveDumps": false,
  "spp": 0,
  "sppTarget": 100,
  ...
}
```

### World Structure
```
temp_test/test_world/
├── entities/
│   ├── r.-1.-1.mca
│   ├── r.-1.0.mca
│   ├── r.0.-1.mca
│   └── r.0.0.mca
├── region/
│   ├── r.-1.-1.mca
│   ├── r.-1.0.mca
│   ├── r.0.-1.mca
│   └── r.0.0.mca
├── level.dat
└── session.lock
```

## Possible Causes

1. **Bug in Chunky 2.4.6**
   - The error message might be misleading
   - Could be an issue with how Chunky handles scenes without pre-existing octrees
   
2. **Scene JSON Format Mismatch**
   - Some required field might be missing
   - Format might have changed between versions

3. **Octree Requirement**
   - Chunky might require an octree file even with `-reload-chunks`
   - The `-snapshot` command might not support building octrees on-the-fly

4. **World Format Issues**
   - Amulet-generated worlds might have subtle differences from vanilla Minecraft
   - The level.dat errors (WorldGenSettings) might be causing problems

## Potential Solutions

### Option 1: Try Different Chunky Version
```bash
# Download Chunky 2.4.5 or 2.5.0
# Replace ChunkyLauncher.jar
# Test again
```

### Option 2: Pre-build Octree
Create a separate step to build the octree before rendering:
```python
# Use Chunky to build octree first
subprocess.run(["java", "-jar", "ChunkyLauncher.jar", 
                "-render", scene_json_path])
# Then snapshot
subprocess.run(["java", "-jar", "ChunkyLauncher.jar",
                "-snapshot", scene_json_path, output_path])
```

### Option 3: Use Chunky GUI for Initial Setup
1. Open scene in Chunky GUI
2. Load chunks manually
3. Save scene (this creates octree)
4. Try headless rendering again

### Option 4: Alternative Rendering Tools
Consider switching to:
- **Mineways + Blender**: More complex but reliable
- **BlueMap**: If top-down views are acceptable
- **Chunky 2.5.0 or newer**: Might have fixes

### Option 5: Manual Octree Generation Script
Write a script to:
1. Load world in Chunky
2. Force chunk loading
3. Build and save octree
4. Exit
5. Then run snapshot

## Workaround for Now

Until the Chunky issue is resolved, you can:

1. **Use the GUI Method**:
   ```bash
   # Open Chunky GUI
   java -jar tools/chunky/ChunkyLauncher.jar
   
   # In GUI:
   # - Load world from temp_test/test_world
   # - Select chunks around origin
   # - Set camera from scene.json values
   # - Render
   ```

2. **Manual Batch Processing**:
   - Generate all worlds and scene.json files using the pipeline
   - Load each scene in Chunky GUI
   - Use GUI to render
   - Not automated but proves the pipeline works

3. **Try BlueMap Instead**:
   - Your existing BlueMap setup works
   - Trade-off: Different rendering style
   - Benefit: Working automated pipeline

## Next Steps

1. **Research**: Check Chunky GitHub issues for similar problems
2. **Version Test**: Try Chunky 2.5.0-alpha or 2.4.5
3. **Community**: Ask on Chunky Discord/Reddit
4. **Alternative**: Implement Mineways + Blender pipeline as backup

## Files for Debugging

All necessary files are preserved in `temp_test/` or `temp_test_uuid/`:
- World data: `temp_test/test_world/`
- Scene JSON: `temp_test/test_scene/test_scene.json`
- Can be manually loaded in Chunky GUI for investigation

## Contact/Report

If you find a solution:
1. Update this document
2. Update the chunky_renderer.py implementation
3. Mark Phase 4 tests as complete in the checklist
