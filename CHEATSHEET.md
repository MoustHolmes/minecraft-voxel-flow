# Quick Reference Cheat Sheet

## Common Commands

### Training Models

```bash
# Train on MNIST (default)
python src/minecraft_voxel_flow/train.py

# Train on 2D Moons dataset
python src/minecraft_voxel_flow/train.py experiment=moons

# Debug mode (1 batch only)
python src/minecraft_voxel_flow/train.py experiment=debug

# Custom hyperparameters
python src/minecraft_voxel_flow/train.py \
    data.batch_size=64 \
    model.optimizer.lr=0.0001 \
    trainer.max_epochs=20
```

### Rendering Schematics

```bash
# Basic render (default 225° angle)
python scripts/paste_schematic_to_real_world.py \
    data/schematics/YOUR_SCHEMATIC.schematic \
    --world data/world_test_file/void \
    --output render.png \
    --spp 100

# Specific angle (0-360°)
python scripts/paste_schematic_to_real_world.py \
    data/schematics/YOUR_SCHEMATIC.schematic \
    --world data/world_test_file/void \
    --output render.png \
    --camera-angle 90 \
    --spp 100

# Top-down view
python scripts/paste_schematic_to_real_world.py \
    data/schematics/YOUR_SCHEMATIC.schematic \
    --world data/world_test_file/void \
    --output top_down.png \
    --camera-angle 45 \
    --camera-elevation 50 \
    --camera-pitch -60 \
    --spp 100

# High quality (more samples)
python scripts/paste_schematic_to_real_world.py \
    data/schematics/YOUR_SCHEMATIC.schematic \
    --world data/world_test_file/void \
    --output high_quality.png \
    --spp 500
```

### Batch Rendering (Multiple Angles)

```bash
# 8 angles (360° turnaround)
for angle in 0 45 90 135 180 225 270 315; do
    python scripts/paste_schematic_to_real_world.py \
        data/schematics/YOUR_SCHEMATIC.schematic \
        --world data/world_test_file/void \
        --output "renders/angle_${angle}.png" \
        --camera-angle $angle \
        --spp 100
done

# 4 cardinal directions
for angle in 0 90 180 270; do
    python scripts/paste_schematic_to_real_world.py \
        data/schematics/YOUR_SCHEMATIC.schematic \
        --world data/world_test_file/void \
        --output "renders/cardinal_${angle}.png" \
        --camera-angle $angle \
        --spp 100
done
```

## Camera Parameters

| Parameter | Default | Description | Example Values |
|-----------|---------|-------------|----------------|
| `--camera-angle` | 225° | Horizontal angle around schematic | 0°=East, 90°=South, 180°=West, 270°=North |
| `--camera-distance` | 42 | Distance from center (blocks) | 20=close, 60=far |
| `--camera-elevation` | 15 | Height above center (blocks) | -10=below, 50=high above |
| `--camera-pitch` | -20° | Vertical tilt | -60°=looking down, 0°=horizontal, 30°=looking up |
| `--spp` | 100 | Samples per pixel (quality) | 50=fast, 200=good, 500+=excellent |

## Angle Reference

```
        270° (North)
            ↑
            |
180° ← CENTER → 0° (East)
    (West)  |
            ↓
         90° (South)
```

## File Locations

### Input Files
- Schematics: `data/schematics/*.schematic`
- World template: `data/world_test_file/void/`

### Output Files
- Renders: Specify with `--output` flag
- Logs: `outputs/` (training) or console (rendering)

### Configuration
- Training configs: `configs/`
- Chunky scenes: `~/.chunky/scenes/schematic_render/`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/minecraft_voxel_flow

# Run specific test
pytest tests/test_model.py -v
```

## Git Commands

```bash
# Check status
git status

# Add and commit changes
git add .
git commit -m "Your message here"

# Push to GitHub
git push origin main

# View history
git log --oneline

# View diff
git diff
```

## Troubleshooting

### Render Issues

**Problem**: "Snapshots directory doesn't exist"  
**Solution**: Run one successful render first to create the directory

**Problem**: Schematic not visible in frame  
**Solution**: Adjust `--camera-distance` (try 60-100 for larger structures)

**Problem**: Renders too dark  
**Solution**: Increase `--spp` for better quality/brightness

**Problem**: Different angles look identical  
**Solution**: Check file modification times. Should be recent and different:
```bash
ls -lh ~/.chunky/scenes/schematic_render/snapshots/
```

### Training Issues

**Problem**: CUDA out of memory  
**Solution**: Reduce `data.batch_size` or use smaller model

**Problem**: Training too slow  
**Solution**: Reduce `trainer.max_epochs` or use `experiment=debug`

**Problem**: Config errors  
**Solution**: Check YAML syntax in `configs/`

## Environment Setup

```bash
# Create conda environment
conda create -n minecraft_voxel_flow python=3.11
conda activate minecraft_voxel_flow

# Install package
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Quick Links

- [Full Documentation](README.md)
- [Camera System Guide](docs/CAMERA_ANGLE_SYSTEM.md)
- [Bug Post-Mortem](docs/ANGLE_BUG_POSTMORTEM.md)
- [Project Summary](PROJECT_SUMMARY.md)
- [GitHub Setup](GITHUB_SETUP.md)

## Common Workflows

### Generate Training Data
```bash
# 1. Download/place schematics in data/schematics/
# 2. Render from multiple angles
for angle in 0 45 90 135 180 225 270 315; do
    python scripts/paste_schematic_to_real_world.py \
        data/schematics/building.schematic \
        --world data/world_test_file/void \
        --output "training_data/building_${angle}.png" \
        --camera-angle $angle \
        --spp 100
done
# 3. Train model on generated images
```

### Experiment Iteration
```bash
# 1. Modify config
vim configs/experiment/my_experiment.yaml

# 2. Train
python src/minecraft_voxel_flow/train.py experiment=my_experiment

# 3. Check results in wandb or outputs/
```

### Code Changes
```bash
# 1. Make changes
# 2. Test
pytest tests/test_model.py

# 3. Commit
git add .
git commit -m "Description of changes"

# 4. Push
git push
```
