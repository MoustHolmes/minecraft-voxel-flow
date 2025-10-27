"""PyTorch Dataset for Minecraft schematics."""

from pathlib import Path
from typing import Optional, Callable, Union, List, Tuple, Dict

import numpy as np
import torch
from torch.utils.data import Dataset

from ..loaders.schematic_loader import SchematicLoader
from ..processors.voxel_processor import VoxelProcessor


class SchematicDataset(Dataset):
    """PyTorch Dataset for Minecraft schematic files.
    
    Args:
        schematic_dir: Directory containing schematic files
        target_size: Optional target size (width, height, depth) for normalization
        transform: Optional transform to apply to voxel arrays
        use_processed: If True, load from processed .npz files
        processed_dir: Directory containing processed .npz files
        cache: If True, cache loaded schematics in memory
        simplify_blocks: If True, simplify block palette
    """
    
    def __init__(
        self,
        schematic_dir: Union[str, Path],
        target_size: Optional[Tuple[int, int, int]] = None,
        transform: Optional[Callable] = None,
        use_processed: bool = False,
        processed_dir: Optional[Union[str, Path]] = None,
        cache: bool = False,
        simplify_blocks: bool = False
    ):
        self.schematic_dir = Path(schematic_dir)
        self.target_size = target_size
        self.transform = transform
        self.use_processed = use_processed
        self.cache = cache
        self.simplify_blocks = simplify_blocks
        
        # Initialize loader and processor
        self.loader = SchematicLoader()
        self.processor = VoxelProcessor()
        
        # Find schematic files
        if use_processed:
            self.processed_dir = Path(processed_dir) if processed_dir else self.schematic_dir / "processed"
            self.files = list(self.processed_dir.glob("*.npz"))
        else:
            self.files = (
                list(self.schematic_dir.glob("*.schematic")) +
                list(self.schematic_dir.glob("*.schem")) +
                list(self.schematic_dir.glob("*.litematic"))
            )
        
        # Sort for consistency
        self.files.sort()
        
        # Cache for loaded data
        self._cache: Dict[int, Tuple[np.ndarray, Dict[int, str]]] = {}
    
    def __len__(self) -> int:
        """Return number of schematics."""
        return len(self.files)
    
    def __getitem__(self, idx: int) -> torch.Tensor:
        """Load and return a schematic as a tensor.
        
        Args:
            idx: Index of schematic to load
            
        Returns:
            Voxel tensor of shape (C, W, H, D) where C is number of channels
        """
        # Check cache
        if self.cache and idx in self._cache:
            voxel_array, palette_reverse = self._cache[idx]
        else:
            # Load schematic
            file_path = self.files[idx]
            
            try:
                if self.use_processed:
                    voxel_array, palette_reverse = self.loader.load_processed(file_path)
                else:
                    voxel_array, palette_reverse, _ = self.loader.load(file_path)
                
                # Simplify blocks if requested
                if self.simplify_blocks:
                    voxel_array, palette_reverse = self.processor.simplify_palette(
                        voxel_array, palette_reverse
                    )
                
                # Normalize size if target specified
                if self.target_size is not None:
                    voxel_array = self.processor.normalize_size(
                        voxel_array, self.target_size, palette_reverse
                    )
                
                # Cache if enabled
                if self.cache:
                    self._cache[idx] = (voxel_array, palette_reverse)
                    
            except Exception as e:
                # Return empty array on error
                print(f"Error loading {file_path}: {e}")
                if self.target_size:
                    voxel_array = np.zeros(self.target_size, dtype=np.int32)
                else:
                    voxel_array = np.zeros((16, 16, 16), dtype=np.int32)
        
        # Convert to tensor (add channel dimension)
        voxel_tensor = torch.from_numpy(voxel_array).unsqueeze(0).float()
        
        # Apply transform if provided
        if self.transform is not None:
            voxel_tensor = self.transform(voxel_tensor)
        
        return voxel_tensor
    
    def get_item_with_metadata(self, idx: int) -> Dict:
        """Get item with additional metadata.
        
        Args:
            idx: Index of schematic to load
            
        Returns:
            Dictionary with 'voxels', 'palette', 'filename', 'shape'
        """
        file_path = self.files[idx]
        
        if self.use_processed:
            voxel_array, palette_reverse = self.loader.load_processed(file_path)
        else:
            voxel_array, palette_reverse, _ = self.loader.load(file_path)
        
        if self.simplify_blocks:
            voxel_array, palette_reverse = self.processor.simplify_palette(
                voxel_array, palette_reverse
            )
        
        if self.target_size is not None:
            original_shape = voxel_array.shape
            voxel_array = self.processor.normalize_size(
                voxel_array, self.target_size, palette_reverse
            )
        else:
            original_shape = voxel_array.shape
        
        voxel_tensor = torch.from_numpy(voxel_array).unsqueeze(0).float()
        
        if self.transform is not None:
            voxel_tensor = self.transform(voxel_tensor)
        
        return {
            'voxels': voxel_tensor,
            'palette': palette_reverse,
            'filename': file_path.name,
            'shape': original_shape,
            'normalized_shape': voxel_array.shape
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
    
    def get_statistics(self) -> Dict:
        """Get dataset statistics.
        
        Returns:
            Dictionary with dataset statistics
        """
        stats = {
            'num_schematics': len(self.files),
            'file_format': 'processed (.npz)' if self.use_processed else 'raw schematics',
            'target_size': self.target_size,
            'cache_enabled': self.cache,
            'cached_items': len(self._cache),
        }
        
        return stats
