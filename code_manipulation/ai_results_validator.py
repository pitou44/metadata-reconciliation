from matching_codes import Codes
from pathlib import Path
import json

from collections import Counter
from collections import defaultdict

code_manager = Codes()
files = code_manager.grab_dng_files(Path(r"E:\VRC - Artists\Tray_032_Bellini_Bellotto"))
correct_codes = [f[0].split('_')[0] for f in files]
file_names = [f[0] for f in files]

print(file_names)

files_num = len(files)

ai_results_dir = "../result_jsons/tmp_json.json"  # gemini 2.5 flash
with open(ai_results_dir, encoding="utf-8") as f:
    ai_results = json.load(f)

correct = 0
incorrect = 0

for key in ai_results["matched_images"]:
    if str(ai_results["matched_images"][key]) + "_" + str(key) in file_names:
        correct += 1
    else:
        incorrect += 1

print("-- FINAL RESULTS --")
print(f"{round(correct / files_num * 100)}% of Images matched CORRECTLY")
print(f"{round(incorrect / files_num * 100)}% of Images matched WRONG")
print(f"{100 - round((correct + incorrect) / files_num * 100)}% of Images NOT MATCHED")

# Consensus algorithm
jsons = [json.load(open(f'../result_jsons/gemini_results_tray_30/gemini_result_{i}.json')) for i in range(1, 5)]

pairs = Counter()
for j in jsons:
    pairs.update(j['matched_images'].items())

votes = defaultdict(Counter)
for (img, code), count in pairs.items():
    votes[img][code] += count

# Build consensus result
consensus = {img: codes.most_common(1)[0][0] for img, codes in votes.items()}

print(consensus)
correct = 0
incorrect = 0

for key in consensus:
    if str(consensus[key]) + "_" + str(key) in file_names:
        correct += 1
    else:
        incorrect += 1

print("\n\n-- CONSENSUS FINAL RESULT --")
print(f"{round(correct / files_num * 100)}% of Images matched CORRECTLY")
print(f"{round(incorrect / files_num * 100)}% of Images matched WRONG")
print(f"{100 - round((correct + incorrect) / files_num * 100)}% of Images NOT MATCHED")