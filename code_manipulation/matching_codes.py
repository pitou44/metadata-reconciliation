import os, json, re
from pathlib import Path
from datetime import datetime
from grabbing_codes import CodeExtractor
from prompt_maker import Matcher
import exifread


class Codes:
    def __init__(self):
        pass
        self.dng_files = []

    # def grab_dng_files(self, path):
    #     self.dng_files = []
    #     for f in path.glob('*.[Dd][Nn][Gg]'):
    #         with open(f, 'rb') as file:
    #             tags = exifread.process_file(file)
    #             date_taken = tags.get('EXIF DateTimeDigitized')
    #             if date_taken:
    #                 dt = datetime.strptime(str(date_taken), '%Y:%m:%d %H:%M:%S')
    #                 timestamp = dt.timestamp()
    #                 self.dng_files.append((f.name, timestamp))
    #
    #     self.dng_files.sort(key=lambda x: x[1])
    #     return self.dng_files
    def grab_dng_files(self, path):
        self.dng_files = sorted(path.glob('*.[Dd][Nn][Gg]'),
                                key=lambda f: int(f.stem.split('_')[-1]))
        return [(f.name, None) for f in self.dng_files]


class JsonManager:
    def __init__(self, tray_name="Tray_003"):
        self.image_descriptions = self.load_image_descriptions()

        self.image_combined = ""
        for key in self.image_descriptions[tray_name]:
            self.image_combined += f"IMAGE {key} with the following info -> {self.image_descriptions[tray_name][key]} \n"

    def load_image_descriptions(self):
        with open('../image_descriptions.json', 'r') as f:
            data = json.load(f)

        # Sort and process
        sorted_data = {}
        for key, value in data.items():
            processed_files = []
            for filename, description in value.items():
                # Remove the number prefix from filename
                # "203843_Tray_003_Anon_000103.dng" -> "Tray_003_Anon_000103.dng"
                new_filename = re.sub(r'^\d+_', '', filename)

                # Extract the last 6-digit number for sorting
                num = int(re.search(r'(\d{6})\.dng', new_filename).group(1))
                processed_files.append((num, new_filename, description))

            processed_files.sort()
            sorted_files = {filename: desc for _, filename, desc in processed_files}

            # Use the tray key itself, not the min_num which can collide
            sorted_data[key] = sorted_files

        return sorted_data


if __name__ == "__main__":
    # image descriptions
    slide_info = JsonManager(tray_name="Tray_032_Bellini_Bellotto")
    #image_descriptions = json.dumps(slide_info.image_descriptions)
    image_descriptions = slide_info.image_combined

    # codes
    code_manager = Codes()
    code_extractor = CodeExtractor()

    # get CORRECT dng codes
    files = code_manager.grab_dng_files(Path(r"E:\VRC - Artists\Tray_032_Bellini_Bellotto"))
    correct_codes = [f[0].split('_')[0] for f in files]

    # get result codes
    extracted = code_extractor.extract_codes()
    extracted = code_extractor.get_results("Tray_032_Bellini_Bellotto")
    fixed_codes = [r['fixed_code'] for r in extracted if r['is_valid']]

    additional_info = {}
    for code in fixed_codes:
        info = [r['context'] for r in extracted if r['fixed_code'] == code]
        additional_info[code] = info[0]

    print(additional_info)

    # result codes WITH their metadata
    codes_list = ""
    for i, code in enumerate(fixed_codes):
        codes_list += f"\n CODE {code_extractor.metadata.get_code_info(code)}"#. ADDITIONAL INFORMATION THAT GAVE THE CODE: '{additional_info[code]}'\n"

    # final prompt
    code_matcher = Matcher()
    code_matcher.send_prompt(codes_list, image_descriptions)

    #print(correct_codes)
    #print(fixed_codes)
