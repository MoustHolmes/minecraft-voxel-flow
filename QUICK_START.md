# 🚀 Quick Reference - Minecraft Schematic Scraper

## Installation
```bash
pip install selenium webdriver-manager
```

## Quick Test (5 schematics)
```bash
python scripts/test_scraper.py
```

## Full Scrape
```bash
# Scrape all ~17k schematics (10-12 hours)
python scripts/run_scraper.py --start 1824 --end 19000

# Scrape a batch
python scripts/run_scraper.py --start 1824 --end 5000

# Resume from specific ID
python scripts/run_scraper.py --start 5234 --end 19000

# Custom speed
python scripts/run_scraper.py --start 1824 --end 19000 --delay 1.0
```

## What's Fixed?

✅ **File formats**: Handles `.schematic`, `.schem`, AND `.litematic`  
💰 **Paid detection**: Auto-skips paid "non-free" schematics  
🔍 **Error logging**: New `error_message` column with detailed debug info  
⚡ **Smart loading**: WebDriverWait instead of sleep - faster & more reliable  
🖥️ **Runnable**: Standalone scripts, not just notebook  
🔄 **Resumable**: Easy to continue after interruption  

## Output Files
```
data/
├── schematics/              # Downloaded files (all formats!)
│   ├── 1824.schematic
│   ├── 1825.schem
│   ├── 1826.litematic      # All three types supported!
│   └── ...
└── schematics_metadata.csv  # All metadata + error details
```

## Common Commands

```bash
# Check progress
tail -n 1 data/schematics_metadata.csv

# Count downloaded files
ls data/schematics/ | wc -l

# Check for errors in CSV
grep "error\|failed" data/schematics_metadata.csv
```

## Help

For detailed documentation:
- `scripts/README.md` - Full usage guide
- `SCRAPER_IMPROVEMENTS.md` - What changed and why

Questions? Check the troubleshooting section in `scripts/README.md`
