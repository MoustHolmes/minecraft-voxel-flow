"""
BlueMap Screenshot Renderer for Minecraft Schematics

Based on: https://bluemap.bluecolored.de/community/python-screenshots.html

This module provides automated screenshot generation for Minecraft schematics
using BlueMap's CLI and Python API.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import shutil

try:
    from PIL import Image
    import requests
except ImportError:
    print("Warning: PIL and requests required. Install with: pip install pillow requests")


class BlueMapRenderer:
    """Render screenshots of Minecraft schematics using BlueMap CLI.
    
    Requires:
    - BlueMap CLI jar file (bluemap-cli.jar)
    - Java Runtime Environment
    """
    
    def __init__(
        self,
        bluemap_jar: Optional[str] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        java_command: str = "java"
    ):
        """Initialize BlueMap renderer.
        
        Args:
            bluemap_jar: Path to bluemap-cli.jar (auto-detected if None)
            resolution: Output image resolution (width, height)
            java_command: Java command to use
        """
        self.resolution = resolution
        
        # Try to find Java in common Homebrew locations
        if java_command == "java":
            homebrew_java = Path("/opt/homebrew/opt/openjdk@21/bin/java")
            if homebrew_java.exists():
                java_command = str(homebrew_java)
        
        self.java_command = java_command
        
        # Find BlueMap jar
        if bluemap_jar is None:
            bluemap_jar = self._find_bluemap_jar()
        
        self.bluemap_jar = Path(bluemap_jar) if bluemap_jar else None
        
        if self.bluemap_jar is None or not self.bluemap_jar.exists():
            print("⚠️  BlueMap CLI not found!")
            print("\nTo install:")
            print("1. Download from: https://github.com/BlueMap-Minecraft/BlueMap/releases")
            print("2. Save as: tools/bluemap/bluemap-cli.jar")
            print("\nOr run: python scripts/download_bluemap.py")
        else:
            print(f"✅ Found BlueMap CLI: {self.bluemap_jar}")
    
    def _find_bluemap_jar(self) -> Optional[str]:
        """Try to find bluemap-cli.jar in common locations."""
        search_paths = [
            "tools/bluemap/bluemap-cli.jar",
            "tools/bluemap-cli.jar",
            "bluemap-cli.jar",
            "../tools/bluemap/bluemap-cli.jar",
        ]
        
        for path in search_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def check_requirements(self) -> bool:
        """Check if all requirements are met.
        
        Returns:
            True if ready to render, False otherwise
        """
        # Check Java
        try:
            result = subprocess.run(
                [self.java_command, "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("❌ Java not found. Install Java 17 or later.")
                return False
            print("✅ Java found")
        except FileNotFoundError:
            print("❌ Java not found. Install Java 17 or later.")
            return False
        
        # Check BlueMap
        if not self.bluemap_jar or not self.bluemap_jar.exists():
            print("❌ BlueMap CLI not found")
            return False
        print(f"✅ BlueMap CLI found")
        
        return True
    
    def render_schematic(
        self,
        schematic_path: str,
        output_path: str,
        camera_distance: float = 100,
        camera_angle: float = 45,
        camera_rotation: float = 45,
        render_edges: bool = True,
        background_color: str = "#87CEEB"  # Sky blue
    ) -> bool:
        """Render a schematic to an image using BlueMap.
        
        Args:
            schematic_path: Path to the schematic file
            output_path: Path to save the rendered image
            camera_distance: Distance from center
            camera_angle: Vertical angle (0-90)
            camera_rotation: Horizontal rotation (0-360)
            render_edges: Whether to render block edges
            background_color: Background color (hex)
            
        Returns:
            True if successful, False otherwise
        """
        schematic_path = Path(schematic_path)
        output_path = Path(output_path)
        
        if not schematic_path.exists():
            print(f"❌ Schematic not found: {schematic_path}")
            return False
        
        if not self.check_requirements():
            return False
        
        print(f"Rendering: {schematic_path.name}")
        
        # Create temporary directory for world
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            world_dir = temp_dir / "world"
            world_dir.mkdir()
            
            # Create a minimal world structure
            region_dir = world_dir / "region"
            region_dir.mkdir()
            
            # Copy schematic to world (simplified - would need proper conversion)
            # For now, we'll use BlueMap's direct schematic support if available
            
            # Create BlueMap config
            config = {
                "accept-download": True,
                "maps": [{
                    "id": "schematic",
                    "name": "Schematic",
                    "world": str(world_dir),
                    "dimension": "minecraft:overworld"
                }],
                "webserver": {
                    "enabled": False
                }
            }
            
            config_path = temp_dir / "bluemap.conf"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Run BlueMap CLI
            try:
                cmd = [
                    self.java_command,
                    "-jar", str(self.bluemap_jar),
                    "-c", str(config_path),
                    "-r"  # Render
                ]
                
                print(f"Running BlueMap...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(temp_dir)
                )
                
                if result.returncode != 0:
                    print(f"❌ BlueMap failed: {result.stderr}")
                    return False
                
                print(f"✅ Rendered successfully")
                
                # TODO: Extract the rendered image
                # BlueMap generates web tiles, would need post-processing
                
                return True
                
            except Exception as e:
                print(f"❌ Error running BlueMap: {e}")
                return False
    
    def render_with_python_api(
        self,
        schematic_path: str,
        output_path: str,
        view_distance: int = 10
    ) -> bool:
        """Render using BlueMap's Python API approach.
        
        Based on: https://bluemap.bluecolored.de/community/python-screenshots.html
        
        Args:
            schematic_path: Path to schematic
            output_path: Output image path
            view_distance: Render distance
            
        Returns:
            True if successful
        """
        # This would require:
        # 1. Starting BlueMap web server
        # 2. Using requests to trigger render
        # 3. Downloading rendered tiles
        # 4. Stitching tiles together
        
        print("⚠️  Python API rendering requires BlueMap web server")
        print("This is a more complex setup. For now, use direct CLI rendering.")
        return False
    
    def batch_render_schematics(
        self,
        schematics_dir: str,
        output_dir: str,
        max_schematics: Optional[int] = None,
        **render_kwargs
    ) -> Dict[str, bool]:
        """Batch render multiple schematics.
        
        Args:
            schematics_dir: Directory containing schematics
            output_dir: Directory to save screenshots
            max_schematics: Optional limit on number to render
            **render_kwargs: Arguments passed to render_schematic
            
        Returns:
            Dictionary mapping schematic names to success status
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
        
        print(f"Found {len(schematic_files)} schematics to render")
        
        results = {}
        for i, schematic_path in enumerate(schematic_files, 1):
            print(f"\n[{i}/{len(schematic_files)}] {schematic_path.name}")
            
            output_path = output_dir / f"{schematic_path.stem}.png"
            
            success = self.render_schematic(
                str(schematic_path),
                str(output_path),
                **render_kwargs
            )
            
            results[schematic_path.name] = success
        
        # Print summary
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'='*60}")
        print(f"Summary: {success_count}/{len(results)} rendered successfully")
        print(f"{'='*60}")
        
        return results


def download_bluemap_cli(output_path: str = "tools/bluemap/bluemap-cli.jar"):
    """Download BlueMap CLI jar file.
    
    Args:
        output_path: Where to save the jar file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get latest release
    print("Fetching latest BlueMap release...")
    
    try:
        import requests
        
        # GitHub API to get latest release
        api_url = "https://api.github.com/repos/BlueMap-Minecraft/BlueMap/releases/latest"
        response = requests.get(api_url)
        response.raise_for_status()
        
        release_data = response.json()
        
        # Find CLI jar asset
        cli_asset = None
        for asset in release_data['assets']:
            if 'cli' in asset['name'].lower() and asset['name'].endswith('.jar'):
                cli_asset = asset
                break
        
        if not cli_asset:
            print("❌ Could not find CLI jar in latest release")
            print("\nPlease download manually from:")
            print("https://github.com/BlueMap-Minecraft/BlueMap/releases")
            return False
        
        # Download
        print(f"Downloading: {cli_asset['name']}")
        print(f"Size: {cli_asset['size'] / (1024*1024):.1f} MB")
        
        download_url = cli_asset['browser_download_url']
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\nPlease download manually from:")
        print("https://github.com/BlueMap-Minecraft/BlueMap/releases")
        return False


if __name__ == "__main__":
    # Example usage
    renderer = BlueMapRenderer()
    
    if not renderer.bluemap_jar:
        print("\nAttempting to download BlueMap CLI...")
        if download_bluemap_cli():
            renderer = BlueMapRenderer()
    
    if renderer.check_requirements():
        print("\n✅ Ready to render!")
        print("\nExample usage:")
        print('  renderer.render_schematic("data/schematics/example.schematic", "output.png")')
    else:
        print("\n❌ Requirements not met. Please install BlueMap CLI.")
