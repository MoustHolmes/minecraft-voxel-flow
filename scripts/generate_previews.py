"""
Generate Preview Screenshots for All Schematics

Uses matplotlib-based rendering (no external dependencies needed).
This is faster and simpler than BlueMap for 2D preview images.
"""

import sys
from pathlib import Path
from tqdm import tqdm
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minecraft_voxel_flow.loaders.schematic_loader import SchematicLoader
from minecraft_voxel_flow.visualization.viewers import SchematicViewer


def generate_previews(
    schematics_dir: str = "data/schematics",
    output_dir: str = "data/previews",
    max_schematics: int = None,
    view_type: str = "slices",
    figsize: tuple = (15, 10)
):
    """Generate preview images for all schematics.
    
    Args:
        schematics_dir: Directory containing schematics
        output_dir: Directory to save preview images
        max_schematics: Optional limit on number to process
        view_type: 'slices' for 2D views, '3d' for 3D scatter (requires plotly)
        figsize: Figure size for matplotlib plots
    """
    schematics_dir = Path(schematics_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all schematics
    schematic_files = (
        list(schematics_dir.glob("*.schematic")) +
        list(schematics_dir.glob("*.schem")) +
        list(schematics_dir.glob("*.litematic"))
    )
    
    if max_schematics:
        schematic_files = schematic_files[:max_schematics]
    
    print(f"Found {len(schematic_files)} schematics")
    print(f"Output directory: {output_dir}")
    print(f"View type: {view_type}")
    print("-" * 60)
    
    loader = SchematicLoader()
    viewer = SchematicViewer()
    
    success_count = 0
    failed_files = []
    
    for schematic_path in tqdm(schematic_files, desc="Generating previews"):
        try:
            # Load
            voxels, palette_reverse, palette = loader.load(str(schematic_path))
            
            # Generate output filename
            output_path = output_dir / f"{schematic_path.stem}.png"
            
            # Render and save
            viewer.save_render(
                voxels,
                str(output_path),
                palette=palette,
                view_type=view_type,
                figsize=figsize,
                title=schematic_path.stem
            )
            
            success_count += 1
            
        except Exception as e:
            failed_files.append((schematic_path.name, str(e)))
            tqdm.write(f"❌ Failed: {schematic_path.name} - {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Successfully rendered: {success_count}/{len(schematic_files)}")
    print(f"  ❌ Failed: {len(failed_files)}")
    print("=" * 60)
    
    if failed_files:
        print("\nFailed files:")
        for filename, error in failed_files[:10]:  # Show first 10
            print(f"  - {filename}: {error}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")
    
    print(f"\n✅ Preview images saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate preview screenshots for Minecraft schematics"
    )
    parser.add_argument(
        "--schematics-dir",
        default="data/schematics",
        help="Directory containing schematic files"
    )
    parser.add_argument(
        "--output-dir",
        default="data/previews",
        help="Directory to save preview images"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Maximum number of schematics to process (for testing)"
    )
    parser.add_argument(
        "--view-type",
        choices=["slices", "3d"],
        default="slices",
        help="Type of visualization (slices=2D cross-sections, 3d=3D scatter)"
    )
    parser.add_argument(
        "--figsize",
        type=int,
        nargs=2,
        default=[15, 10],
        help="Figure size as width height (e.g., --figsize 20 12)"
    )
    
    args = parser.parse_args()
    
    generate_previews(
        schematics_dir=args.schematics_dir,
        output_dir=args.output_dir,
        max_schematics=args.max,
        view_type=args.view_type,
        figsize=tuple(args.figsize)
    )
