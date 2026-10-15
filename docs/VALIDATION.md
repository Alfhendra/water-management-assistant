# Validation

Local validation on 2026-10-15 completed successfully: 14 tests passed, including a subprocess CLI round trip. Eight sample outputs were generated through the public CLI against a temporary database.

```sh
python -m unittest discover -s tests -v
python scripts/generate_samples.py
```

| Area | Verified behavior |
|---|---|
| Analytics | Expected thresholds, mean rainfall, endpoint change, overdue IDs and decimal budget totals |
| Evidence | Source IDs accompany the derived result |
| Scope | Other-estate metrics, inventory, documents and evidence are excluded |
| Routing | English and Indonesian aliases return identical calculations |
| Abstention | Unsupported questions and scope-override text do not trigger analysis |
| Retrieval | Absent scoped SOP returns no data |
| Validation | Negative rainfall, nonfinite values, booleans, future dates, invalid dates and unknown fields fail |
| Deduplication | Exact duplicates are removed; conflicting IDs and duplicate block-days fail |
| Edge cases | Exact thresholds, single observations and empty datasets |
| Persistence | All zones exist; invalid ingestion preserves prior curated data |
| CLI | Ingest, ask, file export, structured scope errors and database-overwrite prevention |

CI is configured for Python 3.11–3.13 on Linux; this document records local results only, not a claimed remote CI run. The tests are engineering checks against synthetic fixtures, not validation of operational thresholds or customer performance.
