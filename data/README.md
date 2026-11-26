# data/

The retrieval corpus (Income-Tax India). These files are **git-ignored**
(`data/*.pdf`) and rebuilt/placed by a script, not committed — the index is
regenerated from them by `python src/rag/ingest.py`.

## What belongs here
- The assignment's committed PDFs: Union Budget speeches `bs202223.pdf` …
  `bs2025_26.pdf`, and the CBDT FAQ PDFs (crypto guidance, BIS/FII exemption,
  transition provisions).
- The large **Income-tax Act 1961 (as amended to 2026)**, ~171 MB — a GitHub
  **Release** asset of the assignment repo, not part of its git tree.

## How to populate
```bash
python scripts/download_corpus.py      # fetches the ~171 MB Act from the release
# the smaller PDFs ship with the assignment repo; copy them here if missing:
#   cp /path/to/VoiceBotAssignment/data/*.pdf data/
```

Ingest picks up every `*.pdf` here. It works with or without the full Act, but
without it section-level answers (80C, 115BBH, 194S, 206C, 112A, residential
status) lean on the Budget and FAQ documents instead of the Act's own text.
