#!/usr/bin/env python3
"""
Compare schematics in downloads folder vs scraped folder.
Shows which IDs are in downloads but not yet scraped.
"""

from pathlib import Path
import re
import csv

def extract_id_from_filename(filename):
    """Extract numeric ID from filename like '1824.schematic' or '1824.schem'"""
    match = re.match(r'(\d+)\.(schematic|schem|litematic)', filename)
    if match:
        return int(match.group(1))
    return None

def get_ids_from_folder(folder_path):
    """Get set of schematic IDs from a folder"""
    folder = Path(folder_path)
    if not folder.exists():
        return set()
    
    ids = set()
    for file in folder.iterdir():
        if file.is_file():
            file_id = extract_id_from_filename(file.name)
            if file_id:
                ids.add(file_id)
    return ids

def get_ids_from_csv(csv_path):
    """Get set of schematic IDs from CSV (successfully downloaded ones)"""
    csv_file = Path(csv_path)
    if not csv_file.exists():
        return set()
    
    ids = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'downloaded':
                ids.add(int(row['id']))
    return ids

def main():
    # Paths
    downloads_folder = Path.home() / "Downloads" / "schematics"
    scraped_folder = Path("data") / "schematics"
    metadata_csv = Path("data") / "schematics_metadata.csv"
    
    print("="*70)
    print("SCHEMATIC COMPARISON")
    print("="*70)
    print(f"\nDownloads folder: {downloads_folder}")
    print(f"Scraped folder:   {scraped_folder}")
    print(f"Metadata CSV:     {metadata_csv}")
    print()
    
    # Get IDs from each source
    print("Reading files...")
    downloads_ids = get_ids_from_folder(downloads_folder)
    scraped_ids = get_ids_from_folder(scraped_folder)
    csv_ids = get_ids_from_csv(metadata_csv)
    
    print(f"✓ Downloads folder: {len(downloads_ids)} schematics")
    print(f"✓ Scraped folder:   {len(scraped_ids)} schematics")
    print(f"✓ CSV (downloaded): {len(csv_ids)} schematics")
    print()
    
    # Find differences
    in_downloads_not_scraped = downloads_ids - scraped_ids
    in_downloads_not_in_csv = downloads_ids - csv_ids
    in_scraped_not_downloads = scraped_ids - downloads_ids
    
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    
    # IDs in downloads but not scraped yet
    if in_downloads_not_scraped:
        print(f"📥 In Downloads but NOT in scraped folder: {len(in_downloads_not_scraped)} files")
        sorted_ids = sorted(in_downloads_not_scraped)
        
        # Show ranges
        ranges = []
        start = sorted_ids[0]
        end = sorted_ids[0]
        
        for i in range(1, len(sorted_ids)):
            if sorted_ids[i] == end + 1:
                end = sorted_ids[i]
            else:
                if start == end:
                    ranges.append(f"{start}")
                else:
                    ranges.append(f"{start}-{end}")
                start = sorted_ids[i]
                end = sorted_ids[i]
        
        if start == end:
            ranges.append(f"{start}")
        else:
            ranges.append(f"{start}-{end}")
        
        print(f"   ID Ranges: {', '.join(ranges[:10])}")
        if len(ranges) > 10:
            print(f"   ... and {len(ranges) - 10} more ranges")
        
        # Show first 20 IDs
        print(f"   First 20 IDs: {sorted_ids[:20]}")
        if len(sorted_ids) > 20:
            print(f"   ... and {len(sorted_ids) - 20} more")
        print()
    else:
        print("✅ All downloads are in scraped folder!")
        print()
    
    # IDs in scraped but not in downloads
    if in_scraped_not_downloads:
        print(f"📤 In scraped folder but NOT in Downloads: {len(in_scraped_not_downloads)} files")
        sorted_ids = sorted(in_scraped_not_downloads)
        print(f"   First 20 IDs: {sorted_ids[:20]}")
        if len(sorted_ids) > 20:
            print(f"   ... and {len(sorted_ids) - 20} more")
        print()
    else:
        print("✅ All scraped files are in Downloads!")
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    total_unique = len(downloads_ids | scraped_ids)
    overlap = len(downloads_ids & scraped_ids)
    
    print(f"Total unique schematics across both:     {total_unique}")
    print(f"Schematics in both locations (overlap):  {overlap}")
    print(f"Only in Downloads:                        {len(in_downloads_not_scraped)}")
    print(f"Only in Scraped:                          {len(in_scraped_not_downloads)}")
    print()
    
    # Recommendations
    if in_downloads_not_scraped:
        print("💡 RECOMMENDATION:")
        print("   You have files in Downloads that aren't in your scraped folder.")
        print("   You can move them with:")
        print(f"   cp ~/Downloads/schematics/*.schematic data/schematics/")
        print(f"   cp ~/Downloads/schematics/*.schem data/schematics/")
        print(f"   cp ~/Downloads/schematics/*.litematic data/schematics/")
        print()
        
        # Check if these IDs are in the CSV
        ids_with_csv_entries = in_downloads_not_scraped & csv_ids
        if ids_with_csv_entries:
            print(f"   ⚠️  {len(ids_with_csv_entries)} of these IDs are already in your CSV!")
            print(f"      They were logged but files weren't moved properly.")
            print()
    
    # Save missing IDs to file
    if in_downloads_not_scraped:
        output_file = Path("missing_from_scraped.txt")
        with open(output_file, 'w') as f:
            for schematic_id in sorted(in_downloads_not_scraped):
                f.write(f"{schematic_id}\n")
        print(f"📄 Saved missing IDs to: {output_file}")
        print()

if __name__ == "__main__":
    main()
