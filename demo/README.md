# VIVO demo recordings

This folder must contain the eight end-to-end voice demos the evaluator listens to:

| File | Question | |
|------|----------|--|
| `vivo_0.mp3` | free choice (Q-E02) **+ a follow-up** | multi-turn evidence (doc-08 bonus) |
| `vivo_1.mp3` | Q-E01 | |
| `vivo_2.mp3` | Q-E02 | |
| `vivo_3.mp3` | Q-E05 | |
| `vivo_4.mp3` | Q-M01 | |
| `vivo_5.mp3` | Q-M04 | |
| `vivo_6.mp3` | Q-C01 | |
| `vivo_7.mp3` | Q-C03 | |

## How to produce them

The recordings are **not committed** here because they require a live LLM
provider (and, for real voice-in, your microphone). Generate them in one command
once your `.env` points at a provider (`slm` or `groq`):

```bash
# Option A — record YOUR voice asking each question (what the rubric wants):
python scripts/make_demos.py --record

# Option B — fully synthesized question + spoken answer (no mic, reproducible):
python scripts/make_demos.py --tts
```

Each file contains the spoken question followed by the bot's spoken answer;
`vivo_0` additionally asks a natural follow-up ("and the 80CCD(1B) limit on top
of that?") answered with retained context.

> Tip: for the cleanest result, screen-record a live `python src/app.py --mode vivo`
> session per question — that captures your voice, the on-screen transcript, and
> the spoken answer together.
