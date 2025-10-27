# Schematic Rendering Pipeline

Automated pipeline for converting Minecraft schematics to high-quality 2D images using Amulet and Chunky.

## Quick Start

1. **Download Chunky** (one-time setup):
   - Visit: https://chunky-dev.github.io/docs/
   - Download `ChunkyLauncher.jar`
   - Place in `tools/chunky/ChunkyLauncher.jar`

2. **Run setup script**:
   ```bash
   ./scripts/setup_chunky_pipeline.sh
   ```

3. **Test with one schematic**:
   ```bash
   python scripts/test_render_pipeline.py data/schematics/10234.schematic
   ```

4. **Process all schematics**:
   ```bash
   python scripts/render_pipeline.py \
     --input_dir data/schematics \
     --output_dir data/rendered_images \
     --workers 4
   ```

## Features

- ✅ Automatic camera positioning for optimal framing
- ✅ Multi-view rendering (4 isometric angles per schematic)
- ✅ Parallel processing for speed
- ✅ Headless operation (no GUI required)
- ✅ High-quality path-traced rendering
- ✅ Handles various schematic formats (.schem, .schematic, .litematic)

## Output

Each schematic produces 4 images from different isometric views:
- `{name}_iso_0.png` - Southeast view
- `{name}_iso_1.png` - Southwest view
- `{name}_iso_2.png` - Northwest view  
- `{name}_iso_3.png` - Northeast view

## Configuration

Common options for `render_pipeline.py`:

```bash
--input_dir       # Directory with .schem files (required)
--output_dir      # Where to save images (required)
--workers 4       # Parallel processes
--width 512       # Image width
--height 512      # Image height  
--spp 256         # Rendering quality (samples per pixel)
--fov 70          # Camera field of view
--single_view     # Render only 1 view instead of 4
--limit N         # Process only first N schematics (for testing)
```

## Architecture

```
src/minecraft_voxel_flow/rendering/
├── __init__.py
├── amulet_helpers.py      # World creation & schematic loading
├── camera_calculator.py   # Camera positioning algorithm
└── chunky_renderer.py     # Chunky interface & rendering

scripts/
├── render_pipeline.py              # Main batch processing script
├── test_render_pipeline.py         # Component testing script
└── setup_chunky_pipeline.sh        # One-time setup script
```

## Documentation

- **Full Setup Guide**: `docs/CHUNKY_RENDERING_SETUP.md`
- **Implementation Plan**: `Schematic-to-Image-Pipeline-plan`
- **Troubleshooting**: See setup guide

## Requirements

- Python 3.8+
- Java 8+ (for Chunky)
- amulet-core
- numpy

## Status

✅ Core implementation complete
✅ All components tested (except actual rendering)
⚠️ Requires Chunky download to test rendering

See checklist in `Schematic-to-Image-Pipeline-plan` for detailed status.
