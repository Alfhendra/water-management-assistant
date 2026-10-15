"""Bounded bilingual question routing, scoped retrieval and sourced answers."""
from .analytics import hydrology, inventory
from .data import InputError


QUESTIONS = {
    "summary": ("summary", "ringkasan", "summarize water conditions", "ringkasan kondisi air"),
    "hydrology": ("show hydrology", "tampilkan hidrologi", "show rainfall and water levels", "tampilkan curah hujan dan tinggi muka air"),
    "inventory": ("show water structures", "tampilkan bangunan air", "show overdue structures", "tampilkan bangunan terlambat"),
    "sop": ("show monitoring sop", "tampilkan sop pemantauan", "show high water sop", "tampilkan sop air tinggi"),
}


def ask(data, question, role="management", estate=None):
    if role not in ("management", "field"):
        raise InputError("Unknown role.")
    if not isinstance(question, str) or not question.strip() or len(question) > 500:
        raise InputError("Question must contain 1 to 500 characters.")
    if role == "field" and not estate:
        raise InputError("Field role requires an explicit estate scope.")
    estates = {r["estate"] for key in ("readings", "structures", "documents") for r in data[key]}
    if estate and estate not in estates:
        raise InputError("Unknown estate scope.")
    # Scope every collection before analytics, retrieval, or evidence generation.
    scoped = {key: [r for r in data[key] if not estate or r["estate"] == estate]
              for key in ("readings", "structures", "documents")}
    normalized = " ".join(question.lower().strip().rstrip("?.!").split())
    intent = next((key for key, phrases in QUESTIONS.items() if normalized in phrases), None)
    result = {"status": "answered", "dataset_id": data["dataset_id"], "as_of": data["as_of"],
              "scope": {"role": role, "estate": estate or "ALL"},
              "question": question, "intent": intent, "evidence": [],
              "trace": ["validate_request", "scope_curated_data", "route_question"],
              "mode": "deterministic_demo", "review_status": "human_review_required"}
    if intent is None:
        result.update(status="unsupported_question", answer="Use one of the supported questions; no answer was inferred.",
                      supported_questions=[phrases[0] for phrases in QUESTIONS.values()])
        return result
    answer = {}
    if intent in ("summary", "hydrology"):
        answer["hydrology"] = hydrology(scoped["readings"], data["as_of"])
        result["evidence"].extend({"collection": "readings", "id": r["id"], "estate": r["estate"], "date": r["date"]}
                                  for r in scoped["readings"])
    if intent in ("summary", "inventory"):
        answer["inventory"] = inventory(scoped["structures"], data["as_of"])
        result["evidence"].extend({"collection": "structures", "id": r["id"], "estate": r["estate"]}
                                  for r in scoped["structures"])
    if intent == "sop":
        topic = "high water" if "high water" in normalized or "air tinggi" in normalized else "monitoring"
        matches = [r for r in scoped["documents"] if topic in r["title"].lower()]
        answer["documents"] = matches
        result["evidence"].extend({"collection": "documents", "id": r["id"], "estate": r["estate"], "title": r["title"]}
                                  for r in matches)
        answer["limitations"] = ["Exact topic retrieval from synthetic guidance, not semantic RAG or an approved field SOP."]
    if not result["evidence"]:
        result["status"] = "no_data"
    result["answer"] = answer
    result["trace"].extend(["compute_or_retrieve", "attach_evidence", "require_human_review"])
    return result
