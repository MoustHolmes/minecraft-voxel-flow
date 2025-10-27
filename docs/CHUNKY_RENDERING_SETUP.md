# Chunky Rendering Pipeline Setup Guide

This guide will help you set up the Chunky-based rendering pipeline for converting Minecraft schematics to 2D images.

## Prerequisites

- Python 3.8 or higher
- Java Runtime Environment (JRE) 8 or higher
- At least 4GB of available RAM
- 1GB of free disk space for Chunky and temporary files

## Step 1: Install Python Dependencies

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install required packages
pip install amulet-core numpy
```

## Step 2: Download and Setup Chunky

### Option A: Manual Download (Recommended)

1. Visit the Chunky website: https://chunky-dev.github.io/docs/
2. Download `ChunkyLauncher.jar`
3. Place it in `tools/chunky/ChunkyLauncher.jar`

### Option B: Use the automated script

```bash
# Create directory
mkdir -p tools/chunky

# Download (you'll need to do this manually from the website)
# Place ChunkyLauncher.jar in tools/chunky/
```

### Initialize Chunky

Once you have ChunkyLauncher.jar, run these commands to set it up:

```bash
cd tools/chunky

# Update Chunky to the latest version
java -jar ChunkyLauncher.jar --update

# Download Minecraft 1.20.4 assets (or your target version)
java -jar ChunkyLauncher.jar -download-mc 1.20.4

# Verify installation
java -jar ChunkyLauncher.jar --version
```

## Step 3: Test the Pipeline

Test with a single schematic to verify everything works:

```bash
# Run the test script (skips rendering for quick validation)
python scripts/test_render_pipeline.py \
    data/schematics/10234.schematic \
    --skip_render

# Full test with rendering (takes longer)
python scripts/test_render_pipeline.py \
    data/schematics/10234.schematic \
    --output test_output.png
```

## Step 4: Run the Full Pipeline

Process all schematics in a directory:

```bash
python scripts/render_pipeline.py \
    --input_dir data/schematics \
    --output_dir data/rendered_images \
    --workers 4 \
    --width 512 \
    --height 512 \
    --spp 256
```

### Pipeline Options

- `--input_dir`: Directory containing .schem files
- `--output_dir`: Where to save rendered images
- `--workers`: Number of parallel processes (default: 4)
- `--width/height`: Output image dimensions (default: 512x512)
- `--spp`: Samples per pixel (quality, default: 256)
- `--fov`: Camera field of view in degrees (default: 70)
- `--single_view`: Render only 1 view instead of 4
- `--limit N`: Process only first N schematics (for testing)
- `--keep_temp`: Don't delete temporary files

## Troubleshooting

### Java Not Found
```bash
# Check Java installation
java -version

# If not installed, install Java:
# macOS: brew install openjdk@17
# Ubuntu: sudo apt install openjdk-17-jre
```

### Amulet-Core Import Errors
```bash
# Reinstall amulet-core
pip uninstall amulet-core
pip install amulet-core
```

### Chunky Rendering Fails
- Check that Minecraft assets are downloaded
- Verify the .construction world file was created
- Check the scene.json file is valid
- Look at pipeline.log for detailed errors

### Out of Memory Errors
- Reduce `--workers` to 2 or 1
- Reduce `--spp` to 100 or lower
- Process schematics in smaller batches using `--limit`

## Performance Tuning

### For Speed
- Lower `--spp` to 100-128 (faster, noisier images)
- Use `--single_view` (1 image per schematic)
- Increase `--workers` (if you have CPU cores)

### For Quality
- Increase `--spp` to 512-1024 (slower, cleaner images)
- Use default 4-view isometric rendering
- Adjust `--fov` for different framing

## Expected Output

For each schematic, the pipeline will create:
- 1 image (with `--single_view`)
- 4 images (default: 4 isometric angles)

Output naming: `{schematic_name}_iso_{0-3}.png`

Example:
- `castle_iso_0.png` (Southeast view)
- `castle_iso_1.png` (Southwest view)
- `castle_iso_2.png` (Northwest view)
- `castle_iso_3.png` (Northeast view)

## Directory Structure

```
minecraft_voxel_flow/
├── tools/
│   └── chunky/
│       └── ChunkyLauncher.jar
├── data/
│   ├── schematics/          # Input schematics
│   └── rendered_images/      # Output images
├── temp_render/              # Temporary files (auto-deleted)
│   ├── worlds/               # .construction files
│   └── scenes/               # scene.json files
└── scripts/
    ├── render_pipeline.py
    └── test_render_pipeline.py
```

## Next Steps

After successful rendering:
1. Review output images in `data/rendered_images/`
2. Adjust camera parameters if needed
3. Process your full dataset
4. Use the rendered images for training your model

## Additional Resources

- Chunky Documentation: https://chunky-dev.github.io/docs/
- Amulet-Core: https://github.com/Amulet-Team/Amulet-Core
- Scene JSON Reference: https://chunky-dev.github.io/docs/reference/scene/
