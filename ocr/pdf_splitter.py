# pip install pytesseract pdf2image Pillow opencv-python numpy

# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# Poppler: https://github.com/oschwartz10612/poppler-windows

#import pytesseract
from pdf2image import convert_from_path
#import pytesseract
#import pdfplumber
#from PIL import Image
import cv2, os
import shutil

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# amazing fucking model: https://huggingface.co/nanonets/Nanonets-OCR-s
# find new models: https://huggingface.co/spaces/prithivMLmods/Multimodal-OCR

# pip install torch==2.4.0 transformers==4.51.3 numpy==1.25.0 pillow==10.3.0 moviepy==1.0.3
# pip install flash-attn==2.7.0.post2 --no-build-isolation
# Ovis2.5-9B seems like the best choice https://huggingface.co/spaces/davanstrien/ocr-time-machine


class PDFSplitter:
    def __init__(self):
        self.tmp_folder = os.getcwd() + "/ocr/images_tmp"

        os.makedirs(self.tmp_folder, exist_ok=True)

        self.page_count = None

    def slice_pdf_to_images(self, pdf_path):
        print(os.getcwd())
        poppler_paths = os.getcwd() + "/ocr/poppler-25.07.0/Library/bin"
        pages = convert_from_path(pdf_path, dpi=500, poppler_path=poppler_paths)

        self.page_count = len(pages)

        # Clear tmp_folder
        shutil.rmtree(self.tmp_folder)
        os.makedirs(self.tmp_folder)

        grid_rows = 5
        grid_cols = 4

        #self.first_character_location(pdf_path, current_page=1)

        for page_num, page in enumerate(pages):
            if 0 < page_num:
                width, height = page.size

                # 942 x 1219
                # w 36 -> 904
                # h 34 -> 1169

                tile_width_max = width# * 0.922
                tile_height_max = height# * 0.912

                tile_width = tile_width_max // grid_cols
                tile_height = tile_height_max // grid_rows

                p_x = 0#width // 26.16
                p_y = 0#height // 35.85

                page_dir = f'{self.tmp_folder}/page_{page_num}'
                os.makedirs(page_dir, exist_ok=True)

                for row in range(grid_rows):
                    for col in range(grid_cols):
                        box = (
                            int(p_x + col * tile_width),
                            int(p_y + row * tile_height),
                            int(p_x + (col + 1) * tile_width),
                            int(p_y + (row + 1) * tile_height)
                        )

                        tile = page.crop(box)
                        tile_path = f'{page_dir}/tile_{row}_{col}.png'

                        tile.save(tile_path)
                        print(f"Saved: {tile_path}")

    def pdf_to_text(self, pdf_path):
        self.slice_pdf_to_images(pdf_path)
