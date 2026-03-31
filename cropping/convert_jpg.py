import os
from pathlib import Path
import rawpy
import imageio

SOURCE_FOLDER = "original"
DEST_FOLDER = "jpgs"
QUALITY = 95  # JPEG quality (1-100)

source_path = Path(SOURCE_FOLDER)
dest_path = Path(DEST_FOLDER)

dest_path.mkdir(parents=True, exist_ok=True)

dng_files = list(source_path.glob("*.dng")) + list(source_path.glob("*.DNG"))

print(f"Found {len(dng_files)} DNG file(s)")

for dng_file in dng_files:
    jpg_path = dest_path / (dng_file.stem + ".jpg")

    print(f"Converting: {dng_file.name}")

    with rawpy.imread(str(dng_file)) as raw:
        rgb = raw.postprocess(use_camera_wb=True)

    imageio.imwrite(str(jpg_path), rgb, quality=QUALITY)

print("Done!")