#!/bin/bash
#SBATCH --partition=superChip
#SBATCH --cpus-per-task=16
#SBATCH --time=00:20:00
#SBATCH --job-name=setup_gh200_env
#SBATCH --output=setup_env_%j.out
#SBATCH --error=setup_env_%j.err

echo "Starting environment setup on $(hostname)"
echo "Date: $(date)"

# Load miniforge
module load miniforge3/25.3.0-3

# Remove old environment if it exists
echo "Removing old gh200-env if it exists..."
conda env remove -n gh200-env -y || echo "No existing environment to remove"

# Create new environment
echo "Creating new gh200-env environment..."
conda create -n gh200-env python=3.10 -y

# Activate environment
echo "Activating environment..."
conda activate gh200-env

# Install packages
echo "Installing PyTorch with CUDA..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124 --python-version 311 --only-binary=:all: --target gh200-2025-02-18-3/lib64/python3.11/site-packages/

echo "Installing other packages..."
pip install pdf2image
pip install transformers==4.51.3 numpy==1.25.0 pillow==10.3.0 moviepy==1.0.3
pip install opencv-python pandas

# Test CUDA availability
echo "Testing CUDA availability..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

echo "Environment setup complete!"
echo "Date: $(date)"