"""Visualization tools for Minecraft schematics."""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
import matplotlib.pyplot as plt


class SchematicViewer:
    """Visualize Minecraft schematic voxel data.
    
    Provides multiple visualization methods:
    - 2D slices (horizontal and vertical)
    - 3D interactive plots (plotly)
    - Saved renders
    """
    
    def __init__(self, backend: str = 'matplotlib'):
        """Initialize viewer.
        
        Args:
            backend: Visualization backend ('matplotlib', 'plotly')
        """
        self.backend = backend
    
    def view_slices(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Optional[Dict[int, str]] = None,
        num_slices: int = 5,
        direction: str = 'horizontal',
        figsize: Tuple[int, int] = (20, 4),
        title: Optional[str] = None
    ):
        """View 2D slices through the structure.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Optional dict mapping block IDs to names
            num_slices: Number of slices to show
            direction: 'horizontal' (Y slices) or 'vertical' (X/Z slices)
            figsize: Figure size
            title: Optional title for the plot
        """
        if direction == 'horizontal':
            self._view_horizontal_slices(
                voxel_array, num_slices, figsize, title
            )
        elif direction == 'vertical':
            self._view_vertical_slices(
                voxel_array, figsize, title
            )
        else:
            raise ValueError(f"Unknown direction: {direction}")
    
    def _view_horizontal_slices(
        self,
        voxel_array: np.ndarray,
        num_slices: int,
        figsize: Tuple[int, int],
        title: Optional[str]
    ):
        """View horizontal (Y-level) slices."""
        width, height, depth = voxel_array.shape
        
        fig, axes = plt.subplots(1, num_slices, figsize=figsize)
        if num_slices == 1:
            axes = [axes]
        
        for i, ax in enumerate(axes):
            y_level = int(height * i / (num_slices - 1)) if num_slices > 1 else height // 2
            y_level = min(y_level, height - 1)
            
            slice_data = voxel_array[:, y_level, :]
            
            ax.imshow(slice_data.T, cmap='tab20c', interpolation='nearest', origin='lower')
            ax.set_title(f'Y = {y_level}')
            ax.set_xlabel('X')
            ax.set_ylabel('Z')
            ax.grid(False)
        
        if title:
            plt.suptitle(title, fontsize=14, y=1.02)
        
        plt.tight_layout()
        plt.show()
    
    def _view_vertical_slices(
        self,
        voxel_array: np.ndarray,
        figsize: Tuple[int, int],
        title: Optional[str]
    ):
        """View vertical (side) slices."""
        width, height, depth = voxel_array.shape
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Front view (X-Y plane)
        z_mid = depth // 2
        slice_data = voxel_array[:, :, z_mid]
        axes[0].imshow(slice_data.T, cmap='tab20c', interpolation='nearest', 
                      origin='lower', aspect='auto')
        axes[0].set_title(f'Front View (Z = {z_mid})')
        axes[0].set_xlabel('X')
        axes[0].set_ylabel('Y (Height)')
        axes[0].grid(False)
        
        # Side view (Y-Z plane)
        x_mid = width // 2
        slice_data = voxel_array[x_mid, :, :]
        axes[1].imshow(slice_data.T, cmap='tab20c', interpolation='nearest',
                      origin='lower', aspect='auto')
        axes[1].set_title(f'Side View (X = {x_mid})')
        axes[1].set_xlabel('Z')
        axes[1].set_ylabel('Y (Height)')
        axes[1].grid(False)
        
        if title:
            plt.suptitle(title, fontsize=14, y=1.02)
        
        plt.tight_layout()
        plt.show()
    
    def view_3d(
        self,
        voxel_array: np.ndarray,
        palette_reverse: Optional[Dict[int, str]] = None,
        max_blocks: int = 10000,
        title: Optional[str] = None,
        width: int = 900,
        height: int = 700
    ):
        """View 3D interactive visualization.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            palette_reverse: Optional dict mapping block IDs to names
            max_blocks: Maximum blocks to display (samples if exceeded)
            title: Optional title for the plot
            width: Plot width in pixels
            height: Plot height in pixels
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise ImportError(
                "Plotly required for 3D visualization. "
                "Install with: pip install plotly"
            )
        
        # Find air blocks to exclude
        if palette_reverse:
            air_ids = [bid for bid, name in palette_reverse.items() 
                      if 'air' in name.lower()]
        else:
            air_ids = [0]
        
        # Get non-air blocks
        non_air_mask = ~np.isin(voxel_array, air_ids)
        non_air_count = np.sum(non_air_mask)
        
        print(f"Non-air blocks: {non_air_count:,}")
        
        # Sample if too many blocks
        if non_air_count > max_blocks:
            print(f"⚠️  Sampling {max_blocks:,} blocks for visualization")
            x_coords, y_coords, z_coords = np.where(non_air_mask)
            indices = np.random.choice(len(x_coords), max_blocks, replace=False)
            x_coords = x_coords[indices]
            y_coords = y_coords[indices]
            z_coords = z_coords[indices]
        else:
            x_coords, y_coords, z_coords = np.where(non_air_mask)
        
        # Get block IDs for colors
        block_ids = voxel_array[x_coords, y_coords, z_coords]
        
        # Create hover text
        if palette_reverse:
            hover_text = [palette_reverse.get(bid, f'Block {bid}') for bid in block_ids]
        else:
            hover_text = [f'Block {bid}' for bid in block_ids]
        
        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='markers',
            marker=dict(
                size=2,
                color=block_ids,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Block ID")
            ),
            text=hover_text,
            hovertemplate='%{text}<br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>'
        )])
        
        fig.update_layout(
            title=title or '3D Voxel View',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y (Height)',
                zaxis_title='Z',
                aspectmode='data'
            ),
            width=width,
            height=height
        )
        
        fig.show()
    
    def save_render(
        self,
        voxel_array: np.ndarray,
        output_path: Union[str, Path],
        view_type: str = 'slices',
        **kwargs
    ):
        """Save visualization to file.
        
        Args:
            voxel_array: 3D numpy array of block IDs
            output_path: Path to save image
            view_type: Type of view ('slices', 'horizontal', 'vertical')
            **kwargs: Additional arguments passed to view function
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create visualization
        if view_type == 'slices' or view_type == 'horizontal':
            self._view_horizontal_slices(
                voxel_array,
                kwargs.get('num_slices', 5),
                kwargs.get('figsize', (20, 4)),
                kwargs.get('title')
            )
        elif view_type == 'vertical':
            self._view_vertical_slices(
                voxel_array,
                kwargs.get('figsize', (15, 5)),
                kwargs.get('title')
            )
        
        # Save
        plt.savefig(output_path, dpi=kwargs.get('dpi', 150), bbox_inches='tight')
        plt.close()
        
        print(f"Saved render to: {output_path}")
