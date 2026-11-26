# Limitations

Known weaknesses of this bot, honestly stated:

1. **Generation quality depends on the provider.** The pipeline is correct, but
   answer accuracy on the hard computation questions (Q-C01, Q-C03) tracks the
   chosen LLM. A CPU-only local `llama3.1:8b` sometimes slips on multi-step slab
   arithmetic; Groq's larger model is more reliable. The committed
   `report/test_results.md` reference answers were drafted from the retrieved
   corpus context and should be regenerated per provider with
   `scripts/run_test_suite.py`.

2. **Retrieval is chunk-level, not table-aware.** Budget slab tables and the
   indexation (CII) table are flattened to text during ingest, so a figure
   occasionally lands in a different chunk from its heading. Top-k is widened to
   compensate, but a reranker or table-structured parsing would ground numeric
   questions better.

3. **The full Income-tax Act 1961 is optional at build time.** It is a ~171 MB
   release asset fetched by `scripts/download_corpus.py`. Without it, section-level
   questions (exact wording of 80C/115BBH/194S/206C/112A) rely on the Budget and
   FAQ documents rather than the Act's own text, which can thin out citations.

4. **Corpus filename quirk.** In the assignment corpus the FII and BIS FAQ
   filenames are swapped (FII content is inside `FAQs-on-BIS-Exemption.pdf`). The
   bot cites the file that actually holds the content, which is correct but can
   look surprising.

5. **Voice latency is not sub-second on CPU.** First audible speech is driven by
   LLM time-to-first-token plus one-sentence TTS synth; on a local CPU SLM this
   is a few seconds. Streaming TTS mitigates it, but a GPU or a cloud provider is
   needed for the stretch targets.

6. **Press-to-talk, not VAD.** Recording is Enter-to-start/Enter-to-stop. There
   is no voice-activity detection or barge-in, so the bot cannot be interrupted
   mid-answer.

7. **TTS voice quality.** The default `pyttsx3` is robotic; `edge`/`piper` sound
   far better but add a dependency or network call. Inline citations are stripped
   before speaking, so spoken answers cite sources only loosely.

8. **No numeric self-check.** The bot does not validate its own arithmetic
   against a tax calculator, so a slab or surcharge slip passes through unflagged.
