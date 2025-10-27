# Failed BlueMap World Generation Attempts

This directory contains scripts that attempted to create Minecraft worlds from schematics for BlueMap rendering.

## Why These Failed

**Core Issue:** Creating a valid Minecraft world from scratch requires extensive metadata that rendering engines (like BlueMap) expect, but programmatic world creation libraries don't provide.

## Archived Scripts

### 1. `build_minecraft_world.py`
**Approach:** Use anvil-parser's `EmptyChunk` to create world directly  
**Status:** ❌ Blocks placed successfully (3,177), but BlueMap doesn't recognize chunks  
**Why Failed:** `EmptyChunk` creates minimal NBT data; missing heightmaps, proper lighting, and generation metadata

### 2. `schematic_to_minecraft_world.py`  
**Approach:** Early iteration of anvil-parser approach  
**Status:** ❌ Similar issues to build_minecraft_world.py  
**Why Failed:** Same root cause - anvil-parser not designed for world creation

### 3. `schematic_to_bluemap_world.py`
**Approach:** Attempt to use Amulet to create world from scratch  
**Status:** ❌ Amulet's AnvilFormat requires existing world  
**Why Failed:** `AnvilFormat.__init__(path)` is a loader, not a creator

### 4. `fix_world_for_bluemap.py`
**Approach:** Load anvil-generated world with Amulet to add metadata  
**Status:** ❌ `LoaderNoneMatched` error  
**Why Failed:** Amulet couldn't even recognize the anvil-parser world format

### 5. `create_world_properly.py`
**Approach:** Attempted various Amulet world creation methods  
**Status:** ❌ Incomplete, dead-end approaches  
**Why Failed:** Realized all paths require existing Minecraft world

## What We Learned

1. **anvil-parser** is for reading/light editing, NOT world creation
2. **Amulet** excels at modifying existing worlds, NOT creating new ones
3. **BlueMap** expects complete chunk metadata that's hard to generate programmatically
4. Creating worlds from scratch = reimplementing Minecraft's world generator

## What Actually Works

### Option A: Matplotlib Rendering ✅
- Located in: `scripts/render_schematics.py`
- Status: Fully working
- Speed: ~1.5s per schematic
- Quality: High quality multi-view renders
- Successfully generated 3 test renders

### Option B: BlueMap with Template World ⏸️
- Script: `scripts/amulet_schematic_to_world.py`
- Status: Ready to test (needs Minecraft template)
- Process:
  1. Create superflat world in Minecraft once
  2. Copy to `templates/minecraft_template/`
  3. Use Amulet to paste schematics into copies
  4. BlueMap renders the modified worlds
- Would provide photo-realistic renders

## Technical Details

See `BLUEMAP_ATTEMPTS_REPORT.md` in project root for complete technical analysis including:
- Detailed failure explanations
- NBT structure requirements
- Coordinate system issues solved
- Lessons learned
- Recommendations

## Do Not Use These Scripts

They are kept for reference only. Use:
- `scripts/render_schematics.py` for production rendering
- `scripts/amulet_schematic_to_world.py` if you have Minecraft and want BlueMap quality
