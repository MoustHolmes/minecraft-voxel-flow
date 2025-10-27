# Planet Minecraft Advanced Filtering Examples

## Using Advanced Filters

The scraper now supports all Planet Minecraft advanced search parameters!

## Category Filtering

### Multiple Categories
```bash
# Using category IDs
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/multiple_categories.json \
    --categories "10,11,18" \
    --max-pages 50 \
    --resume

# Using category names
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/structures.json \
    --categories "3d-art,land-structure,air-structure" \
    --max-pages 50 \
    --resume
```

### Category ID Reference
- 10 = 3D Art
- 18 = Air Structure
- 87 = Challenge / Adventure
- 42 = Complex
- 117 = Educational
- 15 = Environment / Landscaping
- 11 = Land Structure
- 21 = Minecart
- 85 = Music
- 16 = Nether Structure
- 88 = Piston
- 9 = Pixel Art
- 14 = Redstone Device
- 12 = Underground Structure
- 13 = Water Structure
- 17 = Other

### Exclude Specific Categories
To exclude Music (85) and Piston (88), include all others:
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/no_music_piston.json \
    --categories "10,18,87,42,117,15,11,21,16,9,14,12,13,17" \
    --max-pages 100 \
    --resume
```

## Share Type Filtering

### Multiple Share Types
```bash
# Downloadable worlds AND schematics
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/worlds_and_schematics.json \
    --shares "world_link,schematic" \
    --platform 1 \
    --max-pages 100 \
    --resume
```

### Share Type Options
- `world_link` = Downloadable world files
- `schematic` = Schematic files
- `seed` = World seeds only
- `video_preview` = Has video preview

## Monetization Filtering

### Free Content Only
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/free_only.json \
    --monetization "0" \
    --shares "world_link,schematic" \
    --max-pages 100 \
    --resume
```

### Free + Adshortner (Exclude Patreon/Monetized)
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/free_adshortner.json \
    --monetization "0,1" \
    --shares "schematic" \
    --max-pages 100 \
    --resume
```

### Monetization Options
- 0 = Free
- 1 = Adshortner (free but with ad link)
- 2 = Monetized (Patreon/paid content)

## Time Frame Filtering

### Last 24 Hours
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/last_24h.json \
    --time-machine "last24h" \
    --shares "schematic" \
    --max-pages 10 \
    --resume
```

### Last Week
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/last_week.json \
    --time-machine "last7d" \
    --shares "schematic" \
    --platform 1 \
    --max-pages 20 \
    --resume
```

### Specific Month
```bash
# September 2025
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/september_2025.json \
    --time-machine "m-0925" \
    --max-pages 50 \
    --resume

# October 2025 (current month format: u-MMYY)
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/october_2025.json \
    --time-machine "u-1025" \
    --max-pages 50 \
    --resume
```

### Specific Year
```bash
# All projects from 2025
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/year_2025.json \
    --time-machine "y-2025" \
    --shares "schematic" \
    --max-pages 100 \
    --resume
```

### Time Frame Options
- `last24h` = Last 24 hours
- `last3d` = Last 3 days
- `last7d` = Last 7 days
- `last14d` = Last 14 days
- `last30d` = Last 30 days
- `u-MMYY` = Current month (e.g., `u-1025` for October 2025)
- `m-MMYY` = Specific month (e.g., `m-0925` for September 2025)
- `y-YYYY` = Specific year (e.g., `y-2025` for 2025)

## Complete Advanced Search Example

Replicate your exact URL filters:
```bash
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/advanced_search.json \
    --categories "10,18,87,42,117,15,11,21,16,9,14,12,13,17" \
    --shares "world_link,schematic" \
    --platform 1 \
    --monetization "0,1" \
    --time-machine "last24h" \
    --order "order_latest" \
    --max-pages 50 \
    --resume
```

This matches your URL:
- All categories except Music (85) and Piston (88)
- Downloadable + Schematic (no video preview or seeds)
- Java Edition only
- Free + Adshortner only (no monetized)
- Last 24 hours

## Incremental Daily Scraping

For daily updates of new content:
```bash
#!/bin/bash
# daily_scrape.sh

DATE=$(date +%Y%m%d)

caffeinate python scripts/scrape_planet_minecraft.py \
    --output "data/daily/projects_${DATE}.json" \
    --time-machine "last24h" \
    --shares "world_link,schematic" \
    --platform 1 \
    --monetization "0,1" \
    --order "order_latest" \
    --max-pages 10 \
    --resume
```

## Weekly Scraping

For weekly new structures:
```bash
#!/bin/bash
# weekly_scrape.sh

WEEK=$(date +%Y_W%U)

caffeinate python scripts/scrape_planet_minecraft.py \
    --output "data/weekly/projects_${WEEK}.json" \
    --time-machine "last7d" \
    --categories "10,11,18,42" \
    --shares "schematic" \
    --platform 1 \
    --monetization "0,1" \
    --order "order_popularity" \
    --max-pages 50 \
    --resume
```

## Combining with Other Filters

### High-quality recent structures
```bash
# Recent land structures, sorted by popularity, Java only, free
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/quality_structures.json \
    --categories "11" \
    --shares "schematic" \
    --platform 1 \
    --monetization "0" \
    --time-machine "last30d" \
    --order "order_popularity" \
    --max-pages 100 \
    --resume
```

### Educational content
```bash
# Educational projects with worlds/schematics
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/educational.json \
    --categories "117" \
    --shares "world_link,schematic" \
    --platform 1 \
    --order "order_downloads" \
    --max-pages 50 \
    --resume
```

### Challenge maps
```bash
# Recent challenge/adventure maps
caffeinate python scripts/scrape_planet_minecraft.py \
    --output data/challenges.json \
    --categories "87" \
    --shares "world_link" \
    --time-machine "last30d" \
    --order "order_popularity" \
    --max-pages 50 \
    --resume
```

## Tips

1. **Test with small samples**: Always test with `--max-pages 5` first
2. **Combine filters wisely**: More filters = fewer results but more targeted
3. **Use time-machine for updates**: `last24h` or `last7d` for incremental scraping
4. **Monetization filter**: Use `0,1` to exclude Patreon-only content
5. **Platform matters**: Java (1) has more schematic support than Bedrock (2)
6. **Order by relevance**: 
   - `order_latest` for new content
   - `order_popularity` for quality
   - `order_downloads` for popular downloads
