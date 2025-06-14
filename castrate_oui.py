from pathlib import Path
import json

input_file = Path("oui.txt")
output_file = Path("oui.json")

oui_dict = {}

for line in input_file.read_text(encoding="utf-8", errors="ignore").splitlines():
    if "(hex)" in line:
        parts = line.split("(hex)", 1)
        if len(parts) == 2:
            mac = parts[0].strip().upper()
            vendor = parts[1].strip()
            oui_dict[mac] = vendor

with output_file.open("w", encoding="utf-8") as f:
    json.dump(oui_dict, f, indent=2, ensure_ascii=False)

print(f"{len(oui_dict)} Einträge als JSON gespeichert in {output_file}")
