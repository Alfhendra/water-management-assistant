"""Generate checked-in examples using the public CLI and an isolated database."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = [sys.executable, "-m", "water_management", "--db", str(Path(tmp) / "demo.sqlite3")]
        cases = {
            "output_ingest.json": ["ingest", "samples/input.json"],
            "output_management.json": ["ask", "summary"],
            "output_field.json": ["ask", "ringkasan kondisi air", "--role", "field", "--estate", "ESTATE_A"],
            "output_inventory.json": ["ask", "show overdue structures"],
            "output_sop.json": ["ask", "tampilkan sop air tinggi", "--role", "field", "--estate", "ESTATE_A"],
            "output_no_data.json": ["ask", "show high water sop", "--role", "field", "--estate", "ESTATE_B"],
            "output_unsupported.json": ["ask", "Predict next month flooding"],
            "output_invalid_scope.json": ["ask", "summary", "--role", "field"],
        }
        for filename, args in cases.items():
            run = subprocess.run(base + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            expected = 1 if filename == "output_invalid_scope.json" else 0
            if run.returncode != expected:
                raise RuntimeError(f"Example failed: {filename}")
            parsed = json.loads(run.stdout)
            (ROOT / "samples" / filename).write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Generated {len(cases)} examples through the CLI.")


if __name__ == "__main__":
    main()
