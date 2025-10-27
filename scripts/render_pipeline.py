#!/usr/bin/env python3
"""
Automated Minecraft Schematic to 2D Image Rendering Pipeline.

This script converts a corpus of 3D Minecraft schematics into rendered 2D images
using Amulet-Core for world staging and Chunky for path-traced rendering.

Usage:
    python scripts/render_pipeline.py \\
        --input_dir ./data/schematics \\
        --output_dir ./data/rendered_images \\
        --chunky_path ./tools/chunky/ChunkyLauncher.jar \\
        --workers 4
"""

import os
import sys
import shutil
import glob
import argparse
import uuid
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.rendering import (
    create_void_world,
    load_schematic,
    get_schematic_bounds,
    paste_and_save,
    calculate_camera_parameters,
    ISOMETRIC_VECTORS,
    generate_scene_file,
    render_scene_with_chunky
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


def process_schematic(
    schematic_path: str,
    output_dir: str,
    temp_dir: str,
    chunky_path: str,
    width: int,
    height: int,
    spp: int,
    fov: float,
    render_all_views: bool = True
) -> dict:
    """
    Worker function to process a single schematic file.

    Args:
        schematic_path: Path to the input schematic file.
        output_dir: Directory to save rendered images.
        temp_dir: Directory for temporary files.
        chunky_path: Path to ChunkyLauncher.jar.
        width: Output image width.
        height: Output image height.
        spp: Samples per pixel for rendering quality.
        fov: Camera field of view in degrees.
        render_all_views: If True, render all 4 isometric views.

    Returns:
        Dictionary with processing results and statistics.
    """
    schematic_name = os.path.splitext(os.path.basename(schematic_path))[0]
    result = {
        'schematic': schematic_name,
        'success': False,
        'images_created': 0,
        'error': None
    }

    try:
        logger.info(f"Processing: {schematic_name}")

        # 1. Load schematic and get bounds
        schematic = load_schematic(schematic_path)
        bounds = get_schematic_bounds(schematic)

        # 2. Create and stage in a temporary void world
        temp_id = str(uuid.uuid4())
        world_path = os.path.join(temp_dir, 'worlds', f"{temp_id}")
        
        void_world = create_void_world(world_path)
        void_world.close()  # Close before reloading for paste
        target_location, world_bounds = paste_and_save(world_path, schematic, bounds)
        schematic.close()

        # 3. Determine which views to render
        views_to_render = ISOMETRIC_VECTORS if render_all_views else [ISOMETRIC_VECTORS[0]]
        aspect_ratio = width / height

        # 4. Render from each view
        for i, view_vec in enumerate(views_to_render):
            output_image_path = os.path.join(output_dir, f"{schematic_name}_iso_{i}.png")

            # Calculate camera parameters (use world_bounds for correct positioning)
            camera_params = calculate_camera_parameters(
                world_bounds, view_vec, fov, aspect_ratio
            )

            # Generate scene file
            scene_dir = os.path.join(temp_dir, 'scenes', f"{temp_id}_iso_{i}")
            generate_scene_file(
                scene_dir, world_path, camera_params,
                width, height, spp
            )

            # Render with Chunky
            render_success = render_scene_with_chunky(
                chunky_path, scene_dir, output_image_path,
                threads=2,  # Keep low for parallel processing
                timeout=300  # 5 minutes timeout per render
            )

            if render_success:
                result['images_created'] += 1
                logger.info(f"✓ Rendered view {i} for {schematic_name}")
            else:
                logger.warning(f"✗ Failed to render view {i} for {schematic_name}")

        result['success'] = result['images_created'] > 0
        return result

    except Exception as e:
        logger.error(f"Failed to process {schematic_name}: {e}", exc_info=True)
        result['error'] = str(e)
        return result


def setup_directories(output_dir: str, temp_dir: str, clean_temp: bool = True):
    """
    Sets up the required directory structure for the pipeline.

    Args:
        output_dir: Directory for output images.
        temp_dir: Directory for temporary files.
        clean_temp: If True, removes existing temp directory.
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Handle temp directory
    if clean_temp and os.path.exists(temp_dir):
        logger.info(f"Cleaning temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

    os.makedirs(os.path.join(temp_dir, 'worlds'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'scenes'), exist_ok=True)
    logger.info(f"Temporary directory: {temp_dir}")


def find_schematic_files(input_dir: str) -> List[str]:
    """
    Finds all schematic files in the input directory.

    Args:
        input_dir: Directory to search for schematics.

    Returns:
        List of absolute paths to schematic files.
    """
    patterns = ['*.schem', '*.schematic', '*.litematic']
    schematic_files = []

    for pattern in patterns:
        files = glob.glob(
            os.path.join(input_dir, '**', pattern),
            recursive=True
        )
        schematic_files.extend(files)

    return sorted(set(schematic_files))


def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(
        description="Automated Minecraft schematic to 2D image rendering pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Directory containing .schem files"
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Directory to save rendered .png images"
    )

    # Optional arguments
    parser.add_argument(
        "--chunky_path",
        default="./tools/chunky/ChunkyLauncher.jar",
        help="Path to ChunkyLauncher.jar"
    )
    parser.add_argument(
        "--temp_dir",
        default="./temp_render",
        help="Directory for temporary files"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="Number of parallel processes to run"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=512,
        help="Output image width in pixels"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=512,
        help="Output image height in pixels"
    )
    parser.add_argument(
        "--spp",
        type=int,
        default=256,
        help="Samples Per Pixel for Chunky render quality"
    )
    parser.add_argument(
        "--fov",
        type=float,
        default=70.0,
        help="Camera Field of View in degrees"
    )
    parser.add_argument(
        "--single_view",
        action="store_true",
        help="Render only one view instead of all 4 isometric views"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of schematics to process (for testing)"
    )
    parser.add_argument(
        "--keep_temp",
        action="store_true",
        help="Keep temporary files after completion"
    )

    args = parser.parse_args()

    # Validate Chunky path
    if not os.path.exists(args.chunky_path):
        logger.error(f"ChunkyLauncher.jar not found at: {args.chunky_path}")
        logger.error("Please download Chunky and place ChunkyLauncher.jar in tools/chunky/")
        logger.error("Download from: https://chunky-dev.github.io/docs/")
        sys.exit(1)

    # Setup directories
    setup_directories(args.output_dir, args.temp_dir, clean_temp=not args.keep_temp)

    # Find schematic files
    schematic_files = find_schematic_files(args.input_dir)

    if not schematic_files:
        logger.error(f"No schematic files found in {args.input_dir}")
        logger.error("Supported formats: .schem, .schematic, .litematic")
        sys.exit(1)

    # Apply limit if specified
    if args.limit:
        schematic_files = schematic_files[:args.limit]

    logger.info(f"Found {len(schematic_files)} schematics to process")
    logger.info(f"Using {args.workers} worker processes")
    logger.info(f"Rendering {'1 view' if args.single_view else '4 isometric views'} per schematic")

    # Process schematics in parallel
    results = []
    completed = 0
    
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Submit all jobs
        futures = {
            executor.submit(
                process_schematic,
                schematic_path,
                args.output_dir,
                args.temp_dir,
                args.chunky_path,
                args.width,
                args.height,
                args.spp,
                args.fov,
                not args.single_view
            ): schematic_path
            for schematic_path in schematic_files
        }

        # Process results as they complete
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1

            logger.info(
                f"Progress: {completed}/{len(schematic_files)} "
                f"({100 * completed / len(schematic_files):.1f}%)"
            )

    # Summary statistics
    successful = sum(1 for r in results if r['success'])
    total_images = sum(r['images_created'] for r in results)
    failed = len(results) - successful

    logger.info("=" * 70)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Total schematics processed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total images created: {total_images}")
    logger.info(f"Output directory: {args.output_dir}")

    # List failures
    if failed > 0:
        logger.warning("\nFailed schematics:")
        for r in results:
            if not r['success']:
                logger.warning(f"  - {r['schematic']}: {r['error']}")

    # Cleanup temp directory
    if not args.keep_temp:
        logger.info(f"Cleaning up temporary files: {args.temp_dir}")
        try:
            shutil.rmtree(args.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to clean temp directory: {e}")

    logger.info("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
