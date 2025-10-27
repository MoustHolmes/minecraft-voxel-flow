# Schematic Loading & Viewing Plan

## Overview
Goal: Load Minecraft schematic files and convert them to viewable/trainable 3D voxel data.

## Understanding Schematic Formats

### 1. **MCEdit Schematic (.schematic)** - Legacy Format
- **Format**: NBT (Named Binary Tag) structure
- **Compatibility**: Minecraft 1.12.2 and earlier
- **Structure**:
  - Width, Height, Length dimensions
  - Block IDs (numeric, e.g., 1 = Stone)
  - Block Data (metadata/variants)
  - Entities, TileEntities
- **Limitation**: Only 256 block types (numeric IDs)

### 2. **Sponge Schematic (.schem)** - Modern Format
- **Format**: NBT structure (newer spec)
- **Compatibility**: Minecraft 1.13+ (The Flattening)
- **Structure**:
  - Width, Height, Length dimensions
  - Block palette (string IDs, e.g., "minecraft:stone")
  - Block data array (indices into palette)
  - BlockEntities, Entities
- **Advantage**: Supports all modern blocks with namespaced IDs

### 3. **Litematica (.litematic)**
- **Format**: NBT structure (custom format)
- **Compatibility**: Modern Minecraft (client-side mod)
- **Structure**:
  - Multiple regions support
  - Metadata (author, description, time)
  - Schematic version info
- **Usage**: Popular for technical/building communities

## Main Plan: Python-Based Loading with NBT Libraries

### Phase 1: Load Schematic Files ✅ RECOMMENDED

**Libraries to Use:**
1. **amulet-core** (Already installed!) - Best option
   - Supports .schematic, .schem, .litematic, and world files
   - Handles version conversions automatically
   - Converts to universal block format
   - Active development, modern API

2. **mcschematic** (Alternative)
   - Simple API for .schem files
   - Good for modern schematics
   - Lightweight

3. **NBT** (Low-level)
   - Direct NBT parsing
   - More control but requires manual format handling

### Phase 2: Convert to Voxel Array

```python
# Using amulet-core (RECOMMENDED)
from amulet.api.block import Block
from amulet import load_level
import numpy as np

def load_schematic_amulet(filepath):
    """Load schematic and convert to 3D numpy array"""
    # Load the schematic
    level = load_level(filepath)
    
    # Get dimensions
    bounds = level.bounds(level.dimensions[0])
    
    # Extract blocks into 3D array
    blocks = []
    palette = {}
    
    for x in range(bounds.min_x, bounds.max_x):
        for y in range(bounds.min_y, bounds.max_y):
            for z in range(bounds.min_z, bounds.max_z):
                block = level.get_block(x, y, z, level.dimensions[0])
                # Map block to ID
                block_id = get_or_create_id(block, palette)
                blocks.append(block_id)
    
    # Reshape to 3D
    shape = (bounds.max_x - bounds.min_x,
             bounds.max_y - bounds.min_y, 
             bounds.max_z - bounds.min_z)
    voxel_array = np.array(blocks).reshape(shape)
    
    return voxel_array, palette
```

### Phase 3: Visualization Options

#### Option A: 3D Visualization with Plotly (Interactive)
```python
import plotly.graph_objects as go

def visualize_voxels_plotly(voxel_array, palette, max_blocks=10000):
    """Interactive 3D visualization"""
    # Sample if too large
    if voxel_array.size > max_blocks:
        voxel_array = downsample(voxel_array, max_blocks)
    
    # Get non-air block positions
    x, y, z = np.where(voxel_array > 0)
    
    # Create 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=2,
            color=voxel_array[x, y, z],
            colorscale='Viridis',
            showscale=True
        )
    )])
    
    fig.update_layout(scene=dict(aspectmode='data'))
    fig.show()
```

#### Option B: Slice Visualization (2D Cross-sections)
```python
import matplotlib.pyplot as plt

def visualize_slices(voxel_array, palette, num_slices=5):
    """Show 2D slices through the structure"""
    fig, axes = plt.subplots(1, num_slices, figsize=(15, 3))
    
    for i, ax in enumerate(axes):
        slice_idx = int(voxel_array.shape[1] * i / num_slices)
        ax.imshow(voxel_array[:, slice_idx, :], cmap='tab20')
        ax.set_title(f'Y={slice_idx}')
        ax.axis('off')
    
    plt.tight_layout()
    plt.show()
```

#### Option C: Voxel Rendering with PyVista
```python
import pyvista as pv

def visualize_voxels_pyvista(voxel_array):
    """High-quality 3D voxel rendering"""
    # Create structured grid
    grid = pv.ImageData()
    grid.dimensions = voxel_array.shape
    grid.point_data["values"] = voxel_array.flatten(order="F")
    
    # Threshold to remove air blocks
    thresholded = grid.threshold(0.5)
    
    # Plot
    plotter = pv.Plotter()
    plotter.add_mesh(thresholded, scalars="values", cmap="viridis")
    plotter.show()
```

### Phase 4: Save as Standard Format

```python
def save_as_numpy(voxel_array, palette, output_path):
    """Save as compressed numpy format"""
    np.savez_compressed(
        output_path,
        voxels=voxel_array,
        palette=palette,
        shape=voxel_array.shape
    )

def save_as_hdf5(voxel_array, palette, output_path):
    """Save as HDF5 (better for large files)"""
    import h5py
    with h5py.File(output_path, 'w') as f:
        f.create_dataset('voxels', data=voxel_array, compression='gzip')
        f.create_dataset('palette', data=json.dumps(palette))
```

## Alternative Plan 1: Use Existing Minecraft Viewers

### Option: MCEdit Unified / Amulet Editor
- **Pros**: 
  - Visual GUI, no coding needed
  - Handles all formats
  - Can export renders/screenshots
- **Cons**: 
  - Manual process
  - Not scriptable
  - Doesn't produce ML-ready data

### Implementation:
1. Download schematics via scraper
2. Open in Amulet Editor manually
3. Export as images/screenshots
4. Use images for training (2D approach)

## Alternative Plan 2: Convert to Mesh Format

### Using amulet-core to export
```python
def schematic_to_obj(schematic_path, output_obj):
    """Convert schematic to OBJ mesh"""
    level = load_level(schematic_path)
    
    # Export as OBJ
    # (amulet has export capabilities)
    # Then view in Blender, MeshLab, etc.
```

**Pros**: 
- Can use standard 3D tools (Blender, MeshLab)
- High-quality rendering
- Can create dataset of rendered images

**Cons**: 
- Loses voxel grid structure
- Not ideal for voxel-based ML

## Alternative Plan 3: Minecraft-Specific Python Tools

### Using minecraft-python libraries
```python
# pymclevel (older, for .schematic)
import pymclevel

def load_old_schematic(filepath):
    schematic = pymclevel.fromFile(filepath)
    return schematic.Blocks, schematic.Data

# For newer formats, stick with amulet
```

## Alternative Plan 4: Web-Based Viewer

### Three.js Minecraft Viewer
- Convert schematic to JSON
- Use three.js + minecraft-like rendering
- View in browser
- Export screenshots programmatically

```javascript
// Simplified concept
const viewer = new MinecraftViewer('canvas');
viewer.loadSchematic(schematicData);
viewer.render();
```

## Recommended Implementation Pipeline

### Step 1: Schematic Loader Module
```python
# minecraft_voxel_flow/loaders/schematic_loader.py

class SchematicLoader:
    def __init__(self):
        self.supported_formats = ['.schematic', '.schem', '.litematic']
    
    def load(self, filepath):
        """Load any schematic format"""
        ext = Path(filepath).suffix
        
        if ext == '.schematic':
            return self._load_legacy(filepath)
        elif ext == '.schem':
            return self._load_sponge(filepath)
        elif ext == '.litematic':
            return self._load_litematica(filepath)
    
    def to_voxel_array(self, schematic):
        """Convert to numpy array"""
        pass
    
    def get_block_palette(self, schematic):
        """Extract unique blocks"""
        pass
```

### Step 2: Voxel Processor
```python
# minecraft_voxel_flow/processors/voxel_processor.py

class VoxelProcessor:
    def normalize_dimensions(self, voxel_array, target_size=(64, 64, 64)):
        """Resize/pad to standard dimensions"""
        pass
    
    def remove_air(self, voxel_array):
        """Remove empty space"""
        pass
    
    def encode_blocks(self, voxel_array, palette):
        """Encode blocks as integers for ML"""
        pass
    
    def split_into_patches(self, voxel_array, patch_size=16):
        """Split large structures into smaller patches"""
        pass
```

### Step 3: Dataset Builder
```python
# minecraft_voxel_flow/data/schematic_dataset.py

class SchematicDataset:
    def __init__(self, schematic_dir, transform=None):
        self.schematics = self.scan_directory(schematic_dir)
        self.transform = transform
    
    def __getitem__(self, idx):
        schematic_path = self.schematics[idx]
        voxels = self.load_and_process(schematic_path)
        
        if self.transform:
            voxels = self.transform(voxels)
        
        return voxels
    
    def __len__(self):
        return len(self.schematics)
```

### Step 4: Visualization Suite
```python
# minecraft_voxel_flow/visualization/viewers.py

class SchematicViewer:
    def __init__(self, backend='plotly'):
        self.backend = backend
    
    def view_3d(self, voxel_array):
        """Interactive 3D view"""
        pass
    
    def view_slices(self, voxel_array):
        """2D slice view"""
        pass
    
    def save_render(self, voxel_array, output_path):
        """Save as image"""
        pass
```

## Testing Strategy

### Test Cases:
1. **Small schematic** (< 32^3 blocks)
   - Test: Castle tower, small house
   - Verify: Correct dimensions, block types

2. **Medium schematic** (32^3 to 128^3 blocks)
   - Test: Large house, ship
   - Verify: Performance, memory usage

3. **Large schematic** (> 128^3 blocks)
   - Test: City section, massive castle
   - Verify: Chunking, streaming

4. **Different formats**
   - Test: .schematic, .schem, .litematic
   - Verify: Format detection, parsing

5. **Edge cases**
   - Empty schematics
   - Air-only regions
   - Complex block states (stairs, doors)

## Performance Considerations

### Memory Management
- Large schematics can be 100MB+ in memory
- Use chunking for structures > 256^3
- Consider sparse array representation for structures with lots of air

### Optimization Strategies
1. **Lazy loading**: Load schematic metadata first, blocks on demand
2. **Caching**: Cache processed voxel arrays
3. **Downsampling**: Reduce resolution for preview/training
4. **Block simplification**: Group similar blocks (all stone variants → stone)

## Dependencies

```bash
# Core
pip install amulet-core amulet-nbt

# Visualization
pip install plotly pyvista matplotlib

# Data handling
pip install numpy h5py

# Optional
pip install pymclevel  # For legacy support
pip install mcschematic  # Alternative loader
```

## Next Steps

1. **Prototype** with amulet-core on a few test schematics
2. **Evaluate** loading time and memory usage
3. **Build** basic visualization (plotly or matplotlib)
4. **Create** standardized voxel format for the dataset
5. **Implement** batch processing for scraped schematics
6. **Integrate** with ML pipeline

## Questions to Answer

1. **Target dimensions**: What's our standard voxel grid size? (64^3, 128^3?)
2. **Block encoding**: How many unique blocks to support? (All blocks? Simplified palette?)
3. **Augmentation**: Do we need rotations, flips for training?
4. **Storage format**: .npz, .h5, or custom format?
5. **Visualization priority**: Interactive 3D or fast 2D slices?

## Success Metrics

- ✅ Load 95%+ of downloaded schematics
- ✅ Process schematic in < 5 seconds
- ✅ Visualize in < 2 seconds
- ✅ Handle structures up to 512^3 blocks
- ✅ Support all 3 major formats
