# Submission — APICN001

- Team ID: APICN001
- App entry point: `python src/app.py`
- Default provider: SLM (Ollama + llama3.1:8b) — switchable to groq/openai/anthropic/openrouter via `.env`
- STT engine: faster-whisper (`base`), press-Enter / press-Enter recording; Groq/OpenAI Whisper via `.env`
- TTS engine: pyttsx3 (offline, macOS NSSS), sentence-wise streaming; edge / piper via `.env`
- Retrieval: hybrid BM25 + dense (all-MiniLM-L6-v2) with Reciprocal Rank Fusion and year-scope boost

## External data used
- None beyond the assignment corpus. The committed `data/` PDFs are the
  assignment's own files; the ~171 MB Income-tax Act 1961 is pulled from this
  assignment's GitHub Release via `scripts/download_corpus.py` (not re-hosted here).

## AI coding assistant disclosure
- Built with **Claude Code (Anthropic, claude-opus / claude-sonnet)** acting as a
  pair-programmer. It was used to:
  - scaffold the mandatory repo structure from the assignment instructions;
  - write the RAG pipeline (sentence-aware chunking, hybrid BM25+dense retrieval
    with RRF, the provider-switch LLM client with streaming), the STT/TTS modules,
    the CLI/Streamlit app, the benchmark/test/demo scripts, and the unit tests;
  - draft the reference answers and working in `report/test_results.md` from the
    retrieved corpus context, and draft the architecture/limitations write-ups.
- All generated code was reviewed and executed locally (ingest + retrieval +
  unit tests run green). Numbers that require a live LLM/mic are reproduced with
  the committed scripts (`scripts/run_test_suite.py`, `scripts/benchmark.py`,
  `scripts/make_demos.py`) and should be re-run on the grader's configured
  provider; see each report's header note.

## One-line claim to fame
- Hybrid BM25 + dense RRF retrieval with financial-year scoping and
  sentence-streamed TTS — grounded, year-aware answers that start speaking before
  generation finishes, on a CPU-only laptop.
