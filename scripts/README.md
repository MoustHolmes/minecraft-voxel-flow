# Scraper Scripts

This directory contains scripts for scraping Minecraft schematics from minecraft-schematics.com.

## Quick Start

### 1. Install Dependencies

```bash
pip install selenium webdriver-manager beautifulsoup4
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
# Basic usage - scrape a small range
python scripts/run_scraper.py --start 1824 --end 2000

# Full scrape (WARNING: Takes ~10-12 hours for ~17k schematics)
python scripts/run_scraper.py --start 1824 --end 19000

# Resume from a specific ID
python scripts/run_scraper.py --start 5000 --end 19000

# Custom delay (slower = more polite to server)
python scripts/run_scraper.py --start 1824 --end 2000 --delay 1.5
```

### 3. Login Process

The script will:
1. Open Firefox browser automatically
2. Navigate to the login page
3. Wait for you to manually log in
4. Once logged in, return to the terminal and press ENTER
5. Start scraping automatically

## Features

### ✅ Smart File Extension Handling
- **Supports**: `.schematic`, `.schem`, AND `.litematic` files
- **Solution**: Script checks for all three extensions automatically
- No more missed downloads!

### ⚡ Intelligent Loading & Speed
- **Smart Waits**: Uses WebDriverWait instead of fixed sleep times
  - Proceeds immediately when page loads (often < 0.5s)
  - Waits up to 10s for slow connections (more reliable)
- **Paid Schematic Detection**: Skips non-free schematics automatically
- Default delay between requests: 0.8s (configurable)
- **Speed improvement**: ~40-50% faster than original
- **Estimated time** for full scrape: ~10-12 hours (down from ~14-16 hours)

### 📊 Output Files

All files are saved to the `data/` directory:

```
data/
├── schematics/          # Downloaded files (all formats!)
│   ├── 1824.schematic   # Schematica format
│   ├── 1825.schem       # Sponge Schematic format
│   ├── 1826.litematic   # Litematica format
│   └── ...
└── schematics_metadata.csv  # Metadata for all schematics
```

### 📋 CSV Metadata Columns

The metadata CSV includes:
- `id`: Schematic ID
- `title`: Schematic title
- `category`: Category (e.g., "Buildings", "Redstone")
- `theme`: Theme (e.g., "Medieval", "Modern")
- `size`: Dimensions (e.g., "32x64x32")
- `submitted_by`: Username of uploader
- `posted_on`: Upload date
- `downloads`: Download count
- `description`: Full description text
- `local_filename`: Actual filename (`.schematic`, `.schem`, or `.litematic`)
- `status`: Download status (`downloaded`, `not_found`, `paid_schematic`, etc.)
- `error_message`: Detailed error info for failed downloads (NEW!)

## Advanced Usage

### Resume After Interruption

If the scraper is interrupted (Ctrl+C or crash), you can resume:

```bash
# Check the last ID in your CSV file
tail -n 1 data/schematics_metadata.csv

# Resume from next ID
python scripts/run_scraper.py --start 5234 --end 19000
```

### Skip Login (Already Logged In)

If you're running multiple batches and already logged in:

```bash
python scripts/run_scraper.py --start 5000 --end 10000 --skip-login
```

### Adjust Speed

**Faster** (less polite, may risk rate limiting):
```bash
python scripts/run_scraper.py --start 1824 --end 2000 --delay 0.5
```

**Slower** (more polite to server):
```bash
python scripts/run_scraper.py --start 1824 --end 2000 --delay 2.0
```

## Troubleshooting

### "Import selenium could not be resolved"

Install dependencies:
```bash
pip install selenium webdriver-manager
```

### "Session expired" / "Redirected to login"

Your login session expired. The script will stop and you'll need to:
1. Run the script again
2. Log in manually when prompted
3. Continue from where you left off

### Download not found

If files aren't being found:
1. Check your Downloads folder - files might be accumulating there
2. Make sure Firefox download preferences are set correctly
3. The script now handles both `.schematic` and `.schem` extensions

### Browser closes immediately

Make sure you have Firefox installed. The script uses Firefox by default.

To use Chrome instead, modify `scripts/run_scraper.py`:
```python
# Change from Firefox to Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

## Performance Tips

1. **Run overnight**: A full scrape takes 10-12 hours
2. **Use default delay**: 0.8s is optimal (fast but respectful)
3. **Don't interrupt unnecessarily**: Resume feature works, but continuous runs are more efficient
4. **Monitor disk space**: ~17k files can take several GB

## Implementation Details

### Why Manual Login?

The site uses CSRF tokens and session cookies that are hard to automate reliably. Manual login ensures:
- No captcha issues
- Better success rate
- Clearer authentication status
- Respects site's security measures

### File Extension Detection

The script checks for files in this order:
1. `{id}.schematic` (Schematica - original format)
2. `{id}.schem` (Sponge Schematic - newer format)
3. `{id}.litematic` (Litematica mod format)

Whichever exists first is moved and recorded in the metadata.

### Paid Schematic Handling

Paid "non-free" schematics are automatically detected and skipped:
- Checks for text: "This creation is marked as 'non-free'"
- Marked as `paid_schematic` in CSV
- No download attempt (saves time)
- Error message explains it requires payment

## Questions?

Check the notebook `notebooks/scrape.ipynb` for development notes and testing.
