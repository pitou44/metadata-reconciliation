# pip install pysbatch
from pysbatch import Slurm

options = {
    'job-name': "OCR_images",
    'output': "pysbatch-%j.out",
    'error': "pysbatch-%j.err",
    'time': "01:00:00",
    'partition': "your_partition",
    'cpus-per-task': 4,
    'mem': "16G",
}

commands = [
    'python my_script.py'
]

job = Slurm(
    script=commands,
    options=options
)

job_id = job.submit()
print(f"Submitted batch job {job_id}")
