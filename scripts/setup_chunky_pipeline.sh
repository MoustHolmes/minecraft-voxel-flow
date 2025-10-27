#!/bin/bash
# Setup script for Chunky Rendering Pipeline

set -e

echo "=========================================="
echo "Chunky Rendering Pipeline Setup"
echo "=========================================="

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Check Java
echo "Checking Java..."
if ! command -v java &> /dev/null; then
    echo "❌ Java is not installed"
    echo "Please install Java: brew install openjdk@17"
    exit 1
fi
echo "✓ Java found: $(java -version 2>&1 | head -1)"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p tools/chunky
mkdir -p data/rendered_images
mkdir -p temp_render/worlds
mkdir -p temp_render/scenes
echo "✓ Directories created"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

pip install -q amulet-core numpy
echo "✓ Python dependencies installed"

# Check for Chunky
echo ""
CHUNKY_PATH="tools/chunky/ChunkyLauncher.jar"
if [ -f "$CHUNKY_PATH" ]; then
    echo "✓ ChunkyLauncher.jar found"
    
    # Initialize Chunky
    echo ""
    echo "Initializing Chunky..."
    cd tools/chunky
    
    echo "  Updating Chunky..."
    java -jar ChunkyLauncher.jar --update
    
    echo "  Downloading Minecraft 1.20.4 assets..."
    java -jar ChunkyLauncher.jar -download-mc 1.20.4
    
    cd ../..
    echo "✓ Chunky initialized"
else
    echo "⚠️  ChunkyLauncher.jar not found"
    echo ""
    echo "Please download it manually:"
    echo "1. Visit: https://chunky-dev.github.io/docs/getting_started/installing_chunky/"
    echo "2. Download ChunkyLauncher.jar"
    echo "3. Place it at: $CHUNKY_PATH"
    echo ""
    echo "Then run this script again to complete setup."
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Test the pipeline:"
echo "  python scripts/test_render_pipeline.py data/schematics/10234.schematic --skip_render"
echo ""
echo "Run full pipeline:"
echo "  python scripts/render_pipeline.py --input_dir data/schematics --output_dir data/rendered_images"
echo ""
echo "For more information, see: docs/CHUNKY_RENDERING_SETUP.md"
