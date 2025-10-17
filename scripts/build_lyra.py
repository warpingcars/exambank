#!/usr/bin/env python3
import datetime
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_overview() -> dict:
    overview_path = ROOT / "data" / "uni" / "overview.json"
    return json.loads(overview_path.read_text(encoding="utf-8"))


def load_exam_items() -> list[dict]:
    items: list[dict] = []
    pattern = str(ROOT / "data" / "*" / "exams" / "*.json")
    for path in glob.glob(pattern):
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            continue

        course = payload.get("course")
        if not course:
            course = Path(path).parts[-3].upper()

        topics = payload.get("topics", [])
        items.append(
            {
                "course": course,
                "topics": topics,
                "file": path,
                "title": payload.get("title", ""),
            }
        )
    return items


def uniq(seq: list[str]) -> list[str]:
    unique: list[str] = []
    for item in seq:
        if item not in unique:
            unique.append(item)
    return unique


def format_locations(locations: list[dict], status: str) -> str:
    if not locations and not status:
        return ""
    if not locations:
        return status

    loc_str = " / ".join(loc["code"] for loc in locations if loc.get("code"))
    if status:
        loc_str = f"{loc_str} ({status})" if loc_str else status
    return loc_str


def build_dashboard() -> None:
    overview = load_overview()
    exam_items = load_exam_items()

    by_course: dict[str, list[dict]] = {}
    for item in exam_items:
        by_course.setdefault(item["course"], []).append(item)

    lines: list[str] = []
    lines.append(f"# Lyra Dashboard — {overview.get('semester', '')}")
    lines.append("")
    lines.append("| Fag | Navn | Dato | Tid | Sted | Status |")
    lines.append("|-----|------|------|-----|------|--------|")

    for course in overview.get("courses", []):
        code = course.get("code", "")
        name = course.get("name", "")
        exam = course.get("exam", {})
        date = exam.get("date", "")
        time = exam.get("time", "")
        locations = exam.get("locations", [])
        status = exam.get("status", "")
        loc_str = format_locations(locations, status)
        lines.append(
            f"| {code} | {name} | {date} | {time} | {loc_str} | {status or ''} |"
        )

    lines.append("")

    for course in overview.get("courses", []):
        code = course.get("code", "")
        name = course.get("name", "")
        lines.append(f"## {code} — {name}")
        course_items = by_course.get(code, [])
        all_topics = uniq(
            [topic for item in course_items for topic in item.get("topics", [])]
        )
        if all_topics:
            lines.append("Eksamenstema (parafrasert): " + ", ".join(all_topics))
        else:
            lines.append("Eksamenstema (parafrasert): (ingen entries funnet ennå)")

        lower_topics = [topic.lower() for topic in all_topics]
        if any("rekurs" in topic for topic in lower_topics) and any(
            "inkl" in topic or "ie" in topic for topic in lower_topics
        ):
            suggestion = "Økt: 1 rekursjon + 1 IE + 1 grafteori + 1 tallteori"
        else:
            head = all_topics[0] if all_topics else "valgfritt kjerne-topic"
            suggestion = f"Økt: 1 {head} + 1 nabotopic + 1 tidligere års gjenganger"

        lines.append("")
        lines.append(f"Neste forslag: {suggestion}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"Sist oppdatert: {datetime.datetime.now().isoformat()}")

    docs_dir = ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    dashboard_path = docs_dir / "LYRA-DASHBOARD.md"
    dashboard_path.write_text("\n".join(lines), encoding="utf-8")
    print("Built docs/LYRA-DASHBOARD.md")


if __name__ == "__main__":
    build_dashboard()
