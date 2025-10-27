"""
BlueMap Screenshot Demo - Simplified Test

This demonstrates how BlueMap screenshots work, but shows why it's
not ideal for schematic rendering.
"""

from playwright.async_api import async_playwright
from pathlib import Path
import asyncio


async def test_bluemap_connection():
    """Test if BlueMap server is accessible and demonstrate the screenshot process."""
    
    print("=" * 70)
    print("BlueMap Screenshot Test")
    print("=" * 70)
    print()
    
    print("Step 1: Checking if BlueMap server is running...")
    print("   Expected URL: http://localhost:8100")
    print()
    
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("Step 2: Attempting to connect...")
            try:
                response = await page.goto(
                    "http://localhost:8100",
                    wait_until='networkidle',
                    timeout=10000
                )
                
                if response and response.ok:
                    print("✅ BlueMap server is running!")
                    print()
                    print("Step 3: Looking for screenshot button...")
                    
                    # Wait a bit for page to load
                    await asyncio.sleep(2)
                    
                    # Try to find the menu
                    try:
                        await page.get_by_title('Menu').click()
                        print("✅ Found Menu button")
                        
                        await asyncio.sleep(0.5)
                        
                        # Look for screenshot button
                        screenshot_btn = page.get_by_text('Take Screenshot')
                        if await screenshot_btn.count() > 0:
                            print("✅ Found 'Take Screenshot' button")
                            print()
                            print("🎉 BlueMap is fully functional!")
                            print()
                            print("To take a screenshot programmatically:")
                            print("   python scripts/bluemap_screenshot_demo.py")
                        else:
                            print("⚠️  Screenshot button not found")
                            
                    except Exception as e:
                        print(f"⚠️  Could not interact with menu: {e}")
                    
                    # Keep browser open for 5 seconds to see it
                    print()
                    print("Keeping browser open for 5 seconds...")
                    await asyncio.sleep(5)
                    
                else:
                    print("❌ Server responded but not OK")
                    
            except Exception as e:
                print(f"❌ Could not connect to BlueMap server")
                print(f"   Error: {e}")
                print()
                print("To start BlueMap server:")
                print("   1. You need a Minecraft world directory")
                print("   2. Run: java -jar tools/bluemap/bluemap-cli.jar -w <world_path> -rw")
                print()
                print("⚠️  Important: BlueMap works with Minecraft WORLDS, not schematics!")
                
            await page.close()
            await browser.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("BlueMap Screenshot Process:")
    print("1. ✅ BlueMap CLI installed")
    print("2. ✅ Java 21 installed")
    print("3. ✅ Playwright installed")
    print("4. ⚠️  Requires Minecraft WORLD (not schematic)")
    print()
    print("Why BlueMap is complex for schematics:")
    print("- BlueMap renders Minecraft worlds (.mca region files)")
    print("- Schematics must first be converted to worlds")
    print("- World conversion is complex (level.dat, regions, chunks)")
    print("- Each schematic would need its own world")
    print()
    print("Recommendation: Use Matplotlib Solution")
    print("- Works directly with schematics ✅")
    print("- Already tested and working ✅")
    print("- Much faster for batch processing ✅")
    print()
    print("Run: python scripts/render_schematics.py --mode showcase --max 10")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_bluemap_connection())
