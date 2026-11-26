"""Hybrid retriever: BM25 (lexical) + dense embeddings (semantic), fused with
Reciprocal Rank Fusion, plus a light year-scope boost.

Why hybrid: the corpus mixes precise legal tokens ("115BBH", "206C", "80C")
where lexical match is king, with paraphrased FAQ prose where semantic match
wins. RRF needs no score calibration between the two and is robust.

If ``embeddings.npy`` is absent (embedder was unavailable at ingest), the
retriever runs BM25-only so the app still works on any machine.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
STOP = set(
    "the a an and or of to in for on is are be with by from as at that this it "
    "under section subsection shall any such his her its".split()
)

# Financial-year phrasings a user might type, normalised to the ingest tag.
# Order matters: assessment-year (AY) rules are checked first because
# "AY 2025-26" means FY 2024-25 — the bare-year patterns below would otherwise
# mis-map it to FY2025-26.
_FY_PATTERNS = [
    (re.compile(r"\bay\.?\s*2023[\s\-/]*24\b"), "FY2022-23"),
    (re.compile(r"\bay\.?\s*2024[\s\-/]*25\b"), "FY2023-24"),
    (re.compile(r"\bay\.?\s*2025[\s\-/]*26\b"), "FY2024-25"),
    (re.compile(r"\bay\.?\s*2026[\s\-/]*27\b"), "FY2025-26"),
    (re.compile(r"\b(?:fy|financial year)?\s*2022[\s\-/]*23\b"), "FY2022-23"),
    (re.compile(r"\b(?:fy|financial year)?\s*2023[\s\-/]*24\b"), "FY2023-24"),
    (re.compile(r"\b(?:fy|financial year)?\s*2024[\s\-/]*25\b"), "FY2024-25"),
    (re.compile(r"\b(?:fy|financial year)?\s*2025[\s\-/]*26\b"), "FY2025-26"),
]


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOP]


def detect_year(query: str) -> str | None:
    q = query.lower()
    for pattern, year in _FY_PATTERNS:
        if pattern.search(q):
            return year
    return None


class Retriever:
    def __init__(self, index_dir: str | Path | None = None):
        index_dir = Path(index_dir or os.getenv("INDEX_DIR", "index"))
        chunks_path = index_dir / "chunks.json"
        if not chunks_path.exists():
            raise SystemExit(
                f"No index at {chunks_path}. Run `python src/rag/ingest.py` first."
            )
        self.records: list[dict] = json.loads(chunks_path.read_text(encoding="utf-8"))
        self.corpus_tokens = [tokenize(r["text"]) for r in self.records]
        self._init_bm25()
        self._init_dense(index_dir)

    # ---- lexical ----
    def _init_bm25(self) -> None:
        try:
            from rank_bm25 import BM25Okapi

            self.bm25 = BM25Okapi(self.corpus_tokens)
        except ImportError:
            self.bm25 = None  # fall back to the hand-rolled TF-IDF below

    def _bm25_scores(self, query: str):
        q = tokenize(query)
        if self.bm25 is not None:
            return self.bm25.get_scores(q)
        # Minimal TF-IDF fallback so the app runs even without rank_bm25.
        import math

        import numpy as np

        df: dict[str, int] = {}
        for toks in self.corpus_tokens:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        n = len(self.corpus_tokens)
        scores = np.zeros(n, dtype="float32")
        for i, toks in enumerate(self.corpus_tokens):
            if not toks:
                continue
            tf: dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            for t in set(q):
                if t in tf:
                    scores[i] += (tf[t] / len(toks)) * math.log(n / (1 + df.get(t, 0)))
        return scores

    # ---- semantic ----
    def _init_dense(self, index_dir: Path) -> None:
        self.embeddings = None
        self.embedder = None
        emb_path = index_dir / "embeddings.npy"
        if not emb_path.exists():
            return
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            self.embeddings = np.load(emb_path)
            meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
            self.embedder = SentenceTransformer(
                meta.get("embedding_model") or "sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as exc:  # noqa: BLE001 - degrade to BM25-only
            print(f"[retriever] dense disabled ({exc}); using BM25 only")
            self.embeddings = None
            self.embedder = None

    def _dense_scores(self, query: str):
        if self.embeddings is None or self.embedder is None:
            return None
        qv = self.embedder.encode([query], normalize_embeddings=True)[0]
        return self.embeddings @ qv  # cosine (vectors are pre-normalised)

    @staticmethod
    def _ranks(scores, k: int):
        import numpy as np

        order = np.argsort(-scores)[: max(k, 1)]
        return {int(idx): rank for rank, idx in enumerate(order)}

    def search(self, query: str, top_k: int | None = None, rrf_k: int = 60) -> list[dict]:
        top_k = int(top_k or os.getenv("TOP_K", 5))
        pool = max(top_k * 6, 30)

        lex = self._bm25_scores(query)
        lex_ranks = self._ranks(lex, pool)
        dense = self._dense_scores(query)
        dense_ranks = self._ranks(dense, pool) if dense is not None else {}

        # Reciprocal Rank Fusion across whichever rankers are available.
        fused: dict[int, float] = {}
        for i, r in lex_ranks.items():
            fused[i] = fused.get(i, 0.0) + 1.0 / (rrf_k + r)
        for i, r in dense_ranks.items():
            fused[i] = fused.get(i, 0.0) + 1.0 / (rrf_k + r)

        # Year-scope boost: nudge chunks from the FY the question pins.
        want_year = detect_year(query)
        if want_year:
            for i in list(fused):
                if self.records[i].get("year") == want_year:
                    fused[i] *= 1.15

        best = sorted(fused.items(), key=lambda kv: -kv[1])[:top_k]
        hits = []
        for i, score in best:
            hits.append({**self.records[i], "score": round(float(score), 5)})
        return hits

    @property
    def mode(self) -> str:
        return "hybrid (BM25 + dense RRF)" if self.embeddings is not None else "BM25 lexical"


if __name__ == "__main__":
    r = Retriever()
    print(f"retrieval mode: {r.mode}; chunks: {len(r.records)}")
    for h in r.search("tax rate on virtual digital assets under section 115BBH", top_k=3):
        print(f"\n[{h['doc']} p.{h['page']} year={h['year']} score={h['score']}]")
        print(h["text"][:200], "...")
