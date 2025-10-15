#!/usr/bin/env python3
"""Aggregate all resource JSON files into index.json.

The script walks through data/<course>/<category>/ directories, loads each JSON
file (single object or list of objects), optionally validates against the local
schema.json (if jsonschema is installed), and writes a sorted index.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
SCHEMA_PATH = REPO_ROOT / "schema.json"
INDEX_PATH = REPO_ROOT / "index.json"


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip JSON Schema validation even if jsonschema is installed.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def load_schema():
    if not SCHEMA_PATH.exists():
        return None
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return None
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def iter_resource_files() -> Iterable[Path]:
    if not DATA_ROOT.exists():
        return []
    return sorted(DATA_ROOT.rglob("*.json"))


def normalise_items(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise TypeError(f"Unsupported JSON structure in {path}")


def validate_items(items: List[dict], validator) -> None:
    if validator is None:
        return
    for idx, item in enumerate(items, start=1):
        try:
            validator.validate(item)
        except Exception as exc:
            raise ValueError(f"{validator.schema.get('title','schema')} violation in item #{idx}: {exc}")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    schema = None
    validator = None
    if not args.no_validate:
        schema = load_schema()
        if schema is not None:
            try:
                from jsonschema import Draft202012Validator  # type: ignore
            except ImportError:
                validator = None
            else:
                validator = Draft202012Validator(schema)

    all_items: List[dict] = []
    for path in iter_resource_files():
        if path == INDEX_PATH:
            continue
        entries = normalise_items(path)
        validate_items(entries, validator)
        for entry in entries:
            entry.setdefault("course", infer_course_from_path(path))
            entry.setdefault("category", infer_category_from_path(path))
            entry.setdefault("_source_path", str(path.relative_to(REPO_ROOT)))
        all_items.extend(entries)

    all_items.sort(
        key=lambda x: (
            x.get("course", ""),
            x.get("category", ""),
            x.get("source_id", ""),
        )
    )

    INDEX_PATH.write_text(json.dumps(all_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Built index.json with {len(all_items)} item(s)")
    if validator is None and schema is not None and not args.no_validate:
        print("jsonschema not installed; skipping validation", file=sys.stderr)
    return 0


def infer_course_from_path(path: Path) -> str:
    parts = path.parts
    if "data" in parts:
        idx = parts.index("data")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def infer_category_from_path(path: Path) -> str:
    parts = path.parts
    if "data" in parts:
        idx = parts.index("data")
        if idx + 2 < len(parts):
            return parts[idx + 2]
    return ""


if __name__ == "__main__":
    sys.exit(main())
