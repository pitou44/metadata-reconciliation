import re
import json, random
from difflib import get_close_matches
from load_metadata import Metadata


def extract_codes(data, valid_codes):
    # Pattern to find potential codes (6+ digits with optional dashes/spaces)
    code_pattern = r'\d{2,4}[-\s.]?\d{3,6}\b'

    results = []
    valid_set = set(valid_codes)

    def try_fix_code(raw_code):
        digits_only = re.sub(r'[-\s/\n\r.]', '', raw_code)

        # Filter out codes that are too short
        if len(digits_only) < 5:
            return None, "too_short"

        # Filter out date patterns (4 digits - 4 digits)
        if re.match(r'^\d{4}-\d{4}$', raw_code):
            return None, "date_pattern"

        # Try exact match first
        if digits_only in valid_set:
            return digits_only, "exact_match"

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
        matches = get_close_matches(digits_only, valid_codes, n=1, cutoff=0.8)
        if matches:
            return matches[0], "fuzzy_match"

        return None, "no_fix_found"

    for tray_name, tray_data in data.items():
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
        break

    return results


# Example usage:
metadata = Metadata()
valid_codes = [str(int(str(key).split('.')[0])) for key in metadata.data.keys()]#random.sample(list(metadata.data.keys()), 1000)

#valid_codes = ["93-11257", "96-45708", "02-03841"]

with open("../results.json", "r") as f:
    data = json.load(f)

extracted = extract_codes(data, valid_codes)

for result in extracted:
    if result['is_valid']:
        # print(result)
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
