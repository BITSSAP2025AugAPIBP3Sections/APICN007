# Architecture

## Overview
APICN001 is a retrieve-then-generate chatbot for Indian Income-Tax questions,
wired for four interaction modes (TITO/TIVO/VITO/VIVO) over one pipeline. The
design goal was **grounded, year-aware answers that feel conversational on a
CPU-only laptop**, with the generator, embeddings, STT and TTS all swappable
from `.env`.

## Pipeline
`ingest → retrieve → generate`, implemented once in `src/rag/pipeline.py` and
reused by the CLI (`src/app.py`), the Streamlit UI (`src/ui/streamlit_app.py`),
and the benchmark/test/demo scripts, so there is a single graded code path.

1. **Ingest** (`src/rag/ingest.py`). PyMuPDF extracts per-page text from every
   PDF in `data/`. Text is chunked with a **sentence-aware sliding window**
   (~900 chars, 150 overlap) so legal claims are not cut mid-clause, and each
   chunk keeps `{doc, page, year}`. Budget PDFs are tagged with their financial
   year. Chunks are embedded once with `all-MiniLM-L6-v2` and cached to
   `embeddings.npy`; a `meta.json` records model, dims and pinned versions, so
   the index rebuilds deterministically (`python src/rag/ingest.py`).

2. **Retrieve** (`src/rag/retriever.py`). **Hybrid search**: BM25 (lexical) and
   dense cosine (semantic) are each ranked, then fused with **Reciprocal Rank
   Fusion**, which needs no score calibration between the two rankers. A
   **year-scope boost** nudges chunks from the financial year the question pins
   (e.g. "FY 2024-25", "AY 2025-26" → FY2024-25). Why hybrid: the corpus mixes
   exact legal tokens ("115BBH", "206C", "80C"), where lexical match wins, with
   paraphrased FAQ prose, where semantic match wins. If `sentence-transformers`
   is absent the retriever degrades to BM25-only, so the app runs anywhere.

3. **Generate** (`src/rag/llm.py`). One OpenAI-compatible client serves `slm`
   (Ollama/local), `groq`, `openai` and `openrouter`; `anthropic` uses its
   Messages API. Selection is purely from `LLM_PROVIDER`/`LLM_MODEL`. The system
   prompt forces answers from context only, source+page citations, explicit
   assumptions for computations, and an honest "I could not find this in the
   corpus" refusal. Both streaming (`chat_stream`) and blocking (`chat`) entry
   points exist.

## Modes and voice
- **TITO**: question → retrieve → streamed text + cited sources; multi-turn
  history retained for follow-ups.
- **TIVO**: same, plus **sentence-streamed TTS** — `speak_stream` speaks each
  sentence as it arrives, so the first words play before generation finishes.
- **VITO**: press-Enter/press-Enter mic capture → faster-whisper transcribes →
  the transcript is shown (so evaluators can verify) → text answer.
- **VIVO**: STT → RAG → streamed TTS, end to end. This is the headline mode and
  what `demo/vivo_*.mp3` records.

STT (`faster-whisper` local, or Groq/OpenAI Whisper via `.env`) and TTS
(`pyttsx3` offline default, or `edge`/`piper`) are both `.env`-switchable.

### TIVO / VITO availability (evidence)
Both are first-class CLI modes (`--mode tivo`, `--mode vito`) and are selectable
in the Streamlit UI radio without code edits. VITO prints the transcript before
answering; TIVO uses the same streaming-TTS path as VIVO. A spare synthesized
demo and the UI's audio widgets demonstrate each.

## Why these choices beat the baseline
The instructor's Voice Standard RAG demo runs in-browser on a toy corpus with
thin citations and no multi-turn memory. This bot adds: a **real local-SLM path
with a four-provider `.env` switch**, **hybrid year-aware retrieval over the
actual Income-Tax corpus with document+page citations on every answer**, and
**retained multi-turn context** for follow-ups (see `demo/vivo_0.mp3`). Latency
is attacked with streaming generation and sentence-streamed TTS (see
`report/latency_results.md`).

## Reproducibility & tests
`scripts/` rebuilds the corpus, the reports, and the demos one command each;
`tests/` covers chunking, provider resolution, and year detection (`pytest`,
all green). The index and PDFs are git-ignored and rebuilt from scripts.
