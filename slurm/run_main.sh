#!/bin/sh
#SBATCH -t 7:00:00
#SBATCH -p large-gpu              # or ultra-gpu for best GPUs
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH -o main_%j.out
#SBATCH -e main_%j.err
#SBATCH --mail-user=thomas.gailis@gwu.edu
#SBATCH --mail-type=all

module load anaconda/2023.03
module load cuda/12.4
cd /gpfs/automountdir/gpfs/homes/CCAS/home/g33490922/fws_images

export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

/CCAS/home/g33490922/.conda/envs/gh200-env/bin/python main.py