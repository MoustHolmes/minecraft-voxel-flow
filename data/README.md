# Data Directory

This directory contains datasets used for training and evaluation.

## Structure

```
data/
├── MNIST/           # MNIST dataset (auto-downloaded)
│   └── raw/        # Raw MNIST files
└── README.md       # This file
```

## Datasets

### MNIST

The MNIST dataset is automatically downloaded by the `MNISTDataModule` on first use. No manual setup required.

- **Classes**: 10 digit classes (0-9)
- **Training samples**: 60,000
- **Test samples**: 10,000
- **Image size**: 28x28 grayscale

### Moons (Synthetic)

The Moons dataset is generated on-the-fly using scikit-learn's `make_moons` function. No data files needed.

- **Classes**: 2 (two interleaving half circles)
- **Dimensions**: 2D points
- **Configurable**: Number of samples and noise level

## Adding Custom Datasets

To add a custom dataset:

1. **Create a DataModule** in `src/diffusion_playground/data/`:

```python
import lightning as L
from torch.utils.data import DataLoader, Dataset

class MyDataModule(L.LightningDataModule):
    def __init__(self, data_dir: str, batch_size: int = 32, **kwargs):
        super().__init__()
        self.save_hyperparameters()
    
    def prepare_data(self):
        # Download or prepare data here (runs once)
        pass
    
    def setup(self, stage: str = None):
        # Load data and create datasets (runs on each GPU)
        pass
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.hparams.batch_size)
    
    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.hparams.batch_size)
    
    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.hparams.batch_size)
```

2. **Create a config file** in `configs/data/`:

```yaml
# configs/data/my_data.yaml
_target_: diffusion_playground.data.my_datamodule.MyDataModule

data_dir: ${data_dir}
batch_size: 128
num_workers: 4
```

3. **Use it in training**:

```bash
python src/diffusion_playground/train.py data=my_data
```

## Data Organization

Place your raw data files in subdirectories:

```
data/
├── my_dataset/
│   ├── train/
│   ├── val/
│   └── test/
```

The `data_dir` path in configs will automatically point to this directory.
