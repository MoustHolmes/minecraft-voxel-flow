#!/usr/bin/env python3
"""
Planet Minecraft Scraper
Scrapes project metadata from Planet Minecraft with optional filters.
Supports JSON output format with complete download detection.

Usage:
    python scrape_planet_minecraft.py --output data.json --max-pages 10 --share schematic
    caffeinate python scrape_planet_minecraft.py --output all_projects.json --order order_latest
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def setup_driver(headless=True):
    """Initialize Firefox WebDriver with appropriate options"""
    options = Options()
    if headless:
        options.add_argument('--headless')
    
    driver = webdriver.Firefox(options=options)
    return driver


def classify_download_link_v2(url, text):
    """Classify download link type based on URL and text"""
    url_lower = url.lower()
    text_lower = text.lower()
    
    # Direct external hosts
    if 'mediafire.com' in url_lower:
        return 'mediafire'
    elif 'dropbox.com' in url_lower:
        return 'dropbox'
    elif 'drive.google.com' in url_lower or 'docs.google.com' in url_lower:
        return 'google_drive'
    elif 'mega.nz' in url_lower:
        return 'mega'
    elif 'patreon.com' in url_lower:
        return 'patreon'
    else:
        return 'external'


def extract_project_metadata_v2(soup, project_url):
    """
    Enhanced extractor with complete download detection and JSON-friendly structure
    """
    metadata = {
        "url": project_url,
        "title": "N/A",
        "category": "N/A",
        "subcategory": "N/A",
        "posted_date": "N/A",
        "updated_date": "N/A",
        "tags": [],
        "description": "N/A",
        "author": "N/A",
        "stats": {
            "views": 0,
            "views_today": 0,
            "downloads": 0,
            "downloads_today": 0,
            "diamonds": 0,
            "hearts": 0
        },
        "downloads": [],  # Array of download objects
        "has_direct_download": False
    }
    
    # Step 1: Extract from JSON-LD
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    creative_work = None
    
    for script in json_ld_scripts:
        try:
            json_data = json.loads(script.string)
            if json_data.get('@type') == 'CreativeWork':
                creative_work = json_data
                break
        except:
            continue
    
    if creative_work:
        metadata['title'] = creative_work.get('name', 'N/A')
        metadata['description'] = creative_work.get('description', 'N/A')
        metadata['posted_date'] = creative_work.get('datePublished', 'N/A')
        metadata['updated_date'] = creative_work.get('dateModified', 'N/A')
        metadata['category'] = creative_work.get('genre', 'N/A')
        
        # Extract tags from keywords
        keywords = creative_work.get('keywords', '')
        if keywords:
            metadata['tags'] = [tag.strip() for tag in keywords.split(',')]
            
            # Detect subcategory from the official list
            valid_subcategories = [
                '3d-art', 'air-structure', 'challenge-adventure', 'complex', 'educational',
                'enviroment-landscaping', 'land-structure', 'minecart', 'music',
                'nether-structure', 'piston', 'pixel-art', 'redstone-device',
                'underground-structure', 'water-structure', 'other'
            ]
            
            for tag in metadata['tags']:
                if tag in valid_subcategories:
                    metadata['subcategory'] = tag
                    break
        
        # Extract author
        author_data = creative_work.get('author', {})
        if isinstance(author_data, dict):
            metadata['author'] = author_data.get('name', 'N/A')
    
    # Step 2: Extract views and downloads stats
    resource_stats = soup.find('ul', class_='resource-statistics')
    if resource_stats:
        li_elements = resource_stats.find_all('li')
        
        for li in li_elements:
            text = li.get_text(strip=True)
            stat_values = [s.get_text(strip=True) for s in li.find_all('span', class_='stat')]
            
            if 'view' in text.lower() and len(stat_values) >= 2:
                try:
                    metadata['stats']['views'] = int(stat_values[0].replace(',', ''))
                    metadata['stats']['views_today'] = int(stat_values[1].replace(',', ''))
                except:
                    pass
            elif 'download' in text.lower() and len(stat_values) >= 2:
                try:
                    metadata['stats']['downloads'] = int(stat_values[0].replace(',', ''))
                    metadata['stats']['downloads_today'] = int(stat_values[1].replace(',', ''))
                except:
                    pass
    
    # Step 3: Extract diamonds and hearts
    diamond_elem = soup.find('span', class_='c-num-votes')
    if diamond_elem:
        try:
            metadata['stats']['diamonds'] = int(diamond_elem.get_text(strip=True).replace(',', ''))
        except:
            pass
    
    heart_elem = soup.find('span', class_='c-num-favs')
    if heart_elem:
        try:
            metadata['stats']['hearts'] = int(heart_elem.get_text(strip=True).replace(',', ''))
        except:
            pass
    
    # Step 4: Enhanced download link detection
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href']
        text = link.get_text(strip=True)
        classes = link.get('class', [])
        
        download_info = None
        
        # Direct PM downloads - Java schematic
        if '/download/schematic/' in href.lower():
            download_info = {
                'text': text or 'Download Schematic',
                'url': href,
                'type': 'direct_pm_schematic',
                'file_type': 'schematic',
                'platform': 'java'
            }
            metadata['has_direct_download'] = True
        
        # Direct PM downloads - Java world
        elif '/download/world/' in href.lower() or '/download/worldmap/' in href.lower():
            download_info = {
                'text': text or 'Download World',
                'url': href,
                'type': 'direct_pm_world',
                'file_type': 'world',
                'platform': 'java'
            }
            metadata['has_direct_download'] = True
        
        # Direct PM downloads - Bedrock mcworld
        elif '/download/mcworld/' in href.lower():
            download_info = {
                'text': text or 'Download Bedrock World',
                'url': href,
                'type': 'direct_pm_mcworld',
                'file_type': 'world',
                'platform': 'bedrock'
            }
            metadata['has_direct_download'] = True
        
        # PM redirect links to external hosts
        elif '/download/mirror/' in href.lower() or '/download/website/' in href.lower():
            # Try to detect platform from text
            platform = 'unknown'
            if 'java' in text.lower():
                platform = 'java'
            elif 'bedrock' in text.lower():
                platform = 'bedrock'
            
            download_info = {
                'text': text or 'External Download',
                'url': href,
                'type': 'pm_external_redirect',
                'file_type': 'unknown',
                'platform': platform
            }
        
        # Direct external download hosts
        elif any(host in href.lower() for host in ['mediafire.com', 'dropbox.com', 'drive.google.com', 'mega.nz', 'patreon.com']):
            link_type = classify_download_link_v2(href, text)
            download_info = {
                'text': text,
                'url': href,
                'type': link_type,
                'file_type': 'unknown',
                'platform': 'unknown'
            }
        
        # Add download if we found one and it's not a duplicate
        if download_info and not any(d['url'] == download_info['url'] for d in metadata['downloads']):
            metadata['downloads'].append(download_info)
    
    return metadata


def collect_project_urls(driver, start_page=1, max_pages=None, 
                        category=None, categories=None, share=None, shares=None,
                        order=None, platform=None, monetization=None, 
                        time_machine=None, delay=2.0, max_empty_pages=5):
    """
    Collect project URLs from Planet Minecraft browse pages.
    
    Parameters:
    - driver: Selenium WebDriver instance
    - start_page: Page number to start from (default: 1)
    - max_pages: Maximum number of pages to scrape (None = unlimited)
    - category: Single category string (legacy, e.g., 'land-structure')
    - categories: List of category IDs (e.g., [10, 11, 18] for 3D art, Land Structure, Air Structure)
    - share: Single share type ('schematic', 'seed', or None)
    - shares: List of share types (['world_link', 'schematic'])
    - order: Sort order ('order_latest', 'order_popularity', 'order_downloads', 'order_views', 'order_hot')
    - platform: Filter by platform (1=Java, 2=Bedrock, None=any)
    - monetization: List of monetization types ([0, 1, 2] for Free, Adshortner, Monetized)
    - time_machine: Time frame filter ('last24h', 'last3d', 'last7d', 'last14d', 'last30d', 'u-1025', 'm-0925', 'y-2025')
    - delay: Delay between page requests in seconds
    - max_empty_pages: Stop after this many consecutive empty pages
    
    Returns:
    - set: Unique project URLs
    """
    
    base_url = "https://www.planetminecraft.com/projects/"
    all_project_urls = set()
    empty_page_count = 0
    current_page = start_page
    
    # Build query parameters
    params = []
    
    # Advanced mode for multiple categories/shares
    use_advanced = bool(categories or shares or monetization)
    if use_advanced:
        params.append("mode=advanced")
    
    # Categories (multiple support)
    if categories:
        for cat_id in categories:
            params.append(f"category%5B%5D={cat_id}")
    elif category:
        # Legacy single category support
        params.append(f"category={category}")
    
    # Share types (multiple support)
    if shares:
        for share_type in shares:
            params.append(f"share%5B%5D={share_type}")
    elif share:
        # Legacy single share support
        params.append(f"share={share}")
    
    # Monetization filters
    if monetization:
        for mon_type in monetization:
            params.append(f"monetization%5B%5D={mon_type}")
    
    # Time frame filter
    if time_machine:
        params.append(f"time_machine={time_machine}")
    
    # Other filters
    if order:
        params.append(f"order={order}")
    if platform:
        params.append(f"platform={platform}")
    
    param_string = "&".join(params) if params else ""
    
    print("=" * 70)
    print(f"Starting URL collection from page {start_page}")
    if param_string:
        print(f"Filters: {param_string}")
    print("=" * 70)
    
    while True:
        # Check if we've reached max_pages
        if max_pages and (current_page - start_page + 1) > max_pages:
            print(f"\nReached max_pages limit ({max_pages})")
            break
        
        # Build URL with page number
        if param_string:
            url = f"{base_url}?{param_string}&p={current_page}"
        else:
            url = f"{base_url}?p={current_page}"
        
        print(f"\nPage {current_page}: {url}")
        
        try:
            driver.get(url)
            time.sleep(delay)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            project_links = soup.find_all('a', href=lambda h: h and '/project/' in h)
            
            # Extract unique project URLs
            page_projects = set()
            for link in project_links:
                href = link.get('href', '')
                if href.startswith('/project/') and len(href.split('/')) >= 3:
                    clean_href = href.split('?')[0].rstrip('/')
                    page_projects.add(clean_href)
            
            # Check if page has projects
            if len(page_projects) == 0:
                empty_page_count += 1
                print(f"  ⚠ Empty page (count: {empty_page_count}/{max_empty_pages})")
                
                if empty_page_count >= max_empty_pages:
                    print(f"\n  Stopping: {max_empty_pages} consecutive empty pages")
                    break
            else:
                empty_page_count = 0  # Reset counter
                new_projects = page_projects - all_project_urls
                all_project_urls.update(page_projects)
                print(f"  ✓ Found {len(page_projects)} projects ({len(new_projects)} new)")
                print(f"  Total unique: {len(all_project_urls)}")
            
            current_page += 1
            
        except Exception as e:
            print(f"  ✗ Error on page {current_page}: {e}")
            break
    
    print("\n" + "=" * 70)
    print(f"Collection complete: {len(all_project_urls)} unique project URLs")
    print("=" * 70)
    
    return all_project_urls


def scrape_planet_minecraft_json(driver, 
                                 output_json='planet_minecraft_projects.json',
                                 progress_file='scraping_progress.json',
                                 start_page=1, 
                                 max_pages=None,
                                 max_projects=None,
                                 category=None,
                                 categories=None,
                                 share=None,
                                 shares=None,
                                 order=None,
                                 platform=None,
                                 monetization=None,
                                 time_machine=None,
                                 page_delay=2.0,
                                 project_delay=1.0,
                                 resume=True):
    """
    Complete scraper for Planet Minecraft - JSON output version.
    
    Parameters:
    - driver: Selenium WebDriver instance
    - output_json: Path to output JSON file
    - progress_file: Path to progress tracking JSON file
    - start_page: Page number to start URL collection
    - max_pages: Maximum pages to scrape for URLs (None = unlimited)
    - max_projects: Maximum projects to scrape metadata for (None = unlimited)
    - category: Single category string (e.g., 'land-structure')
    - categories: List of category IDs (e.g., [10, 11, 18])
    - share: Single share type ('schematic', 'seed', None)
    - shares: List of share types (['world_link', 'schematic'])
    - order: Sort order ('order_latest', 'order_popularity', etc.)
    - platform: Platform filter (1=Java, 2=Bedrock, None=any)
    - monetization: List of monetization types ([0, 1] for Free + Adshortner)
    - time_machine: Time frame ('last24h', 'last7d', 'last30d', 'y-2025', etc.)
    - page_delay: Delay between page requests (seconds)
    - project_delay: Delay between project metadata requests (seconds)
    - resume: Whether to resume from progress file if it exists
    
    Returns:
    - dict: Scraping statistics
    """
    
    # Initialize progress tracking
    progress = {
        'scraped_urls': set(),
        'failed_urls': {},
        'total_collected': 0,
        'total_scraped': 0,
        'start_time': datetime.now().isoformat(),
        'filters': {
            'category': category,
            'categories': categories,
            'share': share,
            'shares': shares,
            'order': order,
            'platform': platform,
            'monetization': monetization,
            'time_machine': time_machine
        }
    }
    
    # Load existing progress if resuming
    if resume and Path(progress_file).exists():
        print(f"Loading progress from {progress_file}...")
        with open(progress_file, 'r') as f:
            saved_progress = json.load(f)
            progress['scraped_urls'] = set(saved_progress.get('scraped_urls', []))
            progress['failed_urls'] = saved_progress.get('failed_urls', {})
            print(f"  Resuming: {len(progress['scraped_urls'])} already scraped")
    
    # Load existing data if resuming
    existing_projects = []
    if Path(output_json).exists() and resume:
        print(f"Loading existing data from {output_json}...")
        with open(output_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_projects = data.get('projects', [])
            for project in existing_projects:
                progress['scraped_urls'].add(project['url'])
        print(f"  Found {len(existing_projects)} existing projects")
    
    # Step 1: Collect project URLs
    print("\n" + "=" * 70)
    print("STEP 1: Collecting project URLs")
    print("=" * 70)
    
    project_urls = collect_project_urls(
        driver=driver,
        start_page=start_page,
        max_pages=max_pages,
        category=category,
        categories=categories,
        share=share,
        shares=shares,
        order=order,
        platform=platform,
        monetization=monetization,
        time_machine=time_machine,
        delay=page_delay
    )
    
    progress['total_collected'] = len(project_urls)
    
    # Filter out already scraped URLs
    urls_to_scrape = [url for url in project_urls if url not in progress['scraped_urls']]
    
    if max_projects:
        urls_to_scrape = urls_to_scrape[:max_projects]
    
    print(f"\nURLs to scrape: {len(urls_to_scrape)} (out of {len(project_urls)} collected)")
    
    if len(urls_to_scrape) == 0:
        print("No new URLs to scrape!")
        return progress
    
    # Step 2: Extract metadata from each project
    print("\n" + "=" * 70)
    print("STEP 2: Extracting project metadata")
    print("=" * 70)
    
    newly_scraped = []
    
    for idx, project_url in enumerate(urls_to_scrape, 1):
        full_url = f"https://www.planetminecraft.com{project_url}"
        
        print(f"\n[{idx}/{len(urls_to_scrape)}] {project_url}")
        
        try:
            # Load project page
            driver.get(full_url)
            time.sleep(project_delay)
            
            # Extract metadata
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            metadata = extract_project_metadata_v2(soup, full_url)
            
            if metadata and metadata.get('title') != 'N/A':
                newly_scraped.append(metadata)
                
                progress['scraped_urls'].add(project_url)
                progress['total_scraped'] += 1
                
                print(f"  ✓ {metadata.get('title')} - {metadata.get('subcategory', 'N/A')}")
                print(f"    Stats: {metadata['stats']['views']} views, {metadata['stats']['downloads']} downloads")
                print(f"    Downloads: {len(metadata['downloads'])} link(s)")
            else:
                print(f"  ⚠ No metadata extracted")
                progress['failed_urls'][project_url] = "No metadata"
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            progress['failed_urls'][project_url] = str(e)
        
        # Save progress every 10 projects
        if idx % 10 == 0:
            # Combine existing + newly scraped
            all_projects = existing_projects + newly_scraped
            
            # Save JSON
            output_data = {
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'total_projects': len(all_projects),
                    'filters': progress['filters']
                },
                'projects': all_projects
            }
            
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Save progress
            with open(progress_file, 'w') as f:
                json.dump({
                    'scraped_urls': list(progress['scraped_urls']),
                    'failed_urls': progress['failed_urls'],
                    'total_collected': progress['total_collected'],
                    'total_scraped': progress['total_scraped'],
                    'start_time': progress['start_time'],
                    'last_update': datetime.now().isoformat(),
                    'filters': progress['filters']
                }, f, indent=2)
            
            print(f"  📝 Progress saved ({len(all_projects)} total projects)")
    
    # Final save
    all_projects = existing_projects + newly_scraped
    
    output_data = {
        'metadata': {
            'scraped_at': datetime.now().isoformat(),
            'total_projects': len(all_projects),
            'filters': progress['filters'],
            'scrape_stats': {
                'total_collected': progress['total_collected'],
                'successfully_scraped': progress['total_scraped'],
                'failed': len(progress['failed_urls'])
            }
        },
        'projects': all_projects
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Final progress save
    progress['end_time'] = datetime.now().isoformat()
    with open(progress_file, 'w') as f:
        json.dump({
            'scraped_urls': list(progress['scraped_urls']),
            'failed_urls': progress['failed_urls'],
            'total_collected': progress['total_collected'],
            'total_scraped': progress['total_scraped'],
            'start_time': progress['start_time'],
            'end_time': progress['end_time'],
            'filters': progress['filters']
        }, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SCRAPING COMPLETE")
    print("=" * 70)
    print(f"Total URLs collected: {progress['total_collected']}")
    print(f"Successfully scraped: {progress['total_scraped']}")
    print(f"Failed: {len(progress['failed_urls'])}")
    print(f"Output saved to: {output_json}")
    print(f"Progress saved to: {progress_file}")
    print("=" * 70)
    
    return progress


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Planet Minecraft projects with optional filters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 100 pages of schematic files, sorted by latest
  python scrape_planet_minecraft.py --output schematics.json --max-pages 100 --share schematic --order order_latest
  
  # Scrape land-structure category only
  python scrape_planet_minecraft.py --output land_structures.json --category land-structure --max-pages 50
  
  # Scrape Java Edition projects
  python scrape_planet_minecraft.py --output java_projects.json --platform 1 --max-pages 200
  
  # Full scrape with resume support
  caffeinate python scrape_planet_minecraft.py --output all_projects.json --order order_latest --resume
  
Filter Options:
  category: land-structure, challenge-adventure, 3d-art, air-structure, complex, 
            educational, enviroment-landscaping, minecart, music, nether-structure, 
            piston, pixel-art, redstone-device, underground-structure, water-structure, other
  share: schematic, seed
  order: order_latest, order_popularity, order_downloads, order_views, order_hot
  platform: 1 (Java), 2 (Bedrock)
        """
    )
    
    # Output options
    parser.add_argument('--output', '-o', default='planet_minecraft_projects.json',
                        help='Output JSON file path (default: planet_minecraft_projects.json)')
    parser.add_argument('--progress', default='scraping_progress.json',
                        help='Progress file path (default: scraping_progress.json)')
    
    # Pagination options
    parser.add_argument('--start-page', type=int, default=1,
                        help='Starting page number (default: 1)')
    parser.add_argument('--max-pages', type=int, default=None,
                        help='Maximum pages to scrape for URLs (default: unlimited)')
    parser.add_argument('--max-projects', type=int, default=None,
                        help='Maximum projects to scrape metadata (default: unlimited)')
    
    # Filter options
    parser.add_argument('--category', choices=[
        'land-structure', 'challenge-adventure', '3d-art', 'air-structure', 'complex',
        'educational', 'enviroment-landscaping', 'minecart', 'music', 'nether-structure',
        'piston', 'pixel-art', 'redstone-device', 'underground-structure', 'water-structure', 'other'
    ], help='Filter by single project category (legacy)')
    
    parser.add_argument('--categories', type=str,
                        help='Filter by multiple categories (comma-separated IDs or names). '
                             'IDs: 10=3D art, 18=Air Structure, 87=Challenge/Adventure, 42=Complex, '
                             '117=Educational, 15=Environment/Landscaping, 11=Land Structure, 21=Minecart, '
                             '85=Music, 16=Nether Structure, 88=Piston, 9=Pixel Art, 14=Redstone Device, '
                             '12=Underground Structure, 13=Water Structure, 17=Other. '
                             'Example: --categories 10,11,18 or --categories "3d-art,land-structure"')
    
    parser.add_argument('--share', choices=['schematic', 'seed', 'world_link'],
                        help='Filter by single share type (legacy)')
    
    parser.add_argument('--shares', type=str,
                        help='Filter by multiple share types (comma-separated). '
                             'Options: world_link, schematic, seed, video_preview. '
                             'Example: --shares world_link,schematic')
    
    parser.add_argument('--order', choices=['order_latest', 'order_popularity', 'order_downloads', 'order_views', 'order_hot'],
                        help='Sort order')
    
    parser.add_argument('--platform', type=int, choices=[1, 2],
                        help='Filter by platform (1=Java, 2=Bedrock)')
    
    parser.add_argument('--monetization', type=str,
                        help='Filter by monetization types (comma-separated). '
                             'Options: 0=Free, 1=Adshortner, 2=Monetized. '
                             'Example: --monetization 0,1 (Free + Adshortner only)')
    
    parser.add_argument('--time-machine', type=str,
                        help='Filter by time frame. Options: last24h, last3d, last7d, last14d, last30d, '
                             'u-MMYY (e.g., u-1025 for Oct 2025), m-MMYY (e.g., m-0925 for Sep 2025), '
                             'y-YYYY (e.g., y-2025 for year 2025). Example: --time-machine last7d')
    
    # Timing options
    parser.add_argument('--page-delay', type=float, default=2.0,
                        help='Delay between page requests in seconds (default: 2.0)')
    parser.add_argument('--project-delay', type=float, default=1.5,
                        help='Delay between project requests in seconds (default: 1.5)')
    
    # Other options
    parser.add_argument('--resume', action='store_true',
                        help='Resume from progress file if it exists')
    parser.add_argument('--no-headless', action='store_true',
                        help='Show browser window (default: headless)')
    
    args = parser.parse_args()
    
    # Category name to ID mapping
    CATEGORY_MAP = {
        '3d-art': 10,
        'air-structure': 18,
        'challenge-adventure': 87,
        'complex': 42,
        'educational': 117,
        'enviroment-landscaping': 15,
        'land-structure': 11,
        'minecart': 21,
        'music': 85,
        'nether-structure': 16,
        'piston': 88,
        'pixel-art': 9,
        'redstone-device': 14,
        'underground-structure': 12,
        'water-structure': 13,
        'other': 17
    }
    
    # Parse categories if provided
    categories_list = None
    if args.categories:
        categories_list = []
        for cat in args.categories.split(','):
            cat = cat.strip()
            if cat.isdigit():
                categories_list.append(int(cat))
            elif cat in CATEGORY_MAP:
                categories_list.append(CATEGORY_MAP[cat])
            else:
                print(f"Warning: Unknown category '{cat}', skipping")
    
    # Parse shares if provided
    shares_list = None
    if args.shares:
        shares_list = [s.strip() for s in args.shares.split(',')]
    
    # Parse monetization if provided
    monetization_list = None
    if args.monetization:
        monetization_list = [int(m.strip()) for m in args.monetization.split(',')]
    
    # Setup driver
    print("Initializing Firefox WebDriver...")
    driver = setup_driver(headless=not args.no_headless)
    
    try:
        # Run scraper
        stats = scrape_planet_minecraft_json(
            driver=driver,
            output_json=args.output,
            progress_file=args.progress,
            start_page=args.start_page,
            max_pages=args.max_pages,
            max_projects=args.max_projects,
            category=args.category,
            categories=categories_list,
            share=args.share,
            shares=shares_list,
            order=args.order,
            platform=args.platform,
            monetization=monetization_list,
            time_machine=args.time_machine,
            page_delay=args.page_delay,
            project_delay=args.project_delay,
            resume=args.resume
        )
        
        print("\n✅ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Progress has been saved.")
        print(f"   Run again with --resume to continue from where you left off.")
        
    except Exception as e:
        print(f"\n\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == '__main__':
    main()
