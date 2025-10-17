import json, time, torch
import os
from pathlib import Path
from PIL import Image
import rawpy
import tempfile
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

# Setup model and processor
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct", torch_dtype="auto", device_map="auto"
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")


def process_dng(dng_path, max_size_mb=1.3):
    """Convert DNG to temporary JPEG and return path, downscaling if needed"""
    with rawpy.imread(str(dng_path)) as raw:
        rgb = raw.postprocess()

    img = Image.fromarray(rgb)
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)

    # Start with quality 95 and original size
    quality = 95
    max_dimension = max(img.size)

    while True:
        # Save to temp file to check size
        img_resized = img
        if max_dimension < max(img.size):
            img_resized = img.copy()
            img_resized.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        img_resized.save(temp_file.name, 'JPEG', quality=quality)

        # Check file size
        file_size_mb = os.path.getsize(temp_file.name) / (1024 * 1024)
        print(file_size_mb)

        if file_size_mb <= max_size_mb:
            break

        # Reduce size by decreasing dimensions or quality
        if max_dimension > 2048:
            max_dimension = int(max_dimension * 0.8)
        elif quality > 70:
            quality -= 5
        else:
            # If we've reduced both significantly, just accept it
            break

    return temp_file.name


def describe_image(image_path):
    """Get description from model"""
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": image_path},
            {"type": "text",
             "text": "Return everything unique to this art piece you can. That includes the style, buildings, info, potential artist, time period and MUCH more. Only return useful information, that could be used as metadata for this image. Be concise, dont do a bullet point bullshit list, lust have a paragraph with all the info"}
        ]
    }]

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, padding=True, return_tensors="pt").to("cuda")

    with torch.no_grad():  # Disable gradient computation to save memory
        generated_ids = model.generate(**inputs, max_new_tokens=256)

    output_ids = generated_ids[0][len(inputs.input_ids[0]):]
    result = processor.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)

    # Delete tensors explicitly
    del inputs, generated_ids, output_ids
    torch.cuda.empty_cache()

    return result


prev_time = time.time()

# Process directory
dirr = "Tray_001"

directory = Path(f"{dirr}/.")  # Change to your directory
results = {}

for dng_file in directory.glob("*.dng"):
    print(f"Processing {dng_file.name}...")
    key = dng_file.name  #"_".join(dng_file.stem.split("_")[1:])

    temp_jpg = process_dng(dng_file)
    try:
        results.setdefault(dirr, {})[key] = describe_image(temp_jpg)
    finally:
        os.unlink(temp_jpg)

# Save results
with open("image_descriptions.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Processed {len(results)} images. Results saved to image_descriptions.json")
print(f"this took {time.time() - prev_time} seconds")
