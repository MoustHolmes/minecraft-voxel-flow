#!/usr/bin/env python3
"""
Quick test script to verify the scraper works on a small sample.

This will scrape just a few schematics to verify everything is working.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from minecraft_voxel_flow.scrape_scheme import selenium_scraper


def main():
    """Test the scraper with a small sample."""
    print("="*70)
    print("SCRAPER TEST - Small Sample")
    print("="*70)
    print("This will scrape just 5 schematics as a test.")
    print("After this test succeeds, use run_scraper.py for full scraping.")
    print("="*70)
    
    # Setup driver
    print("\nSetting up Firefox...")
    options = Options()
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), 
        options=options
    )
    print("✓ Firefox started")
    
    try:
        # Manual login
        print("\nOpening login page...")
        driver.get("https://www.minecraft-schematics.com/login/")
        print("\nPlease log in manually in the browser.")
        input("Press ENTER after logging in...")
        
        # Test with just 5 schematics
        print("\nStarting test scrape (5 schematics)...")
        selenium_scraper(driver, start_id=1824, end_id=1828, delay=0.8)
        
        print("\n" + "="*70)
        print("TEST COMPLETE!")
        print("="*70)
        print("Check data/schematics/ for downloaded files")
        print("Check data/schematics_metadata.csv for metadata")
        print("\nIf everything looks good, run the full scraper:")
        print("  python scripts/run_scraper.py --start 1824 --end 19000")
        
    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
