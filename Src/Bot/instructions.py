import json
import os

instructions_dir = "./Bot_Memory/Json/instructions"
output_file = "./Bot_Memory/Json/instructions.json"

merged = []

for filename in sorted(os.listdir(instructions_dir)):
    if filename.endswith(".json"):
        with open(os.path.join(instructions_dir, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            merged.extend(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"تم الدمج! عدد السجلات: {len(merged)} → {output_file}")
