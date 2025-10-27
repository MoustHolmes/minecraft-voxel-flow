#!/usr/bin/env python3
"""
Test script for the schematic rendering pipeline.

This script tests each component of the pipeline with a single schematic:
1. Amulet world creation and schematic loading
2. Camera parameter calculation
3. Chunky scene file generation
4. Rendering (optional, can be skipped for quick tests)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.rendering import (
    create_void_world,
    load_schematic,
    get_schematic_bounds,
    paste_and_save,
    calculate_camera_parameters,
    get_chunks_for_bounds,
    ISOMETRIC_VECTORS,
    generate_scene_file,
    render_scene_with_chunky
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_amulet_functions(schematic_path: str, temp_dir: str):
    """Test Amulet-related functions."""
    logger.info("=" * 60)
    logger.info("Testing Amulet Functions")
    logger.info("=" * 60)

    # Test 1: Load schematic
    logger.info("\n1. Loading schematic...")
    schematic = load_schematic(schematic_path)
    logger.info(f"   ✓ Schematic loaded: {schematic_path}")
    logger.info(f"   Dimensions: {schematic.dimensions}")

    # Test 2: Get bounds
    logger.info("\n2. Extracting bounding box...")
    bounds = get_schematic_bounds(schematic)
    logger.info(f"   ✓ Bounds extracted:")
    logger.info(f"     Min: {bounds.min}")
    logger.info(f"     Max: {bounds.max}")
    logger.info(f"     Size: ({bounds.size_x}, {bounds.size_y}, {bounds.size_z})")

    # Test 3: Create void world
    logger.info("\n3. Creating void world...")
    world_path = os.path.join(temp_dir, "test_world")
    os.makedirs(temp_dir, exist_ok=True)
    void_world = create_void_world(world_path)
    void_world.close()  # Close the wrapper, we'll reload it for pasting
    logger.info(f"   ✓ Void world created: {world_path}")

    # Test 4: Paste and save
    logger.info("\n4. Pasting schematic into world...")
    target_location, world_bounds = paste_and_save(world_path, schematic, bounds)
    schematic.close()
    logger.info(f"   ✓ Schematic pasted and world saved")
    logger.info(f"   Target location: {target_location}")
    logger.info(f"   World bounds: min={world_bounds.min}, max={world_bounds.max}")

    # Verify file exists
    if os.path.exists(world_path):
        file_size = os.path.getsize(world_path)
        logger.info(f"   World file size: {file_size} bytes")
    else:
        logger.error(f"   ✗ World file not created!")
        return None, None, None

    return world_path, bounds, world_bounds


def test_camera_calculation(bounds):
    """Test camera parameter calculation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Camera Calculation")
    logger.info("=" * 60)

    for i, view_vec in enumerate(ISOMETRIC_VECTORS):
        logger.info(f"\nView {i}: {view_vec}")
        camera_params = calculate_camera_parameters(
            bounds, view_vec, fov_degrees=70.0, aspect_ratio=1.0
        )
        logger.info(f"  Position: ({camera_params['position']['x']:.2f}, "
                   f"{camera_params['position']['y']:.2f}, "
                   f"{camera_params['position']['z']:.2f})")
        logger.info(f"  Orientation: pitch={camera_params['orientation']['pitch']:.2f}°, "
                   f"yaw={camera_params['orientation']['yaw']:.2f}°")

    return camera_params


def test_scene_generation(world_path: str, bounds, temp_dir: str):
    """Test Chunky scene file generation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Scene File Generation")
    logger.info("=" * 60)

    scene_dir = os.path.join(temp_dir, "test_scene")
    
    # Calculate which chunks the schematic occupies
    chunk_list = get_chunks_for_bounds(bounds)
    logger.info(f"\nSchematic occupies {len(chunk_list)} chunks")
    logger.info(f"Chunks: {chunk_list if len(chunk_list) <= 10 else chunk_list[:10] + ['...']}")
    
    # Calculate camera for first view
    camera_params = calculate_camera_parameters(
        bounds, ISOMETRIC_VECTORS[0], fov_degrees=70.0, aspect_ratio=1.0
    )

    # Generate scene file
    logger.info("\nGenerating scene.json...")
    scene_file = generate_scene_file(
        scene_dir, world_path, camera_params, chunk_list,
        width=512, height=512, spp=100
    )

    logger.info(f"✓ Scene file created: {scene_file}")

    # Read and display key parts
    import json
    with open(scene_file, 'r') as f:
        scene_data = json.load(f)

    logger.info(f"\nScene configuration:")
    logger.info(f"  Name: {scene_data.get('name')}")
    logger.info(f"  Size: {scene_data.get('width')}x{scene_data.get('height')}")
    logger.info(f"  SPP Target: {scene_data.get('sppTarget')}")
    logger.info(f"  World: {scene_data.get('world', {}).get('path')}")

    return scene_dir


def test_render(chunky_path: str, scene_dir: str, output_path: str):
    """Test actual Chunky rendering (optional)."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Chunky Rendering")
    logger.info("=" * 60)

    if not os.path.exists(chunky_path):
        logger.error(f"✗ ChunkyLauncher.jar not found at: {chunky_path}")
        logger.error("  Please download Chunky to test rendering")
        return False

    logger.info("\nStarting render (this may take a few minutes)...")
    try:
        # Use absolute paths for Chunky
        abs_output_path = os.path.abspath(output_path)
        success = render_scene_with_chunky(
            chunky_path, scene_dir, abs_output_path,
            threads=2, timeout=180
        )

        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"✓ Render completed successfully!")
            logger.info(f"  Output: {output_path}")
            logger.info(f"  Size: {file_size} bytes")
            return True
        else:
            logger.error("✗ Render failed or output not created")
            return False

    except Exception as e:
        logger.error(f"✗ Render error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test the schematic rendering pipeline components"
    )
    parser.add_argument(
        "schematic",
        help="Path to a test schematic file"
    )
    parser.add_argument(
        "--output",
        default="./test_render.png",
        help="Output image path"
    )
    parser.add_argument(
        "--temp_dir",
        default="./temp_test",
        help="Temporary directory for test files"
    )
    parser.add_argument(
        "--chunky_path",
        default="./tools/chunky/ChunkyLauncher.jar",
        help="Path to ChunkyLauncher.jar"
    )
    parser.add_argument(
        "--skip_render",
        action="store_true",
        help="Skip the actual rendering step (for quick tests)"
    )

    args = parser.parse_args()

    # Validate schematic file
    if not os.path.exists(args.schematic):
        logger.error(f"Schematic file not found: {args.schematic}")
        sys.exit(1)

    logger.info(f"Testing pipeline with: {args.schematic}")

    try:
        # Test Amulet functions
        world_path, bounds, world_bounds = test_amulet_functions(args.schematic, args.temp_dir)
        if not world_path or not bounds or not world_bounds:
            logger.error("Amulet tests failed!")
            sys.exit(1)

        # Test camera calculation (use world_bounds for correct camera positioning)
        test_camera_calculation(world_bounds)

        # Test scene generation (use world_bounds for correct camera positioning)
        scene_dir = test_scene_generation(world_path, world_bounds, args.temp_dir)

        # Test rendering (optional)
        if not args.skip_render:
            render_success = test_render(args.chunky_path, scene_dir, args.output)
        else:
            logger.info("\n(Skipping render test as requested)")
            render_success = True

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info("✓ Amulet functions: PASSED")
        logger.info("✓ Camera calculation: PASSED")
        logger.info("✓ Scene generation: PASSED")
        
        if args.skip_render:
            logger.info("○ Rendering: SKIPPED")
        elif render_success:
            logger.info("✓ Rendering: PASSED")
        else:
            logger.info("✗ Rendering: FAILED")

        logger.info(f"\nTest files in: {args.temp_dir}")
        
        if render_success and not args.skip_render:
            logger.info(f"Output image: {args.output}")

        sys.exit(0 if (args.skip_render or render_success) else 1)

    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
