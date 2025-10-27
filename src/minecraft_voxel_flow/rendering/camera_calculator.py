"""
Camera positioning and orientation calculator for Minecraft structures.

This module calculates optimal camera parameters to frame structures
using isometric or perspective projections.
"""

import math
import logging
from typing import Dict, Tuple, List

import numpy as np
from amulet.api.selection import SelectionBox

logger = logging.getLogger(__name__)

# Standard isometric view vectors (cardinal directions)
# Each vector points from a corner of a cube towards its center
# Format: (x, y, z) where y-component determines pitch angle
ISOMETRIC_VECTORS: List[Tuple[float, float, float]] = [
    (-1.0, -0.8, -1.0),  # Southeast
    (1.0, -0.8, -1.0),   # Southwest
    (1.0, -0.8, 1.0),    # Northwest
    (-1.0, -0.8, 1.0),   # Northeast
]


def calculate_camera_parameters(
    bounds: SelectionBox,
    view_vector: Tuple[float, float, float],
    fov_degrees: float = 70.0,
    aspect_ratio: float = 1.0,
    margin_factor: float = 1.15
) -> Dict[str, Dict[str, float]]:
    """
    Calculates camera position and orientation to frame a bounding box.

    This function computes the optimal camera placement to ensure the entire
    structure fits within the viewport when rendered.

    Args:
        bounds: The bounding box of the object to frame.
        view_vector: The direction vector for the camera view (e.g., (-1, -0.8, -1)).
        fov_degrees: The camera's vertical field of view in degrees.
        aspect_ratio: The width/height aspect ratio of the output image.
        margin_factor: Additional space around the object (1.0 = tight fit, 1.2 = 20% margin).

    Returns:
        A dictionary containing 'position' and 'orientation' for scene.json.
        Format:
        {
            'position': {'x': float, 'y': float, 'z': float},
            'orientation': {'pitch': float, 'yaw': float, 'roll': float}
        }
    """
    # Calculate the center of the bounding box
    center = np.array([
        bounds.min_x + bounds.size_x / 2.0,
        bounds.min_y + bounds.size_y / 2.0,
        bounds.min_z + bounds.size_z / 2.0
    ])

    # Calculate the size vector
    size = np.array([bounds.size_x, bounds.size_y, bounds.size_z])

    # Calculate the radius of the bounding sphere
    # This is the distance from the center to the farthest corner
    radius = np.linalg.norm(size) / 2.0

    # Handle edge case of single block or very small structures
    if radius < 1.0:
        radius = 1.0
        logger.warning(f"Very small structure detected (radius={radius}), using minimum radius of 1.0")

    # Convert FOV to radians
    fov_rad = math.radians(fov_degrees)

    # Adjust for aspect ratio to ensure the object fits in the wider dimension
    # For landscape images (aspect > 1), we need more horizontal coverage
    effective_fov = fov_rad
    if aspect_ratio > 1.0:
        # Calculate the effective vertical FOV needed
        effective_fov = 2 * math.atan(math.tan(fov_rad / 2) * aspect_ratio)
    elif aspect_ratio < 1.0:
        # Portrait mode
        effective_fov = 2 * math.atan(math.tan(fov_rad / 2) / aspect_ratio)

    # Calculate the required distance from the center
    # Using the formula: distance = radius / sin(fov/2)
    if math.sin(effective_fov / 2) > 0:
        distance = radius / math.sin(effective_fov / 2)
    else:
        distance = radius * 2  # Fallback for very small FOV

    # Apply margin factor for additional spacing
    distance *= margin_factor

    # Normalize the view vector
    view_vector_arr = np.array(view_vector)
    view_vector_norm = view_vector_arr / np.linalg.norm(view_vector_arr)

    # Calculate camera position
    # Camera is positioned opposite to the view direction
    position = center - (view_vector_norm * distance)

    # Calculate yaw and pitch for Chunky's orientation format
    # Chunky uses: yaw = rotation around Y-axis, pitch = up/down rotation
    # Calculate direction FROM camera TO center (what camera is looking at)
    look_direction = center - position
    dx, dy, dz = look_direction

    # Yaw: rotation from positive X axis (in degrees)
    # atan2(dz, dx) gives angle in XZ plane
    yaw = math.degrees(math.atan2(dz, dx))

    # Pitch: rotation from horizontal plane (in degrees)
    # Negative pitch means looking down
    horizontal_dist = math.sqrt(dx**2 + dz**2)
    if horizontal_dist > 0:
        pitch = math.degrees(math.atan2(dy, horizontal_dist))
    else:
        pitch = -90.0 if dy < 0 else 90.0  # Looking straight up or down

    logger.info(
        f"Camera calculated: pos=({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}), "
        f"pitch={pitch:.2f}°, yaw={yaw:.2f}°, distance={distance:.2f}"
    )

    return {
        "position": {
            "x": float(position[0]),
            "y": float(position[1]),
            "z": float(position[2])
        },
        "orientation": {
            "pitch": float(pitch),
            "yaw": float(yaw),
            "roll": 0.0  # No roll for standard views
        }
    }


def get_chunks_for_bounds(bounds: SelectionBox) -> List[List[int]]:
    """
    Calculates a list of all chunk coordinates that a bounding box intersects.

    A Minecraft chunk is a 16x16 area on the X and Z axes. This function converts
    the schematic's block-coordinate bounding box into a list of chunk coordinates.

    Args:
        bounds: The Amulet SelectionBox of the schematic.

    Returns:
        A list of chunk coordinates, e.g., [[-1, 0], [-1, 1], [0, 0], [0, 1]].
        Format matches Chunky's chunkList requirement: array of [x, z] integer arrays.

    Example:
        >>> bounds = SelectionBox((0, 0, 0), (32, 64, 48))
        >>> chunks = get_chunks_for_bounds(bounds)
        >>> print(chunks)  # [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]
    """
    # Convert min/max block coordinates to chunk coordinates
    # Chunk coordinate = floor(block_coordinate / 16)
    min_chunk_x = bounds.min_x // 16
    max_chunk_x = math.ceil(bounds.max_x / 16)
    min_chunk_z = bounds.min_z // 16
    max_chunk_z = math.ceil(bounds.max_z / 16)

    chunk_list = []
    for x in range(min_chunk_x, max_chunk_x):
        for z in range(min_chunk_z, max_chunk_z):
            chunk_list.append([x, z])

    logger.info(
        f"Calculated {len(chunk_list)} chunks for bounds "
        f"({bounds.min_x}, {bounds.min_z}) to ({bounds.max_x}, {bounds.max_z}): "
        f"chunks ({min_chunk_x}, {min_chunk_z}) to ({max_chunk_x-1}, {max_chunk_z-1})"
    )

    return chunk_list


def calculate_target_point(bounds: SelectionBox) -> Dict[str, float]:
    """
    Calculates the center point of a bounding box for camera targeting.

    Args:
        bounds: The bounding box of the structure.

    Returns:
        A dictionary with 'x', 'y', 'z' coordinates of the center point.
    """
    return {
        "x": float(bounds.min_x + bounds.size_x / 2.0),
        "y": float(bounds.min_y + bounds.size_y / 2.0),
        "z": float(bounds.min_z + bounds.size_z / 2.0)
    }
