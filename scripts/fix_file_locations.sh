#!/bin/bash
# Move scraped files from wrong location to correct location

echo "====================================="
echo "Moving Scraped Files to Correct Location"
echo "====================================="

WRONG_DIR="/Users/moustholmes/data"
CORRECT_DIR="/Users/moustholmes/minecraft_voxel_flow/data"

# Check if wrong directory exists
if [ ! -d "$WRONG_DIR" ]; then
    echo "❌ No files found in wrong location ($WRONG_DIR)"
    echo "✅ Files are probably already in the correct location"
    exit 0
fi

# Create correct directory if it doesn't exist
mkdir -p "$CORRECT_DIR/schematics"

echo ""
echo "Source: $WRONG_DIR"
echo "Destination: $CORRECT_DIR"
echo ""

# Count files
SCHEMATIC_COUNT=$(ls -1 "$WRONG_DIR/schematics" 2>/dev/null | wc -l | tr -d ' ')
echo "Found $SCHEMATIC_COUNT schematic files to move"

# Move CSV file
if [ -f "$WRONG_DIR/schematics_metadata.csv" ]; then
    echo ""
    echo "Moving metadata CSV..."
    
    # If destination exists, backup first
    if [ -f "$CORRECT_DIR/schematics_metadata.csv" ]; then
        echo "  ⚠️  Backing up existing CSV to schematics_metadata.csv.backup"
        cp "$CORRECT_DIR/schematics_metadata.csv" "$CORRECT_DIR/schematics_metadata.csv.backup"
    fi
    
    mv "$WRONG_DIR/schematics_metadata.csv" "$CORRECT_DIR/schematics_metadata.csv"
    echo "  ✅ Metadata CSV moved"
fi

# Move schematic files
if [ -d "$WRONG_DIR/schematics" ] && [ "$(ls -A $WRONG_DIR/schematics)" ]; then
    echo ""
    echo "Moving schematic files..."
    mv "$WRONG_DIR/schematics"/* "$CORRECT_DIR/schematics/"
    echo "  ✅ $SCHEMATIC_COUNT files moved"
fi

# Clean up empty directories
if [ -d "$WRONG_DIR/schematics" ] && [ ! "$(ls -A $WRONG_DIR/schematics)" ]; then
    rmdir "$WRONG_DIR/schematics"
    echo "  🗑️  Removed empty schematics directory"
fi

if [ -d "$WRONG_DIR" ] && [ ! "$(ls -A $WRONG_DIR)" ]; then
    rmdir "$WRONG_DIR"
    echo "  🗑️  Removed empty data directory"
fi

echo ""
echo "====================================="
echo "✅ DONE!"
echo "====================================="
echo "Files are now in: $CORRECT_DIR"
echo ""
echo "Check with:"
echo "  ls -lh $CORRECT_DIR/schematics/ | head -20"
echo "  wc -l $CORRECT_DIR/schematics_metadata.csv"
