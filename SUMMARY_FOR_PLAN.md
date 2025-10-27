# BlueMap Integration Summary

## Current Status

✅ **What's Working:**
- Matplotlib rendering system (3 successful test renders)
- BlueMap CLI setup complete
- BlueMap screenshot automation functional
- All infrastructure in place

❌ **What's Not Working:**
- BlueMap can't render our programmatically-created worlds
- Need actual Minecraft to generate a template world

## Files Organized

### Active Scripts
```
scripts/
├── render_schematics.py              ✅ Matplotlib showcase renderer (WORKING)
├── generate_previews.py              ✅ Matplotlib 2D previews (WORKING)
├── test_bluemap_screenshot.py        ✅ BlueMap automation (WORKS, but empty world)
├── amulet_schematic_to_world.py      ⏸️  BlueMap solution (needs Minecraft template)
└── bluemap_screenshot_demo.py        ✅ Original wiki automation
```

### Archived (Failed Attempts)
```
scripts/archive_failed_attempts/
├── README.md                         📝 Explains why these failed
├── build_minecraft_world.py          ❌ anvil-parser direct approach
├── schematic_to_minecraft_world.py   ❌ Early anvil attempt
├── schematic_to_bluemap_world.py     ❌ Amulet direct creation
├── fix_world_for_bluemap.py          ❌ Post-process attempt
└── create_world_properly.py          ❌ Various dead ends
```

### Documentation
```
BLUEMAP_ATTEMPTS_REPORT.md            📊 Complete technical analysis (4000+ words)
BLUEMAP_STATUS.md                     📋 Quick status reference
```

### Generated Output
```
data/bluemap_screenshots/
├── 10234_showcase.png                ✅ 521 KB, 2820x2180 (matplotlib)
├── 7704_showcase.png                 ✅ 699 KB, 2820x2180 (matplotlib)
└── 9719_showcase.png                 ✅ 788 KB, 2820x2180 (matplotlib)

test_screenshot.png                   ✅ 20 KB, 1280x720 (BlueMap - black)
```

## What I Tried (In Order)

### Attempt 1: anvil-parser Direct World Creation
- Created proper world structure (level.dat, regions)
- Successfully placed 3,177 blocks
- **Problem:** Chunks missing metadata BlueMap needs (heightmaps, lighting)
- **Result:** BlueMap sees 0 chunks to render

### Attempt 2: Load anvil World with Amulet
- Tried to fix anvil-parser world by re-saving with Amulet
- **Problem:** Amulet couldn't even load the world format
- **Result:** `LoaderNoneMatched` error

### Attempt 3: Create World with Amulet from Scratch
- Tried to instantiate `AnvilFormat` directly
- **Problem:** `AnvilFormat` is a **loader** not a **creator**
- **Result:** Requires existing world path

### Attempt 4: Various Hybrid Approaches
- Tried Construction format as intermediate
- Tried manual chunk initialization
- **Problem:** All require existing valid world or reimplementing world generator
- **Result:** Too complex, dead ends

## The Complications

### Technical Issues

1. **Chunk Format Requirements**
   ```
   What anvil-parser gives:   What BlueMap needs:
   ✓ Basic NBT structure      ✓ Basic NBT structure
   ✓ Block data               ✓ Block data
   ✓ Status: "full"           ✓ Status: "full"
   ✗ Heightmaps               ✓ MOTION_BLOCKING heightmap
   ✗ Proper lighting          ✓ Light data arrays
   ✗ Biome data               ✓ Biome palette
   ✗ Generation metadata      ✓ Generation stage info
   ```

2. **Coordinate System Confusion**
   - Initially used world coordinates (0-∞) instead of chunk-relative (0-15)
   - Fixed: `block_x = world_x % 16`
   - Blocks now place correctly, but still not recognized by BlueMap

3. **Library Misunderstandings**
   - **anvil-parser:** Reading/editing tool, not world creator
   - **Amulet:** World modifier, not world generator
   - Both assume existing valid Minecraft worlds

### Philosophical Issues

1. **Creating vs Modifying Worlds**
   - Libraries load/modify existing worlds
   - Creating from scratch = reimplementing Minecraft's generator
   - Missing documentation on exact format requirements

2. **Rendering Engine Expectations**
   - BlueMap designed for real Minecraft servers
   - Expects complete, player-generated chunks
   - Minimal chunks might crash or be ignored

## Why BlueMap Automation Still Works

The **screenshot automation is 100% functional:**
- ✅ BlueMap CLI launches
- ✅ Web server starts on port 8100
- ✅ Playwright controls browser
- ✅ Screenshot button automation works
- ✅ PNG download and save works

**The only issue:** The world is empty, so screenshot is black.

**Proof:** `test_screenshot.png` (20 KB, 1280x720) successfully captured.

## The Path Forward

### Option A: Use Matplotlib (Recommended ✅)
**Why:**
- Already working perfectly
- Fast (~1.5s per schematic)
- High quality multi-view renders
- Can batch process all 10,665 schematics today

**How:**
```bash
python scripts/render_schematics.py \
    --schematics-dir data/schematics \
    --output-dir data/screenshots \
    --mode showcase
```

### Option B: Complete BlueMap Setup
**Why:**
- Photo-realistic renders
- True 3D lighting
- Minecraft-accurate appearance

**What's Needed:**
1. **One-Time Setup:** 
   - Open Minecraft Java Edition
   - Create Superflat world
   - Save to `templates/minecraft_template/`
   - (5 minutes total)

2. **Per Schematic:**
   ```bash
   python scripts/amulet_schematic_to_world.py \
       data/schematics/10234.schematic \
       --template templates/minecraft_template
   ```

3. **Then BlueMap renders properly**

**Time Investment:**
- Setup: 5 minutes (one-time)
- Per schematic: ~5-10 seconds
- Full dataset: ~15-30 hours

### Option C: Hybrid Approach
1. Use matplotlib for quick dataset overview
2. Use BlueMap for hero images / publications
3. Best of both worlds

## My Recommendation

**Start with Matplotlib** because:
1. It's working now
2. You can iterate quickly
3. Can process full dataset today
4. Can always add BlueMap later for specific schematics

**Add BlueMap later if:**
1. You need publication-quality renders
2. You have Minecraft available
3. Time budget allows slower processing

## Key Files for You

1. **Read First:** `BLUEMAP_ATTEMPTS_REPORT.md` 
   - Complete technical analysis
   - All attempts documented
   - Lessons learned
   
2. **Archive:** `scripts/archive_failed_attempts/`
   - All non-working scripts moved here
   - Won't clutter your view
   - README explains each failure

3. **Use These:** 
   - `scripts/render_schematics.py` (ready for production)
   - `scripts/generate_previews.py` (fast 2D views)

## Questions for Your Plan

1. **Quality vs Speed:**
   - Matplotlib: High quality, 1.5s each = ~4.5 hours for 10k schematics
   - BlueMap: Photo quality, 10s each = ~30 hours for 10k schematics
   - Which matters more?

2. **Minecraft Access:**
   - Do you have Minecraft Java Edition?
   - If yes, BlueMap is viable
   - If no, matplotlib is the only option

3. **Use Case:**
   - Dataset overview → matplotlib perfect
   - Publication figures → might want BlueMap quality
   - Both → hybrid approach

4. **Storage:**
   - Matplotlib: ~600 KB per image = ~6 GB total
   - BlueMap: ~600 KB per image + ~50 MB per world = ~500 GB total
   - Do you have space for worlds?

