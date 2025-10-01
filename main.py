#from load_metadata import Metadata
from ocr.pdf_splitter import PDFSplitter
from ocr.ocr import OCR
import json

import glob
import os, time, sys

#metadata = Metadata()
pdf = PDFSplitter()
ocr = OCR()

# Test multiple path variations
paths = [
    "/CCAS/home/g33490922/fws_images/ocr/images_tmp/page_1/tile_0_0.png",
    "/gpfs/automountdir/gpfs/homes/CCAS/home/g33490922/fws_images/ocr/images_tmp/page_1/tile_0_0.png",
    "ocr/images_tmp/page_1/tile_0_0.png"
]

# main part
pdf_name = "Tray_004"

pdf.pdf_to_text(f'pdf_files/{pdf_name}.pdf')

directory = "/CCAS/home/g33490922/fws_images/ocr/images_tmp/"
ocr_results = {}

time_taken = time.time()

all_pages = glob.glob(os.path.join(directory, '**'))
for file in all_pages:
    page = os.path.basename(os.path.normpath(file))
    page_num = int(page.split('_')[1])

    for row in range(5):
        for col in range(4):
            tile = f"{row}_{col}"
            result = ocr.generate_ocr(f"{directory}page_{page_num}/tile_{tile}.png")

            ocr_results.setdefault(pdf_name, {}).setdefault(page_num, {})[tile] = result

json.dump(ocr_results, open('results.json', 'w'), indent=2)
json.dump({"time_taken": time.time() - time_taken}, open('time.json', 'w'), indent=2)
print(ocr_results)
exit()
