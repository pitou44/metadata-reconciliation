#!/bin/bash
#SBATCH --partition=superChip
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00
#SBATCH -o main_%j.out
#SBATCH -e main_%j.err

echo "=== System Info ==="
hostname
uname -a
nvidia-smi || echo "nvidia-smi not found"
nvcc --version || echo "nvcc not found"

echo -e "\n=== Environment ==="
module load miniforge3/25.3.0-3
conda activate gh200-env

echo -e "\n=== Python/PyTorch Info ==="
python -c "
import sys
print(f'Python: {sys.version}')
print(f'Platform: {sys.platform}')

import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA compiled version: {torch.version.cuda}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA device count: {torch.cuda.device_count()}')

# Check if we can see GPUs at all
import subprocess
try:
    result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True)
    print(f'nvidia-smi -L: {result.stdout}')
except:
    print('Cannot run nvidia-smi')
"