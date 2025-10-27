#!/usr/bin/env python3
"""
Minecraft Schematics Scraper - Standalone Script

This script scrapes schematic files from minecraft-schematics.com.
It requires manual authentication through the browser.

Usage:
    python scripts/run_scraper.py --start 1824 --end 2000
    python scripts/run_scraper.py --start 1824 --end 2000 --delay 1.0
    python scripts/run_scraper.py --start 1824 --end 19000  # Full scrape
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from minecraft_voxel_flow.scrape_scheme import selenium_scraper


def setup_driver(use_profile=True):
    """
    Set up Firefox WebDriver with anti-detection options.
    
    Args:
        use_profile: If True, uses your real Firefox profile (recommended for Cloudflare)
    
    Returns:
        WebDriver instance
    """
    print("Setting up Firefox WebDriver with anti-detection...")
    
    # Configure Firefox options
    options = Options()
    
    # Anti-detection: Use real Firefox profile (looks more human)
    if use_profile:
        print("\n⚠️  IMPORTANT: Using your real Firefox profile for better Cloudflare bypass")
        print("Please close ALL Firefox windows before continuing!")
        input("Press ENTER when Firefox is closed...")
        
        # Try to find Firefox profile
        from pathlib import Path
        import platform
        
        if platform.system() == "Darwin":  # macOS
            profile_path = Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles"
        elif platform.system() == "Windows":
            profile_path = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        else:  # Linux
            profile_path = Path.home() / ".mozilla" / "firefox"
        
        if profile_path.exists():
            profiles = [p for p in profile_path.iterdir() if p.is_dir() and 'default' in p.name.lower()]
            if profiles:
                options.add_argument("-profile")
                options.add_argument(str(profiles[0]))
                print(f"✓ Using Firefox profile: {profiles[0].name}")
    
    # Anti-detection preferences
    options.set_preference("dom.webdriver.enabled", False)  # Hide webdriver flag
    options.set_preference('useAutomationExtension', False)  # Disable automation flag
    options.set_preference("general.useragent.override", 
                          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # Real user agent
    
    # Set download preferences
    options.set_preference("browser.download.folderList", 1)  # Use Downloads folder
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                          "application/octet-stream,application/x-schematic")
    
    # Initialize driver
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), 
        options=options
    )
    
    # Additional anti-detection: Modify navigator properties
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✓ WebDriver initialized with anti-detection")
    return driver


def manual_login(driver, login_url="https://www.minecraft-schematics.com/login/"):
    """
    Guide user through manual login process with Cloudflare bypass tips.
    
    Args:
        driver: Selenium WebDriver instance
        login_url: URL of the login page
    """
    print("\n" + "="*70)
    print("MANUAL LOGIN & CLOUDFLARE BYPASS")
    print("="*70)
    print(f"Opening login page: {login_url}")
    print("\n⚡ CLOUDFLARE TIPS:")
    print("  1. If you see Cloudflare challenge, WAIT and don't click anything")
    print("  2. Let it verify automatically (can take 5-10 seconds)")
    print("  3. If it asks to verify you're human, complete the challenge")
    print("  4. Then log in manually")
    print("  5. Browse to 1-2 pages manually (this helps!)")
    print("  6. Return here and press ENTER")
    print("\n💡 TIP: Using your real Firefox profile makes Cloudflare much easier!")
    print("="*70)
    
    # Open login page
    driver.get(login_url)
    
    # Give Cloudflare time to load
    print("\nWaiting 5 seconds for Cloudflare to load...")
    time.sleep(5)
    
    # Wait for user to log in
    input("\nPress ENTER after you have:")
    input("  ✓ Passed Cloudflare check")
    input("  ✓ Logged in successfully")
    input("  ✓ Browsed 1-2 pages manually")
    input("\nReady to scrape? Press ENTER...")
    
    # Verify login by checking current URL or page content
    current_url = driver.current_url
    if 'login' not in current_url:
        print("✓ Login appears successful!")
        print(f"  Current URL: {current_url}")
    else:
        print("⚠ Warning: Still on login page. Make sure you logged in correctly.")
        retry = input("Continue anyway? (y/n): ")
        if retry.lower() != 'y':
            print("Exiting...")
            driver.quit()
            sys.exit(1)


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Minecraft schematics from minecraft-schematics.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape schematics from ID 1824 to 2000
  python scripts/run_scraper.py --start 1824 --end 2000
  
  # Full scrape with custom delay
  python scripts/run_scraper.py --start 1824 --end 19000 --delay 1.0
  
  # Resume from ID 5000
  python scripts/run_scraper.py --start 5000 --end 19000
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
        help='Delay between requests in seconds (default: 0.8 for optimal speed)'
    )
    parser.add_argument(
        '--login-url',
        type=str,
        default='https://www.minecraft-schematics.com/login/',
        help='Login URL (default: https://www.minecraft-schematics.com/login/)'
    )
    parser.add_argument(
        '--skip-login',
        action='store_true',
        help='Skip the login step (use if already logged in from previous run)'
    )
    parser.add_argument(
        '--no-profile',
        action='store_true',
        help='Do not use Firefox profile (default: uses profile for better Cloudflare bypass)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.start > args.end:
        print("Error: Start ID must be less than or equal to End ID")
        sys.exit(1)
    
    if args.delay < 0.5:
        print("Warning: Delay less than 0.5 seconds may cause issues or rate limiting")
        print("Recommended minimum: 0.5 seconds")
        proceed = input("Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            sys.exit(1)
    
    # Print configuration
    print("\n" + "="*70)
    print("MINECRAFT SCHEMATICS SCRAPER")
    print("="*70)
    print(f"Schematic ID range: {args.start} to {args.end}")
    print(f"Total schematics: {args.end - args.start + 1}")
    print(f"Delay per request: {args.delay} seconds")
    
    # Estimate time
    total_time = (args.end - args.start + 1) * (args.delay + 2.0)  # +2s for page loads
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    print(f"Estimated time: ~{hours}h {minutes}m")
    print("="*70)
    
    # Setup driver
    driver = None
    try:
        driver = setup_driver(use_profile=not args.no_profile)
        
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
