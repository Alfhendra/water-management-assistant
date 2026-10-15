import argparse
import json
import sqlite3
import sys
from pathlib import Path
from .assistant import QUESTIONS, ask
from .data import InputError, ingest, load


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic water-management assistant; local and credential-free.")
    parser.add_argument("--db", default="data/water.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)
    i = sub.add_parser("ingest")
    i.add_argument("input")
    a = sub.add_parser("ask")
    a.add_argument("question")
    a.add_argument("--role", choices=("management", "field"), default="management")
    a.add_argument("--estate")
    a.add_argument("--output")
    sub.add_parser("questions")
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            result = ingest(args.input, args.db)
        elif args.command == "questions":
            result = QUESTIONS
        else:
            result = ask(load(args.db), args.question, args.role, args.estate)
        rendered = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
        if getattr(args, "output", None):
            dest = Path(args.output)
            if dest.resolve() == Path(args.db).resolve():
                raise InputError("Output must not overwrite the database.")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return 0
    except (InputError, json.JSONDecodeError, UnicodeError, OSError, sqlite3.Error) as exc:
        # Do not echo input records, paths or database internals into errors.
        message = str(exc) if isinstance(exc, InputError) else "Unable to read, validate or persist data. Check input and local paths."
        print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": message}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
