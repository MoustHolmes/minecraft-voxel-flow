#!/bin/bash
# Make scripts executable
chmod +x scripts/run_scraper.py
chmod +x scripts/test_scraper.py

echo "✓ Scripts are now executable"
echo ""
echo "Test the scraper with 5 schematics:"
echo "  python scripts/test_scraper.py"
echo ""
echo "Run full scraper:"
echo "  python scripts/run_scraper.py --start 1824 --end 19000"
