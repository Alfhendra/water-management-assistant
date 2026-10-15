"""Deterministic analytics with explicit units, evidence and limitations."""
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from statistics import mean


def hydrology(rows, as_of):
    by_block = defaultdict(list)
    for row in rows:
        by_block[(row["estate"], row["block"])].append(row)
    blocks, alerts = [], []
    for (estate, block), records in sorted(by_block.items()):
        records.sort(key=lambda r: r["date"])
        latest = records[-1]
        age = (date.fromisoformat(as_of) - date.fromisoformat(latest["date"])).days
        blocks.append({"estate": estate, "block": block, "reading_count": len(records),
                       "mean_observed_rainfall_mm": round(mean(r["rainfall_mm"] for r in records), 2),
                       "latest": latest, "age_days": age,
                       "water_level_change_cm": round(latest["water_level_cm"] - records[0]["water_level_cm"], 2)
                       if len(records) > 1 else None})
        rules = [
            ("HIGH_WATER", latest["water_level_cm"] > 80, "water_level_cm", 80),
            ("DEEP_GROUNDWATER", latest["groundwater_depth_cm"] > 60, "groundwater_depth_cm", 60),
            ("HEAVY_RAIN", latest["rainfall_mm"] > 100, "rainfall_mm", 100),
        ]
        for code, triggered, metric, threshold in rules:
            if triggered:
                alerts.append({"code": code, "estate": estate, "block": block,
                               "source_id": latest["id"], "date": latest["date"],
                               "metric": metric, "value": latest[metric], "threshold_gt": threshold,
                               "action": "Verify the reading and request supervisor review; no equipment action is authorized."})
        if age > 2:
            alerts.append({"code": "STALE_READING", "estate": estate, "block": block,
                           "source_id": latest["id"], "age_days": age, "threshold_gt": 2,
                           "action": "Obtain a current reading before operational decisions."})
    return {"blocks": blocks, "alerts": alerts,
            "limitations": ["Demo thresholds are not operational limits.",
                            "Rainfall means use observed block-days; missing days are not zero rainfall.",
                            "Water level is relative to a synthetic local gauge datum; groundwater is depth below ground.",
                            "Endpoint change is descriptive, not a forecast or causal explanation."]}


def inventory(rows, as_of):
    overdue = [r for r in rows if r["status"] != "completed" and r["planned_completion"] < as_of]
    over_budget = [r for r in rows if r["spent_usd"] > r["budget_usd"]]
    money = lambda key: str(sum((Decimal(str(r[key])) for r in rows), Decimal("0.00")))
    return {"count": len(rows), "by_status": dict(sorted(Counter(r["status"] for r in rows).items())),
            "by_type": dict(sorted(Counter(r["type"] for r in rows).items())),
            "budget_usd": money("budget_usd"), "spent_usd": money("spent_usd"),
            "overdue_ids": [r["id"] for r in overdue],
            "over_budget_ids": [r["id"] for r in over_budget], "records": rows,
            "limitations": ["Budget and spend are synthetic USD amounts, not procurement recommendations."]}
