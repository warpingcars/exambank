# exambank

Parafrasert studie/eksamensbank for UiB-fag (lesbar av GPT-agenter).

Open, paraphrased academic resource bank for UiB courses MAT221, STAT110, and INF161.  
The repository is designed so GPT agents can consume curated JSON entries that describe official, public course materials without exposing private work.

## Contents

- `schema.json` – validation rules for every resource item.
- `index.json` – aggregated manifest generated from files in `data/`.
- `data/<course>/<category>/` – paraphrased entries for exams, slides, and notes.
- `tools/` – helper scripts (`build_index.py`, optional vetting utilities).

## Contribution Principles

- Only paraphrase public, officially released material (e.g., old exams, posted slides).
- Do not include personal solutions, scans, or private notes.
- Keep `content_paraphrase` ≤ 120 words and focus on key ideas.
- Fill out `source_url` when a public link exists; otherwise leave empty.
- Run `python tools/build_index.py` before committing to refresh `index.json`.

## Quickstart

```bash
python tools/build_index.py
```

The script validates JSON structure (basic required keys) and regenerates `index.json`.  
After updating, push to GitHub so the index is available at:

```
https://raw.githubusercontent.com/<username>/warpe-exambank/main/index.json
```

## Lyra

This repository also powers the Lyra study hub. See `docs/LYRA.md` for the manifest and `docs/LYRA-DASHBOARD.md` for the generated progress dashboard.

## Raw index

- [index.json](./index.json)
