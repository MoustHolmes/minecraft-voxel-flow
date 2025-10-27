# Minecraft Voxel Flow Matching

Flow Matching for Minecraft voxel structure generation

## Overview

A minimal, production-ready PyTorch Lightning template for training **Flow Matching** models. Features include:

- 🎯 **Flow Matching & Classifier-Free Guidance**: State-of-the-art generative modeling
- 🔧 **Modular Design**: Easy-to-swap components (models, networks, schedulers, samplers, solvers)
- ⚙️ **Hydra Configuration**: Clean, composable configs for reproducible experiments  
- 📊 **Experiment Tracking**: Built-in Weights & Biases integration
- ✅ **Production Ready**: Type hints, comprehensive tests, and documentation
- 🚀 **Quick Start**: Train on MNIST or 2D toy datasets out of the box

## What is Flow Matching?

Flow Matching is a simulation-free approach to training continuous normalizing flows. Key advantages:

- **Simple Training**: No need for ODE solvers during training
- **Fast Sampling**: Direct path from noise to data
- **Flexible**: Works with any neural network architecture
- **Stable**: More stable training than diffusion models

## Getting Started

### Installation

1. Create and activate a conda environment:
```bash
conda create -n minecraft_voxel_flow python=3.11
conda activate minecraft_voxel_flow
```

2. Install the package:
```bash
pip install -e .  # Basic installation
pip install -e ".[dev]"  # With development dependencies
```

3. Initialize pre-commit hooks (optional):
```bash
pre-commit install
```

### Quick Training Examples

Train on MNIST (default):
```bash
python src/minecraft_voxel_flow/train.py
```

Quick test with debug mode (1 batch only):
```bash
python src/minecraft_voxel_flow/train.py experiment=debug
```

Train on 2D Moons dataset:
```bash
python src/minecraft_voxel_flow/train.py experiment=moons
```

Override any config parameter:
```bash
python src/minecraft_voxel_flow/train.py \
    data.batch_size=64 \
    model.optimizer.lr=0.0001 \
    trainer.max_epochs=20
```

## Project Structure

```
├── configs/                    # Hydra configuration files
│   ├── train_config.yaml      # Main training config
│   ├── paths_config.yaml      # Path configurations
│   ├── data/                  # Data module configs
│   ├── model/                 # Model configs
│   ├── trainer/               # PyTorch Lightning trainer configs
│   ├── callbacks/             # Callback configs
│   ├── logger/                # Logger configs
│   └── experiment/            # Full experiment configs
├── src/minecraft_voxel_flow/
│   ├── train.py               # Main training script
│   ├── models/                # LightningModules (training logic)
│   │   └── flow_matching.py  # FlowMatching & FlowMatchingCFG
│   ├── networks/              # Neural network architectures
│   │   ├── unet.py           # U-Net for images
│   │   └── mlp.py            # MLP for 2D data
│   ├── modules/               # Reusable building blocks
│   │   ├── schedulers.py     # Alpha/beta schedulers
│   │   ├── samplers.py       # Noise samplers
│   │   └── solvers.py        # ODE solvers
│   ├── data/                  # Data modules
│   ├── callbacks/             # Custom callbacks
│   └── util/                  # Utilities
├── tests/                     # Unit tests
├── data/                      # Data directory
└── outputs/                   # Training outputs (logs, checkpoints)
```

## Features

### Flow Matching Models

**Standard Flow Matching**:
```python
from minecraft_voxel_flow.models import FlowMatching

model = FlowMatching(
    model=unet,
    alpha_beta_scheduler=scheduler,
    sampler=sampler,
    ode_solver=solver,
)
```

**Classifier-Free Guidance**:
```python
from minecraft_voxel_flow.models import FlowMatchingCFG

model = FlowMatchingCFG(
    model=unet,
    num_classes=10,
    cfg_prob=0.1,        # 10% unconditional training
    guidance_scale=3.0,  # Guidance strength
)

# Generate with stronger guidance
samples = model.generate_samples(labels, guidance_scale=5.0)
```

### Modular Components

- **Models**: LightningModules for training (FlowMatching, FlowMatchingCFG)
- **Networks**: U-Net for images, MLP for low-dimensional data
- **Modules**: Schedulers (Linear, Cosine, Stable), Samplers (Gaussian), Solvers (Euler, RK4)

## Configuration System

All hyperparameters are managed through Hydra configs:

```yaml
# configs/experiment/my_experiment.yaml
defaults:
  - override /model: default_model
  - override /data: default_data_module

task_name: "my_experiment"

model:
  optimizer:
    lr: 0.001

data:
  batch_size: 128

trainer:
  max_epochs: 10
```

## Development

### Schematic Rendering Pipeline

This project includes a complete pipeline for rendering Minecraft schematics to 2D images using Chunky:

#### Quick Start

Render a schematic with default settings:
```bash
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output render.png \
    --spp 100
```

#### Camera Angle System

Control the camera viewpoint with four parameters:

- `--camera-angle`: Horizontal angle (0-360°, default: 225°)
- `--camera-distance`: Distance from schematic (default: 42 blocks)
- `--camera-elevation`: Height above center (default: 15 blocks)
- `--camera-pitch`: Vertical tilt (default: -20°)

**Examples:**

```bash
# View from North
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output north_view.png \
    --camera-angle 270 \
    --spp 100

# Top-down view
python scripts/paste_schematic_to_real_world.py \
    data/schematics/10234.schematic \
    --world data/world_test_file/void \
    --output top_down.png \
    --camera-angle 45 \
    --camera-elevation 50 \
    --camera-pitch -60 \
    --spp 100

# Generate 360° turnaround (8 angles)
for angle in 0 45 90 135 180 225 270 315; do
    python scripts/paste_schematic_to_real_world.py \
        data/schematics/10234.schematic \
        --world data/world_test_file/void \
        --output "renders/angle_${angle}.png" \
        --camera-angle $angle \
        --spp 100
done
```

**Documentation:**
- [Camera Angle System Guide](docs/CAMERA_ANGLE_SYSTEM.md) - Detailed usage and examples
- [Angle Bug Post-Mortem](docs/ANGLE_BUG_POSTMORTEM.md) - Technical deep-dive on camera system bugs and fixes
- [Screenshot Generation](docs/SCREENSHOT_GENERATION.md) - Overview of the rendering pipeline

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/minecraft_voxel_flow

# Run specific test file
pytest tests/test_config.py -v
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/
```

## Extending the Template

### Adding a Custom Dataset

1. Create `src/minecraft_voxel_flow/data/my_data.py`
2. Inherit from `L.LightningDataModule`
3. Create config in `configs/data/my_data.yaml`
4. Use with: `python train.py data=my_data`

See `data/README.md` for detailed instructions.

### Adding a Custom Model

1. Create your model in `src/minecraft_voxel_flow/networks/`
2. Create config in `configs/model/my_model.yaml`
3. Use with: `python train.py model=my_model`

## Citation

If you use this code in your research, please cite:

```bibtex
@software{ minecraft_voxel_flow,
  author = { Moust Holmes },
  title = { Minecraft Voxel Flow Matching: A PyTorch Lightning Template for Flow Matching},
  year = {2025},
}
```

## License

MIT License - see LICENSE file for details.

## Author

Moust Holmes
