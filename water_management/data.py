"""Validate an explicit data contract and atomically persist three data zones."""
import json
import math
import re
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


class InputError(ValueError):
    pass


def fail(message):
    raise InputError(message)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,39}", value):
        fail("IDs must be uppercase letters, digits, underscores or hyphens (max 40).")
    return value


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail("Dates must use YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        fail("Invalid calendar date.")


def number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail("Measurements must be finite numbers.")
    if not low <= value <= high:
        fail("Measurement is outside the demo input range.")
    return value


def fields(obj, required):
    if not isinstance(obj, dict) or set(obj) != set(required.split()):
        fail("Record fields do not match the documented contract.")


def validate(raw):
    fields(raw, "dataset_id as_of readings structures documents")
    identifier(raw["dataset_id"])
    as_of = day(raw["as_of"])
    cleaned = {"dataset_id": raw["dataset_id"], "as_of": raw["as_of"]}
    removed = 0
    for collection in ("readings", "structures", "documents"):
        rows = raw[collection]
        if not isinstance(rows, list) or len(rows) > 10000:
            fail("Collections must be lists with at most 10000 records.")
        seen = {}
        natural_keys = set()
        for row in rows:
            required = {
                "readings": "id estate block date rainfall_mm water_level_cm groundwater_depth_cm",
                "structures": "id estate type status planned_completion budget_usd spent_usd",
                "documents": "id estate title text",
            }[collection]
            fields(row, required)
            identifier(row["id"])
            identifier(row["estate"])
            if collection == "readings":
                identifier(row["block"])
                if day(row["date"]) > as_of:
                    fail("Readings cannot be later than as_of.")
                number(row["rainfall_mm"], 0, 2000)
                number(row["water_level_cm"], -1000, 1000)
                number(row["groundwater_depth_cm"], 0, 1000)
            elif collection == "structures":
                day(row["planned_completion"])
                if row["type"] not in ("sluice_gate", "culvert", "weir"):
                    fail("Unknown structure type.")
                if row["status"] not in ("planned", "in_progress", "completed"):
                    fail("Unknown structure status.")
                for key in ("budget_usd", "spent_usd"):
                    number(row[key], 0, 1e9)
                    if round(row[key], 2) != row[key]:
                        fail("Budget amounts must have at most two decimal places.")
            else:
                for key in ("title", "text"):
                    if not isinstance(row[key], str) or not row[key].strip() or len(row[key]) > 10000:
                        fail("Document title and text must be nonempty text, max 10000 characters.")
            if row["id"] in seen:
                if seen[row["id"]] != row:
                    fail("Conflicting duplicate ID.")
                removed += 1
                continue
            if collection == "readings":
                key = (row["estate"], row["block"], row["date"])
                if key in natural_keys:
                    fail("Only one daily reading per estate/block is supported.")
                natural_keys.add(key)
            seen[row["id"]] = dict(row)
        cleaned[collection] = list(seen.values())
    return cleaned, removed


def ingest(source, db):
    source = Path(source)
    if source.stat().st_size > 5_000_000:
        fail("Input exceeds 5 MB.")
    raw = json.loads(source.read_text(encoding="utf-8"))
    cleaned, removed = validate(raw)
    # Curated data has stable ordering; queries never access the raw zone.
    curated = {**cleaned, **{key: sorted(cleaned[key], key=lambda r: r["id"])
                           for key in ("readings", "structures", "documents")}}
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS zones (name TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        conn.executemany("INSERT OR REPLACE INTO zones VALUES (?, ?)",
                         [(name, json.dumps(obj, allow_nan=False)) for name, obj in
                          (("raw", raw), ("cleaned", cleaned), ("curated", curated))])
    return {"status": "ingested", "dataset_id": cleaned["dataset_id"],
            "duplicates_removed": removed,
            "counts": {key: len(cleaned[key]) for key in ("readings", "structures", "documents")}}


def load(db):
    if not Path(db).is_file():
        fail("No dataset found. Run ingest first.")
    with closing(sqlite3.connect(f"{Path(db).resolve().as_uri()}?mode=ro", uri=True)) as conn:
        row = conn.execute("SELECT payload FROM zones WHERE name = ?", ("curated",)).fetchone()
    if row is None:
        fail("No curated dataset found.")
    return json.loads(row[0])
