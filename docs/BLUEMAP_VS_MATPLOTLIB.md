# BlueMap vs Matplotlib for Schematic Screenshots

## TL;DR

**BlueMap is installed and working, but it's designed for Minecraft WORLDS, not schematics.**

For your use case (rendering 10,665 schematics), the **matplotlib solution is much better**.

## What You Asked For

You found this page: https://bluemap.bluecolored.de/community/python-screenshots.html

And wanted to see BlueMap screenshots working.

## What I've Set Up

### ✅ BlueMap Installation (Complete)
- BlueMap CLI 5.13 downloaded to `tools/bluemap/bluemap-cli.jar`
- Java 21 installed and configured
- Playwright + chromium installed for browser automation
- All dependencies ready

### ⚠️  The Problem: BlueMap Requires Worlds, Not Schematics

BlueMap is designed to render **Minecraft worlds**, which have a specific structure:
```
world/
├── level.dat          # World metadata (NBT format)
├── region/            # Region files
│   ├── r.0.0.mca     # Anvil format region files
│   ├── r.0.1.mca
│   └── ...
└── data/              # Other world data
```

Your schematics (`.schematic`, `.schem`, `.litematic`) are NOT worlds. They're:
- Smaller, portable structures
- Different file format
- Missing world metadata

## Why This Matters

To use BlueMap with your schematics, you would need to:

1. **Convert each schematic to a full Minecraft world**
   - Create `level.dat` with proper NBT structure
   - Generate region files (`.mca` format)
   - Set up proper chunk data
   - This is complex and time-consuming

2. **Start BlueMap server for each world**
   - `java -jar bluemap-cli.jar -w world_1 -rw` 
   - Wait for server to start (~5 seconds)
   - Take screenshot via Playwright
   - Shut down server
   - Repeat for next schematic

3. **For 10,665 schematics:**
   - 10,665 world conversions
   - 10,665 server start/stop cycles
   - ~15 hours minimum (assuming 5 seconds per schematic)

## What Actually Works: Matplotlib Solution

I've built a **complete working solution** that:

### ✅ Works Directly with Schematics
- No conversion needed
- Loads `.schematic`, `.schem`, `.litematic` directly
- Uses existing `SchematicLoader` class

### ✅ Fast Batch Processing
- ~1 second per schematic
- Progress bars with `tqdm`
- Can process all 10,665 in ~3 hours

### ✅ Multiple Visualization Modes
1. **Showcase Mode** - Comprehensive view with:
   - 3D isometric view
   - Top/front/side 2D slices
   - Statistics panel
   - Top 10 blocks chart

2. **Preview Mode** - Simple 2D slices:
   - 5 horizontal slices
   - Fast generation
   - Good for browsing

### ✅ Already Tested and Working
```bash
# These commands work right now:
python scripts/render_schematics.py --mode showcase --max 10
python scripts/generate_previews.py --max 100
```

## BlueMap Demo (If You Still Want to See It)

### Scenario 1: You Have a Minecraft World

If you have an actual Minecraft world:

```bash
# Start BlueMap server
java -jar tools/bluemap/bluemap-cli.jar -w /path/to/minecraft/world -rw

# In another terminal, take screenshot
python scripts/bluemap_screenshot_demo.py
```

### Scenario 2: Test with Playwright (What I Built)

```bash
# Test BlueMap connection
python scripts/test_bluemap.py
```

This shows:
- ✅ BlueMap CLI installed
- ✅ Java working
- ✅ Playwright working
- ❌ No world to render (expected)

## Side-by-Side Comparison

| Feature | BlueMap | Matplotlib Solution |
|---------|---------|---------------------|
| **Works with schematics** | ❌ No (needs conversion) | ✅ Yes (direct) |
| **Setup complexity** | 🔴 High | 🟢 Low |
| **Speed per schematic** | 🔴 ~5-10 seconds | 🟢 ~1 second |
| **Render quality** | 🟢 Very high (3D game engine) | 🟡 Good (matplotlib 3D) |
| **Batch processing** | 🔴 Complex | 🟢 Simple |
| **All 10,665 schematics** | 🔴 ~15 hours | 🟢 ~3 hours |
| **Currently working** | ⚠️  Needs world setup | ✅ Yes |

## What I Recommend

### For Your Dataset (10,665 Schematics)

**Use the Matplotlib solution:**

```bash
# Generate showcase images for review
python scripts/render_schematics.py --mode showcase --max 100

# Generate simple previews for all
python scripts/generate_previews.py
```

**Why:**
- ✅ Already working
- ✅ Fast batch processing
- ✅ Good quality for ML/analysis
- ✅ No world conversion needed
- ✅ Progress tracking built-in

### If You Need BlueMap-Quality Renders

For a **small subset** of schematics where you need publication-quality images:

1. Manually create Minecraft worlds with selected schematics (using WorldEdit in-game)
2. Use BlueMap on those worlds
3. Use the Playwright automation I built

But this is impractical for thousands of schematics.

## Examples of What Works Now

### Showcase Mode Output
```bash
python scripts/render_schematics.py --mode showcase --max 3
```

Created these files:
- `data/showcase_test/10234_showcase.png` (521 KB)
- `data/showcase_test/7704_showcase.png` (707 KB)
- `data/showcase_test/9719_showcase.png` (788 KB)

Each image includes:
- 3D isometric view (with proper block coloring)
- Top/front/side cross-sections
- Statistics (dimensions, block count, types)
- Top 10 blocks chart

### Preview Mode Output
```bash
python scripts/generate_previews.py --max 5
```

Created: `data/previews_test/*.png` (5 files, ~300 KB each)

Each image shows 5 horizontal slices through the schematic.

## Files I Created

### Working Scripts
- ✅ `scripts/render_schematics.py` - Enhanced renderer (working)
- ✅ `scripts/generate_previews.py` - Simple previews (working)
- ✅ `scripts/bluemap_screenshot_demo.py` - BlueMap automation (needs world)
- ✅ `scripts/test_bluemap.py` - Connection test (shows BlueMap status)

### Documentation
- ✅ `docs/SCREENSHOT_GENERATION.md` - Complete guide
- ✅ `docs/BLUEMAP_SCREENSHOTS.md` - BlueMap setup info
- ✅ `docs/BLUEMAP_VS_MATPLOTLIB.md` - This file

### Tools
- ✅ BlueMap CLI 5.13 (`tools/bluemap/bluemap-cli.jar`)
- ✅ Java 21 installed
- ✅ Playwright + chromium installed

## Conclusion

**BlueMap is successfully installed** and I've built the automation framework from the wiki page you found. However:

- BlueMap is designed for rendering Minecraft **worlds**
- Your schematics would need complex conversion
- The matplotlib solution is **already working** and practical

**You have two complete, working screenshot solutions ready to use right now:**
1. `render_schematics.py` - High-quality multi-view renders
2. `generate_previews.py` - Fast 2D previews

Both work directly with your 10,665 schematics, no conversion needed.

## Try It Yourself

```bash
# See the working solution
python scripts/render_schematics.py --mode showcase --max 5
open data/showcase_test/
```

You'll see beautiful, detailed visualizations of your schematics - no BlueMap world conversion needed!
