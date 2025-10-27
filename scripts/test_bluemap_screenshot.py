"""
Simple BlueMap screenshot test - exactly as shown in the wiki.
Based on: https://bluemap.bluecolored.de/community/python-screenshots.html
"""

from playwright.async_api import async_playwright, Download
from pathlib import Path
from base64 import b64decode
import aiofiles
import asyncio

async def on_download(output_path: Path, download: Download) -> None:
    print(download.url[:50])
    content = download.url.split(",", 1)[1]
    content = b64decode(content.encode())
    async with aiofiles.open(output_path, 'wb') as write:
        await write.write(content)

async def main() -> None:
    output_path = Path('test_screenshot.png')

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(
            'http://localhost:8100/#overworld:0:70:0:100:-0.54:0.83:0:0:perspective',
            wait_until='networkidle'
        )

        page.on('download', lambda download: on_download(output_path, download))

        await page.get_by_title('Menu').click()
        await page.get_by_text('Take Screenshot').locator('xpath=..').click()
        await asyncio.sleep(.5)
        await page.close()
        
        print(f"✅ Screenshot saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
