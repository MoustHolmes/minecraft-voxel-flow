"""VoxelProcessor: Process and transform voxel arrays."""

from typing import Tuple, Optional, Dict, List

import numpy as np
from scipy import ndimage


class VoxelProcessor:
    """Process and transform voxel arrays for ML training.
    
    Provides utilities for:
    - Normalization and resizing
    - Cropping and padding
    - Air removal
    - Block encoding simplification
    - Data augmentation (rotations, flips)
    """
    
    def __init__(self):
        """Initialize the voxel processor."""
        pass
    
    def remove_air(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Dict[int, str]
    ) -> Tuple[np.ndarray, Tuple[int, int, int]]:
        """Remove empty air space around the structure.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Dict mapping block IDs to block names
            
        Returns:
            Tuple of (cropped_array, offset):
                - cropped_array: Voxel array with air removed
                - offset: (x, y, z) offset of cropped region
        """
        # Find all air block IDs
        air_ids = [bid for bid, name in palette_reverse.items() if 'air' in name.lower()]
        
        # Create mask of non-air blocks
        non_air_mask = ~np.isin(voxel_array, air_ids)
        
        # Find bounding box
        coords = np.where(non_air_mask)
        
        if len(coords[0]) == 0:
            # All air, return minimal array
            return np.zeros((1, 1, 1), dtype=voxel_array.dtype), (0, 0, 0)
        
        min_x, max_x = coords[0].min(), coords[0].max() + 1
        min_y, max_y = coords[1].min(), coords[1].max() + 1
        min_z, max_z = coords[2].min(), coords[2].max() + 1
        
        # Crop to bounding box
        cropped = voxel_array[min_x:max_x, min_y:max_y, min_z:max_z]
        offset = (min_x, min_y, min_z)
        
        return cropped, offset
    
    def resize(
        self,
        voxel_array: np.ndarray,
        target_size: Tuple[int, int, int],
        method: str = 'nearest'
    ) -> np.ndarray:
        """Resize voxel array to target dimensions.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            target_size: Target (width, height, depth)
            method: Interpolation method ('nearest', 'linear')
            
        Returns:
            Resized voxel array
        """
        current_size = voxel_array.shape
        zoom_factors = [t / c for t, c in zip(target_size, current_size)]
        
        # Use scipy zoom for resizing
        order = 0 if method == 'nearest' else 1
        resized = ndimage.zoom(voxel_array, zoom_factors, order=order)
        
        return resized.astype(voxel_array.dtype)
    
    def pad_to_size(
        self,
        voxel_array: np.ndarray,
        target_size: Tuple[int, int, int],
        air_id: int = 0,
        center: bool = True
    ) -> np.ndarray:
        """Pad voxel array to target size with air blocks.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            target_size: Target (width, height, depth)
            air_id: Block ID to use for padding
            center: If True, center the structure; otherwise pad at origin
            
        Returns:
            Padded voxel array
        """
        current_size = voxel_array.shape
        
        # Check if already at target size
        if current_size == target_size:
            return voxel_array
        
        # Calculate padding
        pad_amounts = []
        for current, target in zip(current_size, target_size):
            if current > target:
                raise ValueError(
                    f"Current size {current_size} exceeds target {target_size}. "
                    "Use resize() first."
                )
            
            total_pad = target - current
            if center:
                pad_before = total_pad // 2
                pad_after = total_pad - pad_before
            else:
                pad_before = 0
                pad_after = total_pad
            
            pad_amounts.append((pad_before, pad_after))
        
        # Pad with air
        padded = np.pad(voxel_array, pad_amounts, mode='constant', constant_values=air_id)
        
        return padded
    
    def normalize_size(
        self,
        voxel_array: np.ndarray,
        target_size: Tuple[int, int, int],
        palette_reverse: Dict[int, str],
        remove_air_first: bool = True
    ) -> np.ndarray:
        """Normalize voxel array to target size.
        
        First removes air, then either pads or resizes to target.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            target_size: Target (width, height, depth)
            palette_reverse: Dict mapping block IDs to block names
            remove_air_first: If True, remove air before resizing
            
        Returns:
            Normalized voxel array
        """
        # Remove air if requested
        if remove_air_first:
            voxel_array, _ = self.remove_air(voxel_array, palette_reverse)
        
        current_size = voxel_array.shape
        
        # If structure is larger than target, resize
        if any(c > t for c, t in zip(current_size, target_size)):
            voxel_array = self.resize(voxel_array, target_size)
        else:
            # Otherwise pad
            voxel_array = self.pad_to_size(voxel_array, target_size)
        
        return voxel_array
    
    def rotate_90(
        self,
        voxel_array: np.ndarray,
        axis: int = 1,
        k: int = 1
    ) -> np.ndarray:
        """Rotate voxel array 90 degrees around an axis.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            axis: Axis to rotate around (0=X, 1=Y, 2=Z)
            k: Number of 90-degree rotations
            
        Returns:
            Rotated voxel array
        """
        # Map axis to rotation planes
        planes = {
            0: (1, 2),  # Rotate around X (YZ plane)
            1: (0, 2),  # Rotate around Y (XZ plane)
            2: (0, 1),  # Rotate around Z (XY plane)
        }
        
        return np.rot90(voxel_array, k=k, axes=planes[axis])
    
    def flip(
        self,
        voxel_array: np.ndarray,
        axis: int
    ) -> np.ndarray:
        """Flip voxel array along an axis.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            axis: Axis to flip (0=X, 1=Y, 2=Z)
            
        Returns:
            Flipped voxel array
        """
        return np.flip(voxel_array, axis=axis)
    
    def simplify_palette(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Dict[int, str],
        block_mappings: Optional[Dict[str, str]] = None
    ) -> Tuple[np.ndarray, Dict[int, str]]:
        """Simplify block palette by grouping similar blocks.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Dict mapping block IDs to block names
            block_mappings: Optional custom mappings (old_name -> new_name)
            
        Returns:
            Tuple of (simplified_array, new_palette_reverse)
        """
        if block_mappings is None:
            # Default: group by base block type (ignore block states)
            block_mappings = {}
            for block_name in palette_reverse.values():
                # Extract base type (before '[')
                base_type = block_name.split('[')[0]
                block_mappings[block_name] = base_type
        
        # Create new palette
        new_palette = {}
        new_palette_reverse = {}
        next_id = 0
        
        # Remap blocks
        id_mapping = {}  # old_id -> new_id
        
        for old_id, old_name in palette_reverse.items():
            new_name = block_mappings.get(old_name, old_name)
            
            if new_name not in new_palette:
                new_palette[new_name] = next_id
                new_palette_reverse[next_id] = new_name
                next_id += 1
            
            id_mapping[old_id] = new_palette[new_name]
        
        # Apply mapping to array
        simplified = np.copy(voxel_array)
        for old_id, new_id in id_mapping.items():
            simplified[voxel_array == old_id] = new_id
        
        return simplified, new_palette_reverse
    
    def split_into_patches(
        self,
        voxel_array: np.ndarray,
        patch_size: int = 16,
        stride: Optional[int] = None
    ) -> List[np.ndarray]:
        """Split large voxel array into smaller patches.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            patch_size: Size of each cubic patch
            stride: Step size between patches (default: patch_size for no overlap)
            
        Returns:
            List of patch arrays
        """
        if stride is None:
            stride = patch_size
        
        patches = []
        width, height, depth = voxel_array.shape
        
        for x in range(0, width - patch_size + 1, stride):
            for y in range(0, height - patch_size + 1, stride):
                for z in range(0, depth - patch_size + 1, stride):
                    patch = voxel_array[x:x+patch_size, y:y+patch_size, z:z+patch_size]
                    patches.append(patch)
        
        return patches
