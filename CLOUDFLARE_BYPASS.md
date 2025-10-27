# 🛡️ Cloudflare Bypass Guide

## The Problem

Cloudflare has detected your scraper as a bot and is blocking access. This is a common issue with automated web scraping.

## Solutions (Try in Order)

### ✅ Solution 1: Use Your Real Firefox Profile (Recommended)

The updated `run_scraper.py` now uses your real Firefox profile by default, which makes you look more human to Cloudflare.

```bash
python scripts/run_scraper.py --start 5654 --end 26538
```

**Important:**
1. **Close ALL Firefox windows** before running
2. The script will use your actual Firefox profile (with cookies, history, etc.)
3. This makes Cloudflare think you're a real user
4. Much higher success rate!

**To disable profile (old behavior):**
```bash
python scripts/run_scraper.py --start 5654 --end 26538 --no-profile
```

### ✅ Solution 2: Use Undetected ChromeDriver (Best for Cloudflare)

This is a special Chrome driver designed specifically to bypass bot detection:

**1. Install:**
```bash
pip install undetected-chromedriver
```

**2. Run:**
```bash
python scripts/run_scraper_stealth.py --start 5654 --end 26538
```

**Why it works:**
- Automatically patches Chrome to hide automation
- Removes webdriver flags
- Mimics human behavior
- Specifically designed for Cloudflare bypass

### ✅ Solution 3: Manual Browser Interaction

When Cloudflare challenge appears:

**Do:**
- ✅ Wait 5-10 seconds for automatic verification
- ✅ Complete any CAPTCHA if shown
- ✅ Log in manually
- ✅ Browse 2-3 pages manually before starting scrape
- ✅ Keep browser window visible (don't minimize)

**Don't:**
- ❌ Click "Verify you are human" too quickly
- ❌ Refresh the page repeatedly
- ❌ Run the script immediately after login
- ❌ Use headless mode

### ✅ Solution 4: Add Random Delays

Make your scraper behave more human-like:

```bash
# Slower scraping (less suspicious)
python scripts/run_scraper_stealth.py --start 5654 --end 26538 --delay 2.0
```

Cloudflare monitors request patterns. Random longer delays help.

### ✅ Solution 5: Use Existing Session

If you can get past Cloudflare once, keep the session alive:

```bash
# First run - log in
python scripts/run_scraper_stealth.py --start 5654 --end 6000

# Subsequent runs - skip login to reuse session
python scripts/run_scraper_stealth.py --start 6001 --end 7000 --skip-login
```

## What Changed in the Scripts

### `run_scraper.py` (Updated)

Now includes anti-detection features:

```python
# Uses your real Firefox profile (cookies, history, etc.)
options.add_argument("-profile")
options.add_argument(str(profile_path))

# Hides webdriver flag
options.set_preference("dom.webdriver.enabled", False)

# Uses real user agent
options.set_preference("general.useragent.override", "Mozilla/5.0...")

# Modifies navigator.webdriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

### `run_scraper_stealth.py` (NEW)

Uses `undetected-chromedriver`:
- Automatically patches Chrome
- Removes all automation signatures
- Best for Cloudflare bypass

## Debugging Tips

### Check if Cloudflare is Blocking You

When the browser opens, look for:
- "Checking your browser before accessing..."
- "Just a moment..."
- Endless loading/redirect loops
- CAPTCHA challenges

### If Still Blocked

1. **Try different browser:**
   - Firefox: `run_scraper.py`
   - Chrome (stealth): `run_scraper_stealth.py`

2. **Use VPN:**
   - Your IP might be flagged
   - Try a different network

3. **Wait it out:**
   - Cloudflare blocks are often temporary
   - Try again in 1-2 hours

4. **Run during off-peak hours:**
   - Less traffic = less scrutiny
   - Try late night or early morning

## Advanced: Selenium Stealth (Firefox)

If you want stealth with Firefox, install:

```bash
pip install selenium-stealth
```

Then modify `run_scraper.py`:
```python
from selenium_stealth import stealth

# After creating driver:
stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)
```

## What Cloudflare Detects

Cloudflare looks for:
- ❌ `navigator.webdriver === true` (automation flag)
- ❌ Missing browser plugins
- ❌ Unusual user-agent strings
- ❌ Too-fast request patterns
- ❌ No cookies/history
- ❌ Headless browser indicators
- ❌ Inconsistent TLS fingerprints

Our solutions fix most of these! ✅

## Success Checklist

Before running scraper, ensure:
- [ ] Using real Firefox profile OR undetected-chromedriver
- [ ] All Firefox windows closed (if using profile)
- [ ] Browser window stays visible (not minimized)
- [ ] Manually browse 2-3 pages after login
- [ ] Wait 10+ seconds before starting scrape
- [ ] Using reasonable delay (0.8s+)
- [ ] Not using headless mode

## Quick Reference

| Method | Command | Best For |
|--------|---------|----------|
| **Firefox Profile** | `python scripts/run_scraper.py --start X --end Y` | Default, good for most cases |
| **Stealth Chrome** | `python scripts/run_scraper_stealth.py --start X --end Y` | Cloudflare bypass, recommended! |
| **No Profile** | `python scripts/run_scraper.py --no-profile --start X --end Y` | Testing only |
| **Slow Mode** | `python scripts/run_scraper_stealth.py --delay 2.0 --start X --end Y` | Very suspicious IP |

## Still Having Issues?

Try this combination (most reliable):

```bash
# 1. Install stealth driver
pip install undetected-chromedriver

# 2. Run with longer delays
python scripts/run_scraper_stealth.py --start 5654 --end 26538 --delay 1.5

# 3. When browser opens:
#    - Wait 10 seconds
#    - Complete any Cloudflare challenge
#    - Log in
#    - Browse 2-3 pages manually
#    - Return to terminal and press ENTER
```

This has the highest success rate for bypassing Cloudflare! 🎯
