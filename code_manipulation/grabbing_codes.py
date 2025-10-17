import re
import json, random
from difflib import get_close_matches
from load_metadata import Metadata


class CodeExtractor:
    def __init__(self):
        self.metadata = Metadata()
        self.valid_codes = [str(int(str(key).split('.')[0])) for key in
                            self.metadata.data.keys()]  # random.sample(list(metadata.data.keys()), 1000)

        self.results = None

        with open("../results2.json", "r") as f:
            self.data = json.load(f)

    def extract_codes(self):
        # Pattern to find potential codes (6+ digits with optional dashes/spaces)
        code_pattern = r'\d{2,4}[-\s.]?\d{3,6}\b'

        results = []
        valid_set = set(self.valid_codes)

        def try_fix_code(raw_code):
            digits_only = re.sub(r'[-\s/\n\r.]', '', raw_code)

            # Filter out codes that are too short
            if len(digits_only) < 5:
                return None, "too_short"

            # Filter out date patterns (4 digits - 4 digits)
            if re.match(r'^\d{4}-\d{4}$', raw_code):
                return None, "date_pattern"

            if len(digits_only) == 8 and digits_only.startswith(('12', '13', '14', '15', '16', '17', '18', '19', '20')):  # 8 digits starting with 19 or 20
                return None, "date_pattern"

            # Try exact match first
            if digits_only in valid_set:
                return digits_only, "exact_match"

            # Try removing ONE digit first
            if len(digits_only) > 5:  # Only if we have more than 5 digits
                # Try removing one digit from start
                truncated = digits_only[1:]
                if truncated in valid_set:
                    return truncated, "removed_1_from_start"

            # Try fixing first digit OCR error by replacing with 9 or 2
            if len(digits_only) >= 1:
                original_first = digits_only[0]

                # Try replacing first digit with 9
                if original_first != '9':
                    candidate = '9' + digits_only[1:]
                    if candidate in valid_set:
                        return candidate, f"fixed_first_digit_from_{original_first}_to_9"

                # Try replacing first digit with 2
                if original_first != '2':
                    candidate = '2' + digits_only[1:]
                    if candidate in valid_set:
                        return candidate, f"fixed_first_digit_from_{original_first}_to_2"

            # Try fixing second digit OCR error if first digit is 9
            if len(digits_only) >= 2 and digits_only[0] == '9':
                for replacement_digit in range(1, 9):  # Try digits 1-8
                    candidate = '9' + str(replacement_digit) + digits_only[2:]
                    if candidate in valid_set:
                        return candidate, f"fixed_second_digit_to_{replacement_digit}"

            # Try removing digits from start
            for i in range(1, min(4, len(digits_only) - 4)):  # Remove 1-2 digits, keep at least 5
                truncated = digits_only[i:]
                if truncated in valid_set:
                    return truncated, f"removed_{i}_from_start"

            # Try removing digits from end
            for i in range(1, min(3, len(digits_only) - 5)):  # Remove 1-2 digits
                truncated = digits_only[:-i]
                if truncated in valid_set:
                    return truncated, f"removed_{i}_from_end"

            # Try fuzzy matching as fallback
            # matches = get_close_matches(digits_only, self.valid_codes, n=1, cutoff=0.9)
            # if matches:
            #     return matches[0], "fuzzy_match"

            return None, "no_fix_found"

        for tray_name, tray_data in self.data.items():
            for page_num, page_data in tray_data.items():
                for position, text in page_data.items():
                    if not text or text.strip() == "":
                        continue

                    # Find all potential codes in the text
                    potential_codes = re.findall(code_pattern, text)

                    for raw_code in potential_codes:
                        fixed_code, fix_method = try_fix_code(raw_code)

                        results.append({
                            'tray': tray_name,
                            'page': page_num,
                            'position': position,
                            'raw_code': raw_code,
                            'fixed_code': fixed_code,
                            'fix_method': fix_method,
                            'is_valid': fixed_code is not None,
                            'context': text[:100] + "..." if len(text) > 100 else text
                        })

        self.results = results
        return results

    def get_results(self, tray_name="Tray_004"):
        filtered_results = []

        for result in self.results:
            if result.get('tray') == tray_name:
                filtered_results.append({
                    'tray': result['tray'],
                    'page': result['page'],
                    'position': result['position'],
                    'raw_code': result['raw_code'],
                    'fixed_code': result['fixed_code'],
                    'fix_method': result['fix_method'],
                    'is_valid': result['is_valid'],
                    'context': result['context']
                })

        return filtered_results


if __name__ == "__main__":
    code_extractor = CodeExtractor()
    extracted = code_extractor.extract_codes()

    for result in extracted:
        if result['is_valid']:
            # continue

            status = "✓"
            raw_code = re.sub(r'[-\s/\n\r]', '', result['raw_code'])
            if result['fix_method'] != "exact_match":
                print(f"{status} {raw_code} → {result['fixed_code']} ({result['fix_method']})")
            else:
                print(f"{status} {result['fixed_code']}")
        else:
            raw_code = re.sub(r'[-\s/\n\r]', '', result['raw_code'])
            print(f"✗ {raw_code} ({result['fix_method']})")
