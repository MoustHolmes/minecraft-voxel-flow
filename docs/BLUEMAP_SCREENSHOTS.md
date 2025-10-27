# BlueMap Screenshot Automation

This guide shows how to use BlueMap to automatically render screenshots of Minecraft schematics.

## Installation

### 1. Install BlueMap CLI

Download the BlueMap CLI jar file:

```bash
# Create bluemap directory
mkdir -p tools/bluemap
cd tools/bluemap

# Download BlueMap CLI (check https://github.com/BlueMap-Minecraft/BlueMap/releases for latest)
wget https://github.com/BlueMap-Minecraft/BlueMap/releases/download/v3.20/BlueMap-3.20-cli.jar -O bluemap-cli.jar

# Or download manually from: https://bluemap.bluecolored.de/wiki/getting-started/Installation.html
```

### 2. Install Python Dependencies

```bash
pip install pillow requests
```

## Usage

### Basic Screenshot

```python
from scripts.bluemap_screenshots import BlueMapRenderer

renderer = BlueMapRenderer()

# Render a single schematic
renderer.render_schematic(
    "data/schematics/10234.schematic",
    output_path="screenshots/10234.png",
    camera_distance=100,
    camera_angle=45
)
```

### Batch Rendering

```python
# Render all schematics
renderer.batch_render_schematics(
    "data/schematics",
    output_dir="screenshots",
    max_schematics=10  # Limit for testing
)
```

## Configuration

Edit `config/bluemap_config.yaml` to customize:
- Image resolution
- Camera angles
- Lighting settings
- Background color

## Examples

See `notebooks/bluemap_screenshots.ipynb` for interactive examples.

## References

- BlueMap Python Screenshots: https://bluemap.bluecolored.de/community/python-screenshots.html
- BlueMap CLI Installation: https://bluemap.bluecolored.de/wiki/getting-started/Installation.html
