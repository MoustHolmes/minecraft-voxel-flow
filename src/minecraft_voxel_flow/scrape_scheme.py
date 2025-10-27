from pathlib import Path
import csv
from bs4 import BeautifulSoup
import shutil
import os
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def selenium_scraper(driver, start_id, end_id, delay=0.8):
    """
    Scrape schematics using Selenium with an authenticated browser session.
    
    Args:
        driver: Selenium WebDriver instance (already logged in)
        start_id: Starting schematic ID
        end_id: Ending schematic ID
        delay: Delay between requests in seconds (default 0.8 for speed)
    """
    
    # Setup paths
    # Find project root by looking for the scripts directory
    current_path = Path.cwd()
    if (current_path / "scripts").exists():
        # Already in project root
        PROJECT_ROOT = current_path
    elif (current_path.parent / "scripts").exists():
        # In a subdirectory
        PROJECT_ROOT = current_path.parent
    else:
        # Fallback: look for pyproject.toml or data directory
        if (current_path / "pyproject.toml").exists():
            PROJECT_ROOT = current_path
        elif (current_path.parent / "pyproject.toml").exists():
            PROJECT_ROOT = current_path.parent
        else:
            PROJECT_ROOT = current_path
    
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_FOLDER = DATA_DIR / "schematics"
    METADATA_FILE = DATA_DIR / "schematics_metadata.csv"
    DOWNLOADS_FOLDER = Path.home() / "Downloads"
    
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("DIRECTORY SETUP")
    print(f"{'='*60}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Downloads folder: {DOWNLOADS_FOLDER}")
    print(f"Metadata CSV: {METADATA_FILE}")
    print(f"{'='*60}\n")
    
    # CSV headers
    csv_headers = ['id', 'title', 'category', 'theme', 'size', 'submitted_by', 
                   'posted_on', 'downloads', 'description', 'local_filename', 'status', 'error_message']
    
    successful = 0
    failed = 0
    not_found = 0
    
    # Check if CSV already exists to decide whether to write header
    csv_exists = METADATA_FILE.exists()
    
    # Open in append mode to preserve existing data
    with open(METADATA_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        
        # Only write header if file is new
        if not csv_exists:
            writer.writeheader()
        
        for schematic_id in range(start_id, end_id + 1):
            print(f"\n{'='*60}")
            print(f"Processing Schematic ID: {schematic_id}")
            print(f"{'='*60}")
            
            page_url = f"https://www.minecraft-schematics.com/schematic/{schematic_id}/"
            
            try:
                # Navigate to schematic page
                driver.get(page_url)
                
                # Wait for page to load (explicit wait is more reliable than sleep)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                except Exception as wait_error:
                    print(f"✗ Page load timeout: {wait_error}")
                    metadata = {
                        'id': schematic_id,
                        'title': 'N/A', 'category': 'N/A', 'theme': 'N/A',
                        'size': 'N/A', 'submitted_by': 'N/A', 'posted_on': 'N/A',
                        'downloads': '0', 'description': 'N/A',
                        'local_filename': 'N/A', 'status': 'page_load_timeout',
                        'error_message': str(wait_error)
                    }
                    writer.writerow(metadata)
                    failed += 1
                    time.sleep(delay)
                    continue
                
                # Check if page exists (look at current URL after any redirects)
                current_url = driver.current_url
                
                # If redirected away, it might not exist
                if str(schematic_id) not in current_url:
                    print(f"✗ Schematic not found (redirected to {current_url})")
                    metadata = {
                        'id': schematic_id,
                        'title': 'N/A', 'category': 'N/A', 'theme': 'N/A',
                        'size': 'N/A', 'submitted_by': 'N/A', 'posted_on': 'N/A',
                        'downloads': '0', 'description': 'N/A',
                        'local_filename': 'N/A', 'status': 'not_found',
                        'error_message': f'Redirected to {current_url}'
                    }
                    writer.writerow(metadata)
                    not_found += 1
                    time.sleep(delay)
                    continue
                
                # Parse page with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Check if this is a paid schematic
                page_text = soup.get_text()
                if 'This creation is marked as "non-free"' in page_text or 'you\'ll need to make a payment' in page_text:
                    print(f"⊘ Paid schematic - skipping")
                    metadata = {
                        'id': schematic_id,
                        'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else 'N/A',
                        'category': 'N/A', 'theme': 'N/A',
                        'size': 'N/A', 'submitted_by': 'N/A', 'posted_on': 'N/A',
                        'downloads': '0', 'description': 'N/A',
                        'local_filename': 'N/A', 'status': 'paid_schematic',
                        'error_message': 'Non-free schematic requiring payment'
                    }
                    writer.writerow(metadata)
                    csvfile.flush()
                    not_found += 1
                    time.sleep(delay)
                    continue
                
                # Extract metadata
                def get_info_from_table(label):
                    label_tag = soup.find('strong', string=lambda x: x and label in x if x else False)
                    if label_tag and label_tag.parent:
                        value_cell = label_tag.parent.find_next_sibling('td')
                        if value_cell:
                            return value_cell.get_text(strip=True)
                    return 'N/A'
                
                metadata = {
                    'id': schematic_id,
                    'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else 'N/A',
                    'category': get_info_from_table('Category'),
                    'theme': get_info_from_table('Theme'),
                    'size': get_info_from_table('Size'),
                    'submitted_by': get_info_from_table('Submitted by'),
                    'posted_on': get_info_from_table('Posted on'),
                    'downloads': '0',
                    'description': 'N/A',
                    'local_filename': 'N/A',
                    'status': 'pending',
                    'error_message': ''
                }
                
                # Extract downloads count
                downloads_text = get_info_from_table('Download')
                if 'downloaded' in downloads_text:
                    match = re.search(r'(\d+)', downloads_text)
                    if match:
                        metadata['downloads'] = match.group(1)
                
                # Extract description - look for p tag in span10 divs with substantial content
                span10_divs = soup.find_all('div', class_='span10')
                for div in span10_divs:
                    p_tags = div.find_all('p')
                    for p in p_tags:
                        text = p.get_text(strip=True)
                        # Check if this looks like a description (substantial content)
                        if len(text) > 30 and not text.startswith('Category:') and not text.startswith('Theme:'):
                            metadata['description'] = text
                            break
                    if metadata['description'] != 'N/A':
                        break
                
                print(f"Title: {metadata['title']}")
                print(f"Category: {metadata['category']}")
                print(f"Size: {metadata['size']}")
                
                # Now download the file
                download_page_url = f"https://www.minecraft-schematics.com/schematic/{schematic_id}/download/"
                print(f"\nNavigating to download page...")
                
                driver.get(download_page_url)
                
                # Wait for download page to load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except Exception as wait_error:
                    print(f"✗ Download page load timeout: {wait_error}")
                    metadata['status'] = 'download_page_timeout'
                    metadata['error_message'] = str(wait_error)
                    writer.writerow(metadata)
                    csvfile.flush()
                    failed += 1
                    time.sleep(delay)
                    continue
                
                # Check if we were redirected to login
                if 'login' in driver.current_url:
                    print("✗ Redirected to login - session expired!")
                    metadata['status'] = 'auth_required'
                    metadata['error_message'] = 'Session expired, redirected to login'
                    writer.writerow(metadata)
                    csvfile.flush()
                    failed += 1
                    break  # Stop scraping, need to re-login
                
                # Find and click the actual download link
                try:
                    # Wait for download link to be clickable
                    download_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download Schematic File')]"))
                    )
                    download_link.click()
                    
                    # Give download a moment to start
                    time.sleep(1.2)
                    
                    # Check for all possible file extensions
                    possible_extensions = ['.schematic', '.schem', '.litematic']
                    file_found = False
                    
                    for ext in possible_extensions:
                        filename = f"{schematic_id}{ext}"
                        source_path = DOWNLOADS_FOLDER / filename
                        
                        if source_path.exists():
                            dest_path = OUTPUT_FOLDER / filename
                            shutil.move(str(source_path), str(dest_path))
                            print(f"✓ Downloaded and moved: {filename}")
                            metadata['local_filename'] = filename
                            metadata['status'] = 'downloaded'
                            writer.writerow(metadata)
                            csvfile.flush()
                            successful += 1
                            file_found = True
                            break
                    
                    if not file_found:
                        # Check what files ARE in the downloads folder for debugging
                        recent_files = sorted(DOWNLOADS_FOLDER.glob('*'), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
                        recent_files_str = ', '.join([f.name for f in recent_files])
                        error_msg = f'File not found with extensions {possible_extensions}. Recent files: {recent_files_str}'
                        print(f"⚠ {error_msg}")
                        metadata['status'] = 'file_not_found'
                        metadata['error_message'] = error_msg
                        writer.writerow(metadata)
                        csvfile.flush()
                        failed += 1
                        
                except Exception as click_error:
                    error_msg = f'{type(click_error).__name__}: {str(click_error)}'
                    print(f"✗ Could not click download link: {error_msg}")
                    metadata['status'] = 'download_failed'
                    metadata['error_message'] = error_msg
                    writer.writerow(metadata)
                    csvfile.flush()
                    failed += 1
                
            except Exception as e:
                error_msg = f'{type(e).__name__}: {str(e)}'
                print(f"✗ Error: {error_msg}")
                metadata = {
                    'id': schematic_id,
                    'title': 'N/A', 'category': 'N/A', 'theme': 'N/A',
                    'size': 'N/A', 'submitted_by': 'N/A', 'posted_on': 'N/A',
                    'downloads': '0', 'description': 'N/A',
                    'local_filename': 'N/A', 'status': 'error',
                    'error_message': error_msg
                }
                writer.writerow(metadata)
                failed += 1
            
            # Be respectful with delays
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Not Found: {not_found}")
    print(f"✗ Failed: {failed}")
    print(f"\nFiles saved to: {OUTPUT_FOLDER}")
    print(f"Metadata saved to: {METADATA_FILE}")