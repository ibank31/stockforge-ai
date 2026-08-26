from pathlib import Path

path = Path(__file__).resolve().parents[1] / "docs/research/TRADITIONAL_FOOD_GLOBAL_ASSET_RESEARCH_2026-08-26.md"
text = path.read_text(encoding="utf-8")
required = [
    "## Ringkasan eksekutif",
    "## 2. Evidence yang digunakan",
    "## 3. Kerangka prioritas produksi",
    "## 5. Asset contract untuk agent berikutnya",
    "## 9. File dalam branch ini",
    "## References",
]
missing = [heading for heading in required if heading not in text]
reference_count = sum(1 for line in text.splitlines() if line.startswith("[") and "]: " in line)
print({"missing_sections": missing, "reference_count": reference_count})
assert not missing
assert reference_count >= 16
