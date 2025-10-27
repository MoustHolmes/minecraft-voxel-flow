"""
Rendering module for converting Minecraft schematics to 2D images.

This module provides tools for:
- Loading and staging schematics in temporary worlds (Amulet)
- Calculating optimal camera positions for framing structures
- Rendering high-fidelity images using Chunky path tracer
"""

from .amulet_helpers import (
    create_void_world,
    load_schematic,
    get_schematic_bounds,
    paste_and_save
)
from .camera_calculator import (
    calculate_camera_parameters,
    calculate_target_point,
    get_chunks_for_bounds,
    ISOMETRIC_VECTORS
)
from .chunky_renderer import (
    generate_scene_file,
    render_scene_with_chunky
)

__all__ = [
    'create_void_world',
    'load_schematic',
    'get_schematic_bounds',
    'paste_and_save',
    'calculate_camera_parameters',
    'ISOMETRIC_VECTORS',
    'generate_scene_file',
    'render_scene_with_chunky'
]
