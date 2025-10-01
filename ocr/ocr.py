# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# pip install transformers==4.51.3 numpy==1.25.0 pillow==10.3.0 moviepy==1.0.3
# pip install -U "huggingface_hub[cli]"
# hf download AIDC-AI/Ovis2.5-9B

import torch
import requests
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

import time, re

MODEL_PATH = "models/AIDC-AI/Ovis2.5-9B"


class OCR:
    def __init__(self):
        self.enable_thinking = True
        self.enable_thinking_budget = True  # Only effective if enable_thinking is True.

        # Total tokens for thinking + answer. Ensure: max_new_tokens > thinking_budget + 25
        self.max_new_tokens = 3072
        self.thinking_budget = 2048

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            use_fast=True,
            trust_remote_code=True,
        )

        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,  # Reduces memory from ~16GB to ~8GB
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            #quantization_config=quantization_config
        ).cuda()

        if hasattr(self.model, 'text_tokenizer'):
            print("setting tokenizer")
            self.model.text_tokenizer = self.tokenizer

    def generate_ocr(self, image_path):
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": Image.open(image_path)},
                {"type": "text",
                 "text": "perform OCR on the image. Return ONLY the extracted text. do NOT give additional information."},
            ],
        }]

        prev_time = time.time()

        input_ids, pixel_values, grid_thws = self.model.preprocess_inputs(
            messages=messages,
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking,
        )
        input_ids = input_ids.cuda()
        pixel_values = pixel_values.cuda() if pixel_values is not None else None
        grid_thws = grid_thws.cuda() if grid_thws is not None else None

        outputs = self.model.generate(
            inputs=input_ids,
            pixel_values=pixel_values,
            grid_thws=grid_thws,
            enable_thinking=self.enable_thinking,
            enable_thinking_budget=self.enable_thinking_budget,
            max_new_tokens=self.max_new_tokens,
            thinking_budget=self.thinking_budget,
        )

        print(f"Generation took {time.time() - prev_time} seconds")

        response = self.model.text_tokenizer.decode(outputs[0], skip_special_tokens=True)

        result = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        print(result)

        return result
