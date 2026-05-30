import json
import os

laws_dir = "./Bot_Memory/Json/laws"
output_file = "./Bot_Memory/Json/laws.json"

merged = []

for filename in sorted(os.listdir(laws_dir)):
    if filename.endswith(".json"):
        with open(os.path.join(laws_dir, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            merged.extend(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"تم الدمج! عدد السجلات: {len(merged)} → {output_file}")
