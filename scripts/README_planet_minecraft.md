# Planet Minecraft Scraper

Standalone Python script to scrape project metadata from Planet Minecraft with optional filters.

## Features

- ✅ Complete metadata extraction (title, author, description, stats, tags)
- ✅ Full download link detection (Java, Bedrock, schematic, world, external)
- ✅ Platform detection (Java vs Bedrock)
- ✅ JSON output with clean nested structure
- ✅ Progress tracking and resume capability
- ✅ Optional filters (category, platform, share type, sort order)
- ✅ Rate limiting to be polite to server

## Installation

```bash
# Install dependencies (if not already installed)
pip install selenium beautifulsoup4
```

## Quick Start

```bash
# Scrape 10 pages of schematic files (test run)
python scripts/scrape_planet_minecraft.py --output data/test.json --max-pages 10 --share schematic

# Scrape with caffeinate to prevent sleep
caffeinate python scripts/scrape_planet_minecraft.py --output data/schematics.json --max-pages 100 --share schematic --order order_latest
```

## Usage Examples

### 1. Scrape Schematic Files (Recommended for structures)
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/schematics.json \
    --share schematic \
    --order order_latest \
    --max-pages 500 \
    --resume
```

### 2. Scrape Specific Category
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/land_structures.json \
    --category land-structure \
    --order order_popularity \
    --max-pages 200 \
    --resume
```

### 3. Scrape Java Edition Only
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/java_projects.json \
    --platform 1 \
    --share schematic \
    --max-pages 300 \
    --resume
```

### 4. Full Scrape (All Projects)
⚠️ **Warning**: This will take a VERY long time (days/weeks) and generate large files

```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/all_projects.json \
    --order order_latest \
    --max-pages 10000 \
    --page-delay 2.5 \
    --project-delay 2.0 \
    --resume
```

### 5. Resume Interrupted Scraping
```bash
# If scraping was interrupted, just run the same command with --resume
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/schematics.json \
    --share schematic \
    --resume
```

## Command Line Options

### Output Options
- `--output`, `-o`: Output JSON file path (default: `planet_minecraft_projects.json`)
- `--progress`: Progress file path (default: `scraping_progress.json`)

### Pagination Options
- `--start-page`: Starting page number (default: 1)
- `--max-pages`: Maximum pages to scrape (default: unlimited)
- `--max-projects`: Maximum projects to scrape (default: unlimited)

### Filter Options
- `--category`: Filter by category
  - Options: `land-structure`, `challenge-adventure`, `3d-art`, `air-structure`, `complex`, `educational`, `enviroment-landscaping`, `minecart`, `music`, `nether-structure`, `piston`, `pixel-art`, `redstone-device`, `underground-structure`, `water-structure`, `other`
  
- `--share`: Filter by share type
  - Options: `schematic`, `seed`
  
- `--order`: Sort order
  - Options: `order_latest` (newest first), `order_popularity`, `order_downloads`, `order_views`, `order_hot`
  
- `--platform`: Filter by platform
  - Options: `1` (Java Edition), `2` (Bedrock Edition)

### Timing Options
- `--page-delay`: Delay between page requests in seconds (default: 2.0)
- `--project-delay`: Delay between project requests in seconds (default: 1.5)

### Other Options
- `--resume`: Resume from progress file if it exists
- `--no-headless`: Show browser window (useful for debugging)

## Output Format

The scraper outputs JSON with this structure:

```json
{
  "metadata": {
    "scraped_at": "2025-10-10T12:00:00",
    "total_projects": 1234,
    "filters": {
      "category": "land-structure",
      "share": "schematic",
      "order": "order_latest"
    },
    "scrape_stats": {
      "total_collected": 1250,
      "successfully_scraped": 1234,
      "failed": 16
    }
  },
  "projects": [
    {
      "url": "https://www.planetminecraft.com/project/example",
      "title": "Example Project",
      "author": "BuilderName",
      "category": "Map",
      "subcategory": "land-structure",
      "description": "Project description...",
      "tags": ["modern", "city", "land-structure"],
      "posted_date": "2025-01-15T00:00:00",
      "updated_date": "2025-01-20T00:00:00",
      "stats": {
        "views": 1234,
        "views_today": 56,
        "downloads": 789,
        "downloads_today": 12,
        "diamonds": 45,
        "hearts": 23
      },
      "downloads": [
        {
          "text": "Download Schematic",
          "url": "/project/example/download/schematic/",
          "type": "direct_pm_schematic",
          "file_type": "schematic",
          "platform": "java"
        },
        {
          "text": "Download Bedrock mcworld",
          "url": "/project/example/download/mcworld/",
          "type": "direct_pm_mcworld",
          "file_type": "world",
          "platform": "bedrock"
        }
      ],
      "has_direct_download": true
    }
  ]
}
```

## Progress Tracking

The scraper automatically saves progress every 10 projects to a progress file (default: `scraping_progress.json`). If interrupted:

1. The progress file contains all scraped URLs
2. The output JSON contains all successfully scraped projects
3. Use `--resume` to continue from where you left off

## Tips

1. **Start small**: Test with `--max-pages 5` first
2. **Use filters**: Narrow scope with `--share schematic` or `--category`
3. **Use caffeinate**: Prevents Mac from sleeping during long scrapes
4. **Monitor progress**: Check output file size periodically
5. **Be polite**: Don't reduce delays too much (respect server load)
6. **Resume capability**: Safe to interrupt with Ctrl+C, just resume later

## Recommended Workflows

### For ML/Data Science (Structure Generation)
```bash
# Get all schematics, newest first, Java only
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/training_data.json \
    --share schematic \
    --platform 1 \
    --order order_latest \
    --max-pages 1000 \
    --resume
```

### For Building Dataset by Category
```bash
# Scrape each category separately for easier management
for category in land-structure challenge-adventure pixel-art; do
    caffeinate python scripts/scrape_planet_minecraft.py \
        --output data/planet_minecraft/${category}.json \
        --category ${category} \
        --share schematic \
        --max-pages 100 \
        --resume
done
```

### For Incremental Updates
```bash
# Get newest projects (for daily/weekly updates)
python scripts/scrape_planet_minecraft.py \
    --output data/planet_minecraft/latest.json \
    --order order_latest \
    --max-pages 20 \
    --resume
```

## Troubleshooting

### Browser not found
```bash
# Install Firefox (required for Selenium)
brew install firefox  # macOS
```

### Out of memory
- Reduce `--max-pages` to scrape in smaller batches
- Process and delete large JSON files periodically

### Rate limiting / 403 errors
- Increase delays: `--page-delay 3.0 --project-delay 2.5`
- Add random jitter to delays (modify script if needed)

### Interrupted scraping
- Always use `--resume` to continue
- Check progress file to see how many were scraped
- Output JSON is valid even if interrupted

## Performance Estimates

- ~25-30 projects per page
- ~2-3 seconds per page (with delays)
- ~1.5-2 seconds per project (with delays)
- 100 pages ≈ 2,500 projects ≈ 1-2 hours
- 1,000 pages ≈ 25,000 projects ≈ 12-20 hours
- 10,000 pages ≈ 250,000 projects ≈ 5-8 days

Use `caffeinate` to prevent sleep during long runs!
