"""
BlueMap Screenshot Demo - Using Playwright to automate screenshots

Based on: https://bluemap.bluecolored.de/community/python-screenshots.html

This demonstrates the actual BlueMap screenshot workflow:
1. Convert schematic to Minecraft world
2. Start BlueMap web server
3. Use Playwright to automate browser screenshot
"""

from playwright.async_api import async_playwright, Download
from pathlib import Path
from base64 import b64decode
import aiofiles
import asyncio
import subprocess
import time
import signal
import sys


async def on_download(output_path: Path, download: Download) -> None:
    """Callback when screenshot download happens."""
    print(f"📥 Downloading screenshot...")
    content = download.url.split(",", 1)[1]
    content = b64decode(content.encode())
    async with aiofiles.open(output_path, 'wb') as write:
        await write.write(content)
    print(f"✅ Screenshot saved to: {output_path}")


async def take_screenshot(
    bluemap_url: str,
    output_path: Path,
    headless: bool = True,
    wait_time: float = 2.0
) -> bool:
    """Take a screenshot from BlueMap web interface.
    
    Args:
        bluemap_url: Full URL with camera position (e.g., 'http://localhost:8100/#world:0:0:0:...')
        output_path: Where to save the screenshot
        headless: Run browser in headless mode
        wait_time: Seconds to wait for page to load
        
    Returns:
        True if successful
    """
    try:
        async with async_playwright() as playwright:
            print(f"🌐 Launching browser...")
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"📍 Loading BlueMap at: {bluemap_url}")
            await page.goto(bluemap_url, wait_until='networkidle', timeout=30000)
            
            # Set up download handler
            page.on('download', lambda download: on_download(output_path, download))
            
            # Wait a bit for map to render
            print(f"⏳ Waiting {wait_time}s for map to render...")
            await asyncio.sleep(wait_time)
            
            # Click menu and take screenshot
            print(f"📸 Taking screenshot...")
            await page.get_by_title('Menu').click()
            await page.get_by_text('Take Screenshot').locator('xpath=..').click()
            
            # Wait for download to complete
            await asyncio.sleep(0.5)
            
            await page.close()
            await browser.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return False


def start_bluemap_server(
    world_path: str,
    config_path: str = None,
    jar_path: str = "tools/bluemap/bluemap-cli.jar",
    port: int = 8100
) -> subprocess.Popen:
    """Start BlueMap web server in background.
    
    Args:
        world_path: Path to Minecraft world directory
        config_path: Optional config file path
        jar_path: Path to BlueMap CLI jar
        port: Web server port
        
    Returns:
        Subprocess handle
    """
    cmd = ["java", "-jar", jar_path]
    
    if config_path:
        cmd.extend(["-c", config_path])
    
    cmd.extend(["-w", world_path, "-rw"])  # -r render, -w web server
    
    print(f"🚀 Starting BlueMap server...")
    print(f"   Command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print(f"⏳ Waiting for server to start on port {port}...")
    time.sleep(5)  # Give it time to initialize
    
    return process


async def demo_bluemap_screenshot():
    """Demo: Complete workflow to take a BlueMap screenshot."""
    
    print("=" * 70)
    print("BlueMap Screenshot Demo")
    print("=" * 70)
    print()
    
    # Configuration
    world_path = "temp_world"  # You need a real Minecraft world here
    output_path = Path("bluemap_screenshot_test.png")
    
    # Check if we have a world to work with
    if not Path(world_path).exists():
        print("⚠️  No test world found!")
        print()
        print("To use BlueMap screenshots, you need:")
        print("1. A Minecraft world directory (not a schematic)")
        print("2. BlueMap CLI running as a web server")
        print()
        print("For schematics, you would need to:")
        print("  a) Convert schematic to Minecraft world using Amulet")
        print("  b) Place it in a world directory")
        print("  c) Run BlueMap on that world")
        print()
        print("This is complex! The matplotlib solution is much simpler for schematics.")
        return False
    
    # Start BlueMap server
    bluemap_process = None
    try:
        bluemap_process = start_bluemap_server(world_path)
        
        # Build URL with camera position
        # Format: #map:x:y:z:distance:yaw:pitch:angle:tilt:projection
        bluemap_url = "http://localhost:8100/#world:0:64:0:100:0:45:0:0:perspective"
        
        # Take screenshot
        success = await take_screenshot(bluemap_url, output_path, headless=False)
        
        if success and output_path.exists():
            print()
            print("=" * 70)
            print(f"✅ Success! Screenshot saved to: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
            print("=" * 70)
            return True
        else:
            print()
            print("❌ Screenshot failed or file not found")
            return False
            
    finally:
        # Stop BlueMap server
        if bluemap_process:
            print()
            print("🛑 Stopping BlueMap server...")
            bluemap_process.terminate()
            bluemap_process.wait(timeout=5)


async def demo_with_existing_server():
    """Demo: Take screenshot from already-running BlueMap server."""
    
    print("=" * 70)
    print("BlueMap Screenshot Demo (Existing Server)")
    print("=" * 70)
    print()
    print("This assumes BlueMap is already running on http://localhost:8100")
    print()
    
    output_path = Path("bluemap_test.png")
    
    # You can customize this URL with different camera positions
    # Format: #mapid:x:y:z:distance:yaw:pitch:angle:tilt:projection
    bluemap_url = "http://localhost:8100/"
    
    success = await take_screenshot(
        bluemap_url,
        output_path,
        headless=False,  # Set to True for production
        wait_time=3.0
    )
    
    if success and output_path.exists():
        print()
        print("=" * 70)
        print(f"✅ Screenshot saved: {output_path}")
        print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
        print("=" * 70)
        return True
    else:
        print()
        print("❌ Failed to take screenshot")
        print()
        print("Make sure:")
        print("1. BlueMap server is running: java -jar tools/bluemap/bluemap-cli.jar -w <world> -rw")
        print("2. You can access http://localhost:8100 in your browser")
        return False


if __name__ == "__main__":
    print()
    print("BlueMap Screenshot Tool")
    print()
    print("Options:")
    print("1. Take screenshot from existing BlueMap server")
    print("2. Full demo (requires Minecraft world)")
    print()
    
    choice = input("Choose (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_with_existing_server())
    elif choice == "2":
        asyncio.run(demo_bluemap_screenshot())
    else:
        print("Invalid choice. Running option 1...")
        asyncio.run(demo_with_existing_server())
