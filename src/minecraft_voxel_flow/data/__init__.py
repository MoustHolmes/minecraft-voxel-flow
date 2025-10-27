"""Data modules for diffusion playground."""

from minecraft_voxel_flow.data.MNIST_datamodule import MNISTDataModule
from minecraft_voxel_flow.data.moons_datamodule import MoonsDataModule

__all__ = [
    "MNISTDataModule",
    "MoonsDataModule",
]
