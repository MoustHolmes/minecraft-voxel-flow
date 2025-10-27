"""SchematicLoader: Load and convert Minecraft schematics to voxel arrays."""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional, Union

import numpy as np
from amulet import load_level
from amulet.api.block import Block


class SchematicLoader:
    """Load Minecraft schematic files and convert to voxel arrays.
    
    Supports multiple schematic formats:
    - .schematic (MCEdit legacy format)
    - .schem (Sponge schematic format)
    - .litematic (Litematica format)
    """
    
    SUPPORTED_FORMATS = ['.schematic', '.schem', '.litematic']
    
    def __init__(self):
        """Initialize the schematic loader."""
        self.last_palette = None
        self.last_palette_reverse = None
    
    def load(
        self,
        filepath: Union[str, Path]
    ) -> Tuple[np.ndarray, Dict[int, str], Dict[str, int]]:
        """Load a schematic file and convert to voxel array.
        
        Args:
            filepath: Path to the schematic file
            
        Returns:
            Tuple of (voxel_array, palette_reverse, palette):
                - voxel_array: 3D numpy array of block IDs (int32)
                - palette_reverse: Dict mapping block IDs to block names
                - palette: Dict mapping block names to block IDs
                
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
            Exception: If loading fails
        """
        filepath = Path(filepath)
        
        # Validate file
        if not filepath.exists():
            raise FileNotFoundError(f"Schematic file not found: {filepath}")
        
        if filepath.suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {filepath.suffix}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )
        
        # Load with amulet
        level = load_level(str(filepath))
        dimension = level.dimensions[0]
        bounds = level.bounds(dimension)
        
        # Get dimensions
        width = bounds.max_x - bounds.min_x
        height = bounds.max_y - bounds.min_y
        depth = bounds.max_z - bounds.min_z
        
        # Initialize array
        voxel_array = np.zeros((width, height, depth), dtype=np.int32)
        
        # Build palette
        palette = {}  # block_name -> id
        palette_reverse = {}  # id -> block_name
        next_id = 0
        
        # Reserve 0 for air (universal format)
        air_block = Block('universal_minecraft', 'air')
        palette[str(air_block)] = 0
        palette_reverse[0] = str(air_block)
        next_id = 1
        
        # Extract blocks
        for x in range(bounds.min_x, bounds.max_x):
            for y in range(bounds.min_y, bounds.max_y):
                for z in range(bounds.min_z, bounds.max_z):
                    block = level.get_block(x, y, z, dimension)
                    block_str = str(block)
                    
                    if block_str not in palette:
                        palette[block_str] = next_id
                        palette_reverse[next_id] = block_str
                        next_id += 1
                    
                    block_id = palette[block_str]
                    voxel_array[x - bounds.min_x, y - bounds.min_y, z - bounds.min_z] = block_id
        
        # Store for later access
        self.last_palette = palette
        self.last_palette_reverse = palette_reverse
        
        return voxel_array, palette_reverse, palette
    
    def save_processed(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Dict[int, str],
        output_path: Union[str, Path],
        original_file: Optional[Union[str, Path]] = None
    ):
        """Save processed voxel array to compressed numpy format.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Dict mapping block IDs to block names
            output_path: Path to save the .npz file
            original_file: Optional path to original schematic file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'voxels': voxel_array,
            'palette': json.dumps(palette_reverse),
            'shape': voxel_array.shape,
        }
        
        if original_file is not None:
            save_data['original_file'] = str(original_file)
        
        np.savez_compressed(output_path, **save_data)
    
    @staticmethod
    def load_processed(filepath: Union[str, Path]) -> Tuple[np.ndarray, Dict[int, str]]:
        """Load processed voxel array from .npz file.
        
        Args:
            filepath: Path to the .npz file
            
        Returns:
            Tuple of (voxel_array, palette_reverse)
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Processed file not found: {filepath}")
        
        loaded = np.load(filepath, allow_pickle=True)
        
        voxel_array = loaded['voxels']
        palette_reverse = json.loads(str(loaded['palette']))
        
        # Convert string keys back to integers
        palette_reverse = {int(k): v for k, v in palette_reverse.items()}
        
        return voxel_array, palette_reverse
    
    def get_statistics(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Dict[int, str]
    ) -> Dict:
        """Get statistics about the voxel array.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Dict mapping block IDs to block names
            
        Returns:
            Dictionary with statistics
        """
        unique, counts = np.unique(voxel_array, return_counts=True)
        
        # Count air blocks
        air_ids = [bid for bid, name in palette_reverse.items() if 'air' in name.lower()]
        air_count = sum(counts[unique == aid][0] for aid in air_ids if aid in unique)
        
        stats = {
            'shape': voxel_array.shape,
            'total_blocks': voxel_array.size,
            'unique_blocks': len(unique),
            'air_blocks': int(air_count),
            'solid_blocks': int(voxel_array.size - air_count),
            'air_percentage': float(air_count / voxel_array.size * 100),
            'memory_mb': float(voxel_array.nbytes / (1024 ** 2)),
        }
        
        # Top blocks
        sorted_indices = np.argsort(counts)[::-1]
        top_blocks = []
        for i in range(min(10, len(unique))):
            idx = sorted_indices[i]
            block_id = unique[idx]
            count = counts[idx]
            percentage = (count / voxel_array.size) * 100
            top_blocks.append({
                'block_id': int(block_id),
                'block_name': palette_reverse.get(block_id, f'Unknown {block_id}'),
                'count': int(count),
                'percentage': float(percentage)
            })
        
        stats['top_blocks'] = top_blocks
        
        return stats
