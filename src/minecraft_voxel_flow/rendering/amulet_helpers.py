"""
Amulet-Core helper functions for schematic processing.

This module provides utilities for:
- Creating empty void worlds
- Loading schematic files
- Extracting bounding boxes
- Pasting structures into staging worlds
"""

import os
import logging
from typing import Tuple

import amulet
from amulet.api.level import World, Structure
from amulet.api.selection import SelectionGroup, SelectionBox

logger = logging.getLogger(__name__)


def create_void_world(
    world_path: str,
    platform: str = "java",
    version: Tuple[int, int, int] = (1, 19, 4)
):
    """
    Creates a new, empty Amulet world object in Anvil format.

    Args:
        path: The directory path where the world will be created.
        platform: The target Minecraft platform (e.g., "java", "bedrock").
        version: The target Minecraft version tuple (e.g., (1, 20, 4)).

    Returns:
        The newly created, empty world object.

    Raises:
        IOError: If the world cannot be created.
    """
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(world_path), exist_ok=True)

    try:
        # Import the anvil world format
        from amulet.level.formats.anvil_world import AnvilFormat
        
        # Create a format wrapper instance for an Anvil world
        wrapper = AnvilFormat(world_path)

        # Create and open the new world
        initial_bounds = SelectionGroup()
        wrapper.create_and_open(platform, version, initial_bounds, overwrite=True)

        logger.info(f"Created void world at {world_path}")
        return wrapper

    except Exception as e:
        logger.error(f"Failed to create void world at {world_path}: {e}")
        raise


def load_schematic(path: str) -> Structure:
    """
    Loads a schematic file into an Amulet Structure object.

    Args:
        path: The file path to the schematic file (.schem, .schematic, etc.).

    Returns:
        The loaded schematic as an Amulet Structure object.

    Raises:
        FileNotFoundError: If the schematic file does not exist.
        ValueError: If the file format is not supported.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schematic file not found at: {path}")

    try:
        level = amulet.load_level(path)
        logger.info(f"Loaded schematic from {path}")
        return level
    except Exception as e:
        logger.error(f"Failed to load schematic from {path}: {e}")
        raise ValueError(f"Unsupported or corrupted schematic file: {path}") from e


def get_schematic_bounds(schematic: Structure) -> SelectionBox:
    """
    Extracts the primary bounding box from a loaded schematic.

    Args:
        schematic: The Amulet Structure object.

    Returns:
        The bounding box of the structure.

    Raises:
        ValueError: If the schematic has no dimensions or is empty.
    """
    if not schematic.dimensions:
        raise ValueError("Schematic does not contain any dimensions.")

    # Get the selection group for the primary dimension
    # For schematics, this is usually the only dimension
    dimension = list(schematic.dimensions)[0]
    selection_group = schematic.bounds(dimension)

    if not selection_group.selection_boxes:
        raise ValueError("Schematic bounding box is empty.")

    # For simplicity, we use the first bounding box
    # A more robust implementation might merge multiple boxes if present
    bounds = selection_group.selection_boxes[0]
    
    logger.info(f"Schematic bounds: min={bounds.min}, max={bounds.max}, size=({bounds.size_x}, {bounds.size_y}, {bounds.size_z})")
    return bounds


def paste_and_save(
    world_path: str,
    schematic: Structure,
    bounds: SelectionBox,
    center_at_origin: bool = True
) -> tuple:
    """
    Pastes a schematic into a world and saves the world to disk.

    By default, centers the schematic's footprint at the world origin (x=0, z=0).

    Args:
        world_path: Path to the world directory.
        schematic: The source schematic object.
        bounds: The bounding box of the schematic.
        center_at_origin: If True, centers the schematic at (0, y, 0).

    Returns:
        Tuple of (target_location, world_bounds) where:
            target_location: The (x, y, z) coordinates where the schematic was pasted
            world_bounds: SelectionBox representing the schematic's location in world coordinates

    Raises:
        RuntimeError: If the paste or save operation fails.
    """
    try:
        # Load the world that was just created
        world = amulet.load_level(world_path)
        
        # Get the dimensions
        world_dimension = "minecraft:overworld"
        schematic_dimension = list(schematic.dimensions)[0]

        if center_at_origin:
            # Calculate the center of the schematic's base
            center_x = bounds.min_x + bounds.size_x // 2
            center_z = bounds.min_z + bounds.size_z // 2

            # Calculate the target location to center the schematic at (0, y, 0)
            # The y-coordinate is kept as is, so the structure isn't moved vertically
            target_location = (-center_x, bounds.min_y, -center_z)
        else:
            target_location = (0, 0, 0)

        logger.info(f"Pasting schematic to world at location {target_location}")

        # Perform the paste operation
        # Note: paste expects a SelectionGroup, so wrap the SelectionBox
        selection_group = SelectionGroup(bounds)
        
        world.paste(
            schematic,
            schematic_dimension,
            selection_group,
            world_dimension,
            target_location,
            include_blocks=True,
            include_entities=False
        )

        # Save changes to disk
        world.save()
        logger.info("World saved successfully")
        
        # Calculate world bounds (where the schematic actually is in world coordinates)
        world_bounds = SelectionBox(
            (target_location[0], target_location[1], target_location[2]),
            (target_location[0] + bounds.size_x, target_location[1] + bounds.size_y, target_location[2] + bounds.size_z)
        )

    except Exception as e:
        logger.error(f"Failed to paste and save schematic: {e}")
        raise RuntimeError(f"Paste operation failed: {e}") from e
    finally:
        # Always try to close the world
        try:
            world.close()
            logger.info("World closed")
        except Exception as e:
            logger.warning(f"Failed to close world: {e}")
            
    return target_location, world_bounds
