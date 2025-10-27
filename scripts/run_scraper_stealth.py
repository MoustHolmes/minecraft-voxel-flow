#!/usr/bin/env python3
"""
Minecraft Schematics Scraper - Cloudflare Bypass Version

This version uses undetected-chromedriver which is specifically designed
to bypass Cloudflare and other bot detection systems.

Installation:
    pip install undetected-chromedriver

Usage:
    python scripts/run_scraper_stealth.py --start 1824 --end 2000
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import undetected_chromedriver as uc
except ImportError:
    print("❌ undetected-chromedriver not installed!")
    print("Install it with: pip install undetected-chromedriver")
    sys.exit(1)

from minecraft_voxel_flow.scrape_scheme import selenium_scraper


def setup_stealth_driver():
    """
    Set up undetected Chrome WebDriver for Cloudflare bypass.
    
    Returns:
        WebDriver instance
    """
    print("Setting up Stealth Chrome WebDriver (Cloudflare bypass)...")
    
    options = uc.ChromeOptions()
    
    # Set download preferences
    prefs = {
        "download.default_directory": str(Path.home() / "Downloads"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Additional stealth options
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Initialize undetected Chrome
    driver = uc.Chrome(options=options, version_main=None)
    
    print("✓ Stealth WebDriver initialized")
    print("  This driver is designed to bypass Cloudflare!")
    return driver


def manual_login(driver, login_url="https://www.minecraft-schematics.com/login/"):
    """
    Guide user through manual login process.
    
    Args:
        driver: Selenium WebDriver instance
        login_url: URL of the login page
    """
    print("\n" + "="*70)
    print("CLOUDFLARE BYPASS & LOGIN")
    print("="*70)
    print("Using undetected-chromedriver for automatic Cloudflare bypass!")
    print(f"\nOpening login page: {login_url}")
    print("\n✨ With this stealth driver:")
    print("  • Cloudflare should pass automatically")
    print("  • You may not even see the challenge")
    print("  • Just log in normally when the page loads")
    print("\nSteps:")
    print("  1. Wait for page to load (Cloudflare bypass happens automatically)")
    print("  2. Log in manually")
    print("  3. Return here and press ENTER")
    print("="*70)
    
    # Open login page
    driver.get(login_url)
    
    # Wait for Cloudflare bypass
    print("\nWaiting for Cloudflare bypass (10 seconds)...")
    time.sleep(10)
    
    # Wait for user to log in
    input("\n✅ Press ENTER after you have logged in successfully...")
    
    # Verify login
    current_url = driver.current_url
    if 'login' not in current_url:
        print("✓ Login successful!")
        print(f"  Current URL: {current_url}")
    else:
        print("⚠ Warning: Still on login page.")
        retry = input("Continue anyway? (y/n): ")
        if retry.lower() != 'y':
            print("Exiting...")
            driver.quit()
            sys.exit(1)


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Minecraft schematics with Cloudflare bypass (undetected-chromedriver)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape schematics from ID 1824 to 2000
  python scripts/run_scraper_stealth.py --start 1824 --end 2000
  
  # Full scrape with custom delay
  python scripts/run_scraper_stealth.py --start 1824 --end 26538 --delay 1.0
  
  # Resume from ID 5000
  python scripts/run_scraper_stealth.py --start 5000 --end 26538

Note: This version uses undetected-chromedriver which is better at bypassing Cloudflare.
        """
    )
    
    parser.add_argument(
        '--start', 
        type=int, 
        required=True,
        help='Starting schematic ID'
    )
    parser.add_argument(
        '--end', 
        type=int, 
        required=True,
        help='Ending schematic ID'
    )
    parser.add_argument(
        '--delay', 
        type=float, 
        default=0.8,
        help='Delay between requests in seconds (default: 0.8)'
    )
    parser.add_argument(
        '--login-url',
        type=str,
        default='https://www.minecraft-schematics.com/login/',
        help='Login URL'
    )
    parser.add_argument(
        '--skip-login',
        action='store_true',
        help='Skip the login step'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.start > args.end:
        print("Error: Start ID must be less than or equal to End ID")
        sys.exit(1)
    
    # Print configuration
    print("\n" + "="*70)
    print("MINECRAFT SCHEMATICS SCRAPER (STEALTH MODE)")
    print("="*70)
    print(f"Schematic ID range: {args.start} to {args.end}")
    print(f"Total schematics: {args.end - args.start + 1}")
    print(f"Delay per request: {args.delay} seconds")
    print("\n🕵️ Using undetected-chromedriver for Cloudflare bypass")
    
    # Estimate time
    total_time = (args.end - args.start + 1) * (args.delay + 2.0)
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    print(f"Estimated time: ~{hours}h {minutes}m")
    print("="*70)
    
    # Setup driver
    driver = None
    try:
        driver = setup_stealth_driver()
        
        # Login (unless skipped)
        if not args.skip_login:
            manual_login(driver, args.login_url)
        else:
            print("\n⚠ Skipping login - assuming already authenticated")
        
        # Start scraping
        print("\n" + "="*70)
        print("STARTING SCRAPE")
        print("="*70)
        
        start_time = time.time()
        
        selenium_scraper(driver, args.start, args.end, delay=args.delay)
        
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        print("\n" + "="*70)
        print("SCRAPING COMPLETED")
        print("="*70)
        print(f"Total time: {hours}h {minutes}m {seconds}s")
        print(f"Check the data/schematics folder for downloaded files")
        print(f"Check data/schematics_metadata.csv for metadata")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user (Ctrl+C)")
        print("Partial results have been saved to CSV")
        print("You can resume by running the script again with --start <last_id>")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("✓ Browser closed")


if __name__ == "__main__":
    main()
