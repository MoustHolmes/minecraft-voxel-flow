"""
Enhanced Schematic Renderer

Generates high-quality preview images for Minecraft schematics using matplotlib.
Includes multiple view angles and styles.
"""

import sys
from pathlib import Path
import argparse
from typing import Optional, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.loaders.schematic_loader import SchematicLoader
from minecraft_voxel_flow.processors.voxel_processor import VoxelProcessor
from minecraft_voxel_flow.visualization.viewers import SchematicViewer


class EnhancedRenderer:
    """Enhanced renderer with multiple viewing modes."""
    
    def __init__(self):
        self.loader = SchematicLoader()
        self.processor = VoxelProcessor()
        self.viewer = SchematicViewer()
    
    def render_multi_view(
        self,
        schematic_path: str,
        output_path: str,
        views: List[str] = ['top', 'front', 'side', 'iso'],
        figsize: Tuple[int, int] = (20, 15)
    ) -> bool:
        """Render schematic with multiple viewpoints.
        
        Args:
            schematic_path: Path to schematic
            output_path: Output image path
            views: List of view types
            figsize: Figure size
            
        Returns:
            True if successful
        """
        try:
            # Load schematic
            voxels, palette_reverse, palette = self.loader.load(schematic_path)
            
            # Remove air padding (simple crop without palette)
            non_air = voxels > 0
            coords = np.where(non_air)
            if len(coords[0]) > 0:
                x_min, x_max = coords[0].min(), coords[0].max()
                y_min, y_max = coords[1].min(), coords[1].max()
                z_min, z_max = coords[2].min(), coords[2].max()
                voxels = voxels[x_min:x_max+1, y_min:y_max+1, z_min:z_max+1]
            
            # Create figure
            n_views = len(views)
            fig = plt.figure(figsize=figsize)
            gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
            
            name = Path(schematic_path).stem
            fig.suptitle(f"{name} - Multiple Views", fontsize=16, fontweight='bold')
            
            # Get non-air blocks
            non_air = voxels > 0
            blocks = np.argwhere(non_air)
            colors = [palette_reverse.get(voxels[tuple(b)], 'gray') for b in blocks]
            
            # Convert block names to numeric IDs for coloring
            color_ids = [voxels[tuple(b)] for b in blocks]
            
            # View 1: Top view (XZ plane)
            ax1 = fig.add_subplot(gs[0, 0])
            y_slice = voxels.shape[1] // 2
            slice_data = voxels[:, y_slice, :]
            ax1.imshow(slice_data.T, cmap='tab20', origin='lower')
            ax1.set_title('Top View (Y slice)', fontsize=12)
            ax1.set_xlabel('X')
            ax1.set_ylabel('Z')
            ax1.grid(True, alpha=0.3)
            
            # View 2: Front view (XY plane)
            ax2 = fig.add_subplot(gs[0, 1])
            z_slice = voxels.shape[2] // 2
            slice_data = voxels[:, :, z_slice]
            ax2.imshow(slice_data.T, cmap='tab20', origin='lower')
            ax2.set_title('Front View (Z slice)', fontsize=12)
            ax2.set_xlabel('X')
            ax2.set_ylabel('Y')
            ax2.grid(True, alpha=0.3)
            
            # View 3: Side view (YZ plane)
            ax3 = fig.add_subplot(gs[1, 0])
            x_slice = voxels.shape[0] // 2
            slice_data = voxels[x_slice, :, :]
            ax3.imshow(slice_data.T, cmap='tab20', origin='lower')
            ax3.set_title('Side View (X slice)', fontsize=12)
            ax3.set_xlabel('Y')
            ax3.set_ylabel('Z')
            ax3.grid(True, alpha=0.3)
            
            # View 4: 3D scatter (isometric)
            ax4 = fig.add_subplot(gs[1, 1], projection='3d')
            
            # Sample if too many blocks
            max_blocks = 5000
            if len(blocks) > max_blocks:
                indices = np.random.choice(len(blocks), max_blocks, replace=False)
                blocks_sample = blocks[indices]
                colors_sample = [color_ids[i] for i in indices]
            else:
                blocks_sample = blocks
                colors_sample = color_ids
            
            ax4.scatter(
                blocks_sample[:, 0],
                blocks_sample[:, 1],
                blocks_sample[:, 2],
                c=colors_sample,
                cmap='tab20',
                marker='s',
                s=20,
                alpha=0.6
            )
            
            ax4.set_xlabel('X')
            ax4.set_ylabel('Y')
            ax4.set_zlabel('Z')
            ax4.set_title('3D Isometric View', fontsize=12)
            ax4.view_init(elev=20, azim=45)
            
            # Add info text
            info_text = f"Size: {voxels.shape[0]}×{voxels.shape[1]}×{voxels.shape[2]}\n"
            info_text += f"Blocks: {np.sum(non_air):,}\n"
            info_text += f"Block Types: {len(palette)}"
            
            fig.text(0.02, 0.02, info_text, fontsize=10, 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Save
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"Error rendering {schematic_path}: {e}")
            return False
    
    def render_showcase(
        self,
        schematic_path: str,
        output_path: str,
        figsize: Tuple[int, int] = (24, 16)
    ) -> bool:
        """Render a showcase image with all information.
        
        Args:
            schematic_path: Path to schematic
            output_path: Output image path
            figsize: Figure size
            
        Returns:
            True if successful
        """
        try:
            # Load
            voxels, palette_reverse, palette = self.loader.load(schematic_path)
            
            # Crop air (simple approach)
            non_air = voxels > 0
            coords = np.where(non_air)
            if len(coords[0]) > 0:
                x_min, x_max = coords[0].min(), coords[0].max()
                y_min, y_max = coords[1].min(), coords[1].max()
                z_min, z_max = coords[2].min(), coords[2].max()
                voxels_cropped = voxels[x_min:x_max+1, y_min:y_max+1, z_min:z_max+1]
            else:
                voxels_cropped = voxels
            
            # Get statistics
            stats = self.loader.get_statistics(voxels, palette_reverse)
            
            # Create figure with custom layout
            fig = plt.figure(figsize=figsize)
            gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.4)
            
            name = Path(schematic_path).stem
            fig.suptitle(f"Schematic Showcase: {name}", fontsize=18, fontweight='bold')
            
            # Main 3D view (large)
            ax_main = fig.add_subplot(gs[0:2, 0:2], projection='3d')
            
            non_air = voxels_cropped > 0
            blocks = np.argwhere(non_air)
            
            # Sample if needed
            max_blocks = 8000
            if len(blocks) > max_blocks:
                indices = np.random.choice(len(blocks), max_blocks, replace=False)
                blocks = blocks[indices]
            
            colors = [palette_reverse.get(voxels_cropped[tuple(b)], 'gray') for b in blocks]
            
            # Use block IDs as numeric colors
            color_ids = [voxels_cropped[tuple(b)] for b in blocks]
            
            ax_main.scatter(
                blocks[:, 0], blocks[:, 1], blocks[:, 2],
                c=color_ids, cmap='tab20', marker='s', s=30, alpha=0.7, edgecolors='black', linewidth=0.1
            )
            ax_main.set_title('3D View', fontsize=14, pad=20)
            ax_main.view_init(elev=25, azim=45)
            ax_main.set_xlabel('X', fontsize=10)
            ax_main.set_ylabel('Y', fontsize=10)
            ax_main.set_zlabel('Z', fontsize=10)
            
            # Top view
            ax_top = fig.add_subplot(gs[0, 2])
            y_mid = voxels_cropped.shape[1] // 2
            ax_top.imshow(voxels_cropped[:, y_mid, :].T, cmap='tab20', origin='lower')
            ax_top.set_title('Top View', fontsize=11)
            ax_top.axis('off')
            
            # Front view
            ax_front = fig.add_subplot(gs[1, 2])
            z_mid = voxels_cropped.shape[2] // 2
            ax_front.imshow(voxels_cropped[:, :, z_mid].T, cmap='tab20', origin='lower')
            ax_front.set_title('Front View', fontsize=11)
            ax_front.axis('off')
            
            # Statistics panel
            ax_stats = fig.add_subplot(gs[2, 0])
            ax_stats.axis('off')
            
            stats_text = "Statistics:\\n" + "="*30 + "\\n"
            stats_text += f"Dimensions: {voxels.shape[0]}×{voxels.shape[1]}×{voxels.shape[2]}\\n"
            stats_text += f"After crop: {voxels_cropped.shape[0]}×{voxels_cropped.shape[1]}×{voxels_cropped.shape[2]}\\n"
            stats_text += f"Total blocks: {np.sum(non_air):,}\\n"
            stats_text += f"Block types: {len(palette_reverse)}\\n"
            stats_text += f"Air%: {stats.get('air_percentage', 0):.1f}%"
            
            ax_stats.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
                         verticalalignment='center',
                         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            # Top blocks chart
            ax_blocks = fig.add_subplot(gs[2, 1:3])
            
            top_blocks = stats['top_blocks'][:10]
            if top_blocks:
                block_names = [b['block_name'].split(':')[-1][:20] for b in top_blocks]
                block_counts = [b['count'] for b in top_blocks]
                
                bars = ax_blocks.barh(block_names, block_counts, color='steelblue', alpha=0.7)
                ax_blocks.set_xlabel('Count', fontsize=10)
                ax_blocks.set_title('Top 10 Block Types', fontsize=11)
                ax_blocks.grid(axis='x', alpha=0.3)
                
                # Add count labels
                for bar in bars:
                    width = bar.get_width()
                    ax_blocks.text(width, bar.get_y() + bar.get_height()/2,
                                  f'{int(width):,}', ha='left', va='center', fontsize=8)
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return True
            
        except Exception as e:
            import traceback
            print(f"Error creating showcase: {e}")
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced schematic rendering with multiple views"
    )
    parser.add_argument("--schematics-dir", default="data/schematics",
                       help="Directory containing schematics")
    parser.add_argument("--output-dir", default="data/renders",
                       help="Output directory for renders")
    parser.add_argument("--mode", choices=['multi', 'showcase'], default='showcase',
                       help="Render mode: multi (4 views) or showcase (detailed)")
    parser.add_argument("--max", type=int, help="Maximum number to render")
    parser.add_argument("--figsize", type=int, nargs=2, default=[24, 16],
                       help="Figure size")
    
    args = parser.parse_args()
    
    # Setup
    schematics_dir = Path(args.schematics_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find schematics
    schematic_files = (
        list(schematics_dir.glob("*.schematic")) +
        list(schematics_dir.glob("*.schem")) +
        list(schematics_dir.glob("*.litematic"))
    )
    
    if args.max:
        schematic_files = schematic_files[:args.max]
    
    print(f"Found {len(schematic_files)} schematics")
    print(f"Mode: {args.mode}")
    print(f"Output: {output_dir}")
    print("-" * 60)
    
    # Render
    renderer = EnhancedRenderer()
    success_count = 0
    
    for schematic_path in tqdm(schematic_files, desc="Rendering"):
        output_path = output_dir / f"{schematic_path.stem}_{args.mode}.png"
        
        try:
            if args.mode == 'multi':
                success = renderer.render_multi_view(
                    str(schematic_path),
                    str(output_path),
                    figsize=tuple(args.figsize)
                )
            else:  # showcase
                success = renderer.render_showcase(
                    str(schematic_path),
                    str(output_path),
                    figsize=tuple(args.figsize)
                )
            
            if success:
                success_count += 1
                
        except Exception as e:
            tqdm.write(f"❌ Failed {schematic_path.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully rendered: {success_count}/{len(schematic_files)}")
    print(f"📁 Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
