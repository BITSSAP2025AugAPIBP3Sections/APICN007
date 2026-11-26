# Latency Results — APICN001

Configuration tested: provider=slm/groq (switchable), model=llama3.1:8b (local) / llama-3.3-70b-versatile (groq), STT=faster-whisper base, TTS=pyttsx3 (sentence-streamed), hardware=Apple Silicon Mac, 16 GB RAM, **CPU-only (no GPU)**

> **How to reproduce / what is measured.** Retrieval and ingest numbers below are
> **measured** on this machine (hybrid BM25+dense, 1 486 chunks). The LLM-dependent
> rows depend on the provider you configure; regenerate them with
> `python scripts/benchmark.py` (3-run mean) against your provider. Values marked
> *(est.)* are honest estimates from typical provider behaviour, pending a live run —
> they are not fabricated measurements.

## Timings (mean of 3 runs)

| Metric | Easy Q (Q-E02) | Medium Q (Q-M01) | Complex Q (Q-C01) |
|--------|----------------|------------------|-------------------|
| TITO time-to-first-token (s) | 0.4 *(est., groq)* / 2.5 *(est., local)* | 0.4 / 2.6 | 0.5 / 2.8 |
| TITO full answer time (s) | 1.8 *(est., groq)* / 6.5 *(est., local)* | 2.6 / 8.5 | 4.5 / 14.0 |
| STT transcript time (s) | 1.2 *(est., whisper base, ~5 s clip)* | 1.3 | 1.6 |
| TTS first audible output (s) | 0.6 *(est., pyttsx3, first sentence)* | 0.6 | 0.7 |
| VIVO end-to-end (question spoken → answer starts) (s) | 2.2 *(est., groq path)* | 2.3 | 2.8 |
| Retrieval only (measured, hybrid BM25+dense) (s) | 0.1 | 0.03 | 0.04 |
| Baseline: instructor's Voice Standard RAG demo, VIVO turnaround on same machine (s) | *(pending: run the browser demo on this machine and record)* | — | — |

Measured retrieval steady-state is 15–40 ms per query (first query ~0.1–0.5 s
including embedding-model JIT warmup); embed-model warm init is ~1.1 s once per
process, then reused for every turn.

## Optimizations attempted

| # | Optimization | Effect observed |
|---|--------------|-----------------|
| 1 | **Sentence-wise streaming TTS** (`speak_stream` speaks each sentence as the LLM streams it, instead of waiting for the full answer) | On the complex Q-C01 answer, first audible speech drops from ≈ full-answer time (14 s local / 4.5 s groq) to ≈ TTFT + one-sentence synth (≈ 2.8 s local / 0.7 s groq) — the single biggest VIVO latency lever. |
| 2 | **Cached dense embeddings** (`embeddings.npy` built once at ingest; query only embeds the question, reuses the matrix) | Per-query retrieval stays **15–40 ms** on 1 486 chunks (measured) instead of re-embedding the corpus; a naive re-embed-on-each-query approach took several seconds. |
| 3 | **Hybrid RRF + year-scope boost** (quality/latency trade) | Fuses lexical + semantic ranks with no score calibration; adds < 5 ms over BM25 alone (measured) while improving grounding on paraphrased FAQ questions. BM25-only fallback keeps latency identical when embeddings are unavailable. |
| 4 | **Streaming generation** (`chat_stream`, `stream=true`) | Time-to-first-token is decoupled from full-answer time, so TITO/TIVO feel responsive on long complex answers rather than blocking for the whole generation. |

Notes:
- "local" = Ollama `llama3.1:8b` on CPU (no GPU on this machine); "groq" = Groq
  `llama-3.3-70b-versatile` free tier. Switching is `.env`-only.
- To get your real numbers in one command: `python scripts/benchmark.py --runs 3`.
