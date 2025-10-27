"""
Chunky renderer interface for generating high-fidelity Minecraft images.

This module provides functions to:
- Generate Chunky scene configuration files
- Execute headless rendering operations
"""

import os
import json
import subprocess
import sys
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def generate_scene_file(
    scene_dir: str,
    world_path: str,
    camera_params: Dict[str, Dict[str, float]],
    chunk_list: list,
    width: int = 512,
    height: int = 512,
    spp: int = 256,
    projection_mode: str = "PINHOLE",
    fov: float = 70.0,
    transparent_sky: bool = True
) -> str:
    """
    Generates a scene.json file for a Chunky render, including the chunk list.

    Args:
        scene_dir: Path to the scene directory (e.g., 'temp_scenes/my_render').
        world_path: Path to the .construction or Minecraft world file.
        camera_params: Dictionary containing camera 'position' and 'orientation'.
        chunk_list: A list of chunk coordinates to render, e.g., [[0, 0], [0, 1], [1, 0]].
        width: Output image width in pixels.
        height: Output image height in pixels.
        spp: Samples Per Pixel target for render quality.
        projection_mode: Camera projection type ("PINHOLE" or "PARALLEL").
        fov: Field of view in degrees.
        transparent_sky: If True, render with transparent background.

    Returns:
        Path to the generated scene.json file.

    Raises:
        IOError: If the scene file cannot be written.
    """
    scene_name = os.path.basename(scene_dir)

    # Construct the scene configuration
    scene_data = {
        "sdfVersion": 9,
        "name": scene_name,
        "width": width,
        "height": height,
        "exposure": 1.0,
        "postprocess": "NONE",
        "outputMode": "PNG",
        "renderTime": 0,
        "spp": 0,
        "sppTarget": spp,
        "pathTrace": True,
        "dumpFrequency": 0,  # Disable dumps for headless rendering
        "saveSnapshots": False,
        "saveDumps": False,  # Explicitly disable dump saving
        
        "camera": {
            "name": "camera_1",
            "projectionMode": projection_mode,
            "fov": fov,
            "dof": "Infinity",
            "focalOffset": 2.0,
            "position": camera_params.get("position", {"x": 0, "y": 70, "z": 0}),
            "orientation": camera_params.get("orientation", {"pitch": 0, "yaw": 0, "roll": 0})
        },
        
        "sun": {
            "enabled": True,
            "azimuth": 225.0,  # Angle from North (225° = Southwest)
            "altitude": 45.0,   # Angle from horizon
            "intensity": 1.0,
            "color": {"red": 1.0, "green": 1.0, "blue": 1.0}
        },
        
        "sky": {
            "skyYaw": 0.0,
            "skyMirrored": False,
            "skyLight": 1.0,
            "mode": "SIMULATED" if not transparent_sky else "BLACK",
            "horizonOffset": 0.1
        },
        
        "world": {
            "path": os.path.abspath(world_path),
            "dimension": 0  # 0 = Overworld, -1 = Nether, 1 = End
        },
        
        "chunkList": chunk_list,  # List of [x, z] chunk coordinates to load
        
        "yMin": 0,  # Minimum Y level to include in octree
        "yMax": 256,  # Maximum Y level to include in octree
        "yClipMin": 0,  # Minimum Y level for rendering
        "yClipMax": 256,  # Maximum Y level for rendering
        
        "transparentSky": transparent_sky,
        "renderActors": False,  # Do not render player models
        "entities": [],
        
        "emitterIntensity": 13.0,
        "emitterSamplingStrategy": "ONE",
        "biomeColorsEnabled": True,
        "stillWater": False,
        "clearWater": False,
        "atmosphereEnabled": False,
        "volumetricFogEnabled": False,
        "waterHeight": 0
    }

    # Create the scene directory if it doesn't exist
    os.makedirs(scene_dir, exist_ok=True)
    # Chunky expects the scene file to be named {scene_name}.json
    scene_file_path = os.path.join(scene_dir, f"{scene_name}.json")

    try:
        with open(scene_file_path, 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        logger.info(f"Generated scene file: {scene_file_path}")
        return scene_file_path

    except Exception as e:
        logger.error(f"Failed to write scene file to {scene_file_path}: {e}")
        raise IOError(f"Could not write scene file: {e}") from e


def render_scene_with_chunky(
    chunky_launcher_path: str,
    scene_dir: str,
    output_image_path: str,
    threads: int = 4,
    settings_dir: Optional[str] = None,
    timeout: Optional[int] = None
) -> bool:
    """
    Invokes Chunky to render a scene headlessly.

    Args:
        chunky_launcher_path: Path to ChunkyLauncher.jar.
        scene_dir: Path to the scene directory containing scene.json.
        output_image_path: Path to save the final PNG image.
        threads: Number of render threads to use.
        settings_dir: Optional custom Chunky settings directory.
        timeout: Optional timeout in seconds for the render process.

    Returns:
        True if render completed successfully, False otherwise.

    Raises:
        subprocess.CalledProcessError: If the Chunky process fails.
        FileNotFoundError: If ChunkyLauncher.jar is not found.
    """
    if not os.path.exists(chunky_launcher_path):
        raise FileNotFoundError(f"ChunkyLauncher.jar not found at: {chunky_launcher_path}")

    scene_name = os.path.basename(scene_dir)
    scene_json_path = os.path.join(scene_dir, f"{scene_name}.json")

    # Get Chunky home directory (where scenes are stored)
    chunky_home = os.path.expanduser("~/.chunky")
    
    # Determine the SPP from scene JSON to find the output file
    import json
    with open(scene_json_path, 'r') as f:
        scene_data = json.load(f)
    spp_target = scene_data.get('sppTarget', 100)

    # Build the command - call Chunky directly bypassing the launcher
    # This avoids JavaFX initialization issues
    chunky_lib_dir = os.path.join(chunky_home, "lib")
    classpath = ":".join([
        os.path.join(chunky_lib_dir, "chunky-core-2.4.6.jar"),
        os.path.join(chunky_lib_dir, "commons-math3-3.2.jar"),
        os.path.join(chunky_lib_dir, "fastutil-8.4.4.jar")
    ])
    
    command = [
        "java",
        f"-Dchunky.home={chunky_home}",
        "-cp", classpath,
        "se.llbit.chunky.main.Chunky",
        "-threads", str(threads),
        "-f",  # Force rendering even if scene has issues
        "-reload-chunks",  # Load chunks from the world without needing an octree
        "-render", os.path.abspath(scene_json_path)
    ]

    logger.info(f"Executing Chunky render: {' '.join(command)}")

    try:
        # Execute the render command
        # Note: Chunky output is captured but can be verbose, so we only log on errors
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        logger.info(f"Chunky render completed successfully")
        
        # Copy the output file from Chunky's snapshots directory to the desired location
        # IMPORTANT: Chunky's headless mode saves snapshots to:
        #   ~/.chunky/scenes/{scene_name}/snapshots/{scene_name}-{spp}.png
        # 
        # Snapshot behavior notes:
        # - Snapshots are automatically saved when rendering with saveSnapshots=true
        # - Chunky overwrites snapshots at the same SPP value for the same scene
        # - Using the same scene name for multiple renders allows Chunky to reuse
        #   the scene directory and properly save new snapshots
        # - Do NOT delete the snapshots directory between renders - Chunky needs it
        snapshot_dir = os.path.join(chunky_home, "scenes", scene_name, "snapshots")
        snapshot_file = os.path.join(snapshot_dir, f"{scene_name}-{spp_target}.png")
        
        # Poll for the snapshot file (Chunky may take a moment to write it)
        import time
        max_wait = 10  # seconds
        poll_interval = 0.5  # seconds
        elapsed = 0
        
        while not os.path.exists(snapshot_file) and elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        if os.path.exists(snapshot_file):
            import shutil
            # Verify it's the right file by checking modification time is recent
            mod_time = os.path.getmtime(snapshot_file)
            age = time.time() - mod_time
            if age > 60:  # Older than 1 minute - probably stale
                logger.warning(f"Snapshot file {snapshot_file} is {age:.1f}s old - may be from previous render")
            
            shutil.copy2(snapshot_file, output_image_path)
            file_size = os.path.getsize(output_image_path)
            logger.info(f"Output copied to: {output_image_path} ({file_size} bytes)")
            return True
        else:
            logger.error(f"Expected output file not found at {snapshot_file} after {max_wait}s wait")
            # List what files exist in the snapshots directory
            if os.path.exists(snapshot_dir):
                files = os.listdir(snapshot_dir)
                logger.info(f"Files in snapshots directory: {files}")
                # Only fail - don't use potentially wrong snapshot
                logger.error(f"Refusing to copy wrong snapshot - expected {scene_name}-{spp_target}.png")
            else:
                logger.error(f"Snapshots directory doesn't exist: {snapshot_dir}")
            return False

    except subprocess.TimeoutExpired as e:
        logger.error(f"Chunky render timed out after {timeout} seconds for scene {scene_name}")
        raise

    except subprocess.CalledProcessError as e:
        logger.error(f"Chunky render failed for {scene_name} with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during Chunky render: {e}")
        raise


def validate_chunky_setup(chunky_launcher_path: str) -> bool:
    """
    Validates that Chunky is properly installed and configured.

    Args:
        chunky_launcher_path: Path to ChunkyLauncher.jar.

    Returns:
        True if Chunky is ready to use, False otherwise.
    """
    if not os.path.exists(chunky_launcher_path):
        logger.error(f"ChunkyLauncher.jar not found at: {chunky_launcher_path}")
        return False

    try:
        # Try to get Chunky version
        result = subprocess.run(
            ["java", "-jar", chunky_launcher_path, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logger.info(f"Chunky validation successful: {result.stdout.strip()}")
        return True

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error(f"Chunky validation failed: {e}")
        return False
