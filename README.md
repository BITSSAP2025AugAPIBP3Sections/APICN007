# APICN001 — RAG VoiceBot

A retrieval-augmented chatbot for **Indian Income-Tax** questions that works in
all four interaction modes — **TITO, TIVO, VITO, VIVO** — with a locally-running
SLM by default and a `.env` switch to Groq / OpenAI / Anthropic / OpenRouter.
Answers are grounded in the assignment corpus (Income-tax Act 1961, Union Budget
speeches FY2022-23 → FY2025-26, and CBDT FAQs) and every answer cites its source
document and page.

## Team
| Member | Role | Email |
|--------|------|-------|
| Aniket Shaw | Developer (RAG + voice + reports) | aniketshaw29@users.noreply.github.com |

## How to run
1. `python -m venv .venv` and activate it (`source .venv/bin/activate`).
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and set `LLM_PROVIDER=<provider>` (+ model/key).
   - **Local SLM (default):** install [Ollama](https://ollama.com), then
     `ollama pull llama3.1:8b` and `ollama serve`. Keep `LLM_PROVIDER=slm`.
   - **No local GPU?** Set `LLM_PROVIDER=groq` and `GROQ_API_KEY=...` (free tier).
4. Get the corpus into `data/`:
   - The small PDFs are already committed under `data/`.
   - The ~171 MB Income-tax Act is a GitHub **Release** asset — run
     `python scripts/download_corpus.py` (or download it manually and drop it in `data/`).
5. `python src/rag/ingest.py` — builds the index at `index/`.
6. `python src/app.py` — interactive mode menu. Or go straight to a mode:
   - `python src/app.py --mode tito`
   - `python src/app.py --question "What is the 80C limit?"` (one-shot)
   - `python src/app.py --ui` (Streamlit web UI with all four modes)

> **Note on `python`:** if your shell aliases `python` to a non-venv interpreter,
> call `.venv/bin/python` explicitly (this repo was built and tested that way).

## Modes
- **TITO** (`--mode tito`) — type a question, read a streamed text answer with
  cited sources. Multi-turn context is retained for follow-ups.
- **TIVO** (`--mode tivo`) — same, plus the answer is spoken sentence-by-sentence
  as it streams (so the first words play before generation finishes).
- **VITO** (`--mode vito`) — press Enter to start/stop recording → faster-whisper
  transcribes → the transcript is shown → RAG answers as text.
- **VIVO** (`--mode vivo`) — voice in **and** voice out, chained end to end. This
  is the headline mode; `demo/vivo_*.mp3` records it.

All four modes are also reachable from the Streamlit UI (`--ui`) with no code edits.

## Retrieval
Hybrid **BM25 (lexical) + dense embeddings (all-MiniLM-L6-v2) fused with
Reciprocal Rank Fusion**, with a year-scope boost that prefers the financial year
a question pins. If `sentence-transformers` is not installed the retriever
degrades gracefully to BM25-only, so the app still runs anywhere.

## Providers (all via `.env`, one code path)
`slm` (Ollama/any OpenAI-compatible local runtime) · `groq` · `openai` ·
`openrouter` share one OpenAI-compatible client; `anthropic` uses its Messages
API. See [`.env.example`](.env.example).

## Hardware used
- Apple Mac (Apple Silicon), macOS, 16 GB RAM, **CPU-only** (no discrete GPU).
- Retrieval and ingest run in ~1–2 s on this machine; LLM latency depends on the
  chosen provider (local SLM vs. hosted). See [`report/latency_results.md`](report/latency_results.md).

## Repository layout
```
src/app.py            entry point (all four modes + one-shot + --ui)
src/rag/              ingest.py · retriever.py · llm.py · pipeline.py · questions.py
src/speech/           stt.py · tts.py
src/ui/               streamlit_app.py
scripts/              download_corpus.py · ingest is in src · benchmark.py · run_test_suite.py · make_demos.py
report/               test_results.md · latency_results.md · architecture.md · limitations.md
demo/                 vivo_0..7 recordings (see demo/README.md)
tests/                pytest unit tests
```

## Reproducing the reports
- `python scripts/run_test_suite.py` — runs all 13 official questions and writes
  `report/test_results.generated.md` (the bot's verbatim answers).
- `python scripts/benchmark.py` — prints the latency table for the three
  benchmark questions.
- `python scripts/make_demos.py --record` (mic) or `--tts` (synthesized) — builds
  the `demo/vivo_*.mp3` files.
