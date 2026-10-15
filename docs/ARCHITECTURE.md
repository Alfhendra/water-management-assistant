# Architecture and implementation decisions

## Problem and boundaries

Water-management teams need a consistent way to inspect readings, check infrastructure progress and retrieve relevant guidance. The demonstration implements those operations over a shared synthetic dataset. Customer source material informed the workflow categories only; no source documents, branding, real site codes, coordinates, network details or credentials are distributed.

## Components

`data.py` validates the input before opening a write transaction. It retains the original parsed object in `raw`, deduplicated validated records in `cleaned`, and deterministically sorted records in `curated`. Raw is parsed JSON, not a byte-identical source archive. All three zones are replaced atomically; this is a current snapshot store rather than a historical data lake.

`assistant.py` validates the request, restricts every collection to the chosen estate, routes an exact supported phrase, invokes analytics or retrieval, and attaches source identifiers. Field queries must supply an estate. Management can query all estates or select one. User text never becomes executable SQL, and it cannot override the chosen scope. The SQLite read uses a parameterized query in read-only mode.

`analytics.py` computes per-block hydrological statistics and inventory exceptions. All thresholds and units are explicit. Records and evidence are included in answers so a reviewer can trace a number back to the fixture. Synthetic SOP retrieval uses an exact topic in document titles and returns the complete matching text; it is not vector search.

## Production concepts represented locally

| Concern | Mini implementation | Production extension |
|---|---|---|
| Operational ingestion | Explicit JSON contract | Scheduled source adapters and incremental ingestion |
| Shared analytical foundation | SQLite raw/cleaned/curated payloads | Governed storage, catalog, lineage and retention |
| Management queries | All-estate CLI scope | Verified management identity and analytical API |
| Field questions | Mandatory estate filter | Server-derived scope from authenticated claims |
| Reference retrieval | Synthetic documents and topic match | Governed indexed corpus with source citations |
| Assistant routing | Exact bilingual phrase set | Constrained intent extraction with evaluated abstention |
| Human decisions | Review-required result label | Authenticated review workflow and durable decision audit |
| Freshness | Explicit as-of date and age flags | Data freshness SLOs and ingestion monitoring |

The last column is a proposed extension, not implemented functionality. This repository has no cloud integration, mobile app, offline sync, LLM, vector database, forecasting model, authentication or equipment control. It makes no claims about production costs, throughput or availability.

## Trade-offs

1. Standard-library Python makes the demo runnable without secrets or dependency installation. An exact phrase router has limited language coverage but predictable behavior.
2. SQLite keeps the three zones consistent and makes ingestion failures easy to test. JSON payload storage is appropriate for the small fixture, not large-scale analytical queries.
3. Per-block statistics preserve gauge boundaries. Levels measured against different local datums must not be averaged into an estate-wide level.
4. Rules expose individual observations and thresholds. They do not establish causal relationships between rainfall and groundwater or predict floods.
5. Scope enforcement is separated from intent matching. A future language model should never decide which estates a user is allowed to access.
6. Every answer is labeled for human review. The label is not a persisted approval state or evidence of an actual review.

## Next engineering steps

Add source adapters behind a documented interface, authenticate requests, version datasets, and retain ingestion provenance. Evaluate a model-backed router against supported, ambiguous and adversarial questions. Test per-estate access in every downstream tool. Preserve deterministic arithmetic and source citations. Add metrics, alert delivery and operational review only after the responsible team defines approved thresholds and processes.
