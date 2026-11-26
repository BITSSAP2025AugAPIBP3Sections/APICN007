"""Produce the demo/vivo_*.mp3 recordings.

Two modes:

  python scripts/make_demos.py --tts        # synthesize Q+A audio with the
                                            # configured TTS engine (no mic).
                                            # Honest, reproducible placeholders.

  python scripts/make_demos.py --record     # record YOUR voice asking each
                                            # question, then append the bot's
                                            # spoken answer. This is what the
                                            # rubric ultimately wants.

The recording map (doc 04) is taken from rag.questions.VIVO_DEMO_MAP, plus a
free-choice vivo_0 that also demonstrates a follow-up for the doc-08 bonus.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from rag import pipeline  # noqa: E402
from rag.questions import OFFICIAL_QUESTIONS, VIVO_DEMO_MAP  # noqa: E402

load_dotenv()
DEMO = ROOT / "demo"


def synth_demo(ret, name: str, question: str, follow_up: str | None = None) -> None:
    from speech import tts

    turn = pipeline.answer(ret, question, [])
    script = f"Question: {question}\nAnswer: {turn.answer}"
    if follow_up:
        fu = pipeline.answer(
            ret, follow_up,
            [{"role": "user", "content": question},
             {"role": "assistant", "content": turn.answer[:1800]}],
        )
        script += f"\nFollow up: {follow_up}\nAnswer: {fu.answer}"
    out = DEMO / f"{name}.mp3"
    if tts.synthesize_to_file(script, str(out)):
        print(f"  wrote {out}")
    else:
        print(f"  FAILED to synthesize {out} (install/configure a TTS engine)")


def record_demo(ret, name: str, question_id: str) -> None:
    from speech import stt, tts

    print(f"\n[{name}] Please speak: {OFFICIAL_QUESTIONS.get(question_id, question_id)}")
    wav = stt.record_to_wav()
    spoken = stt.transcribe(wav) or OFFICIAL_QUESTIONS.get(question_id, "")
    turn = pipeline.answer(ret, spoken, [])
    print(f"  Bot> {turn.answer[:200]}...")
    tts.synthesize_to_file(f"{spoken}. {turn.answer}", str(DEMO / f"{name}.mp3"))
    print(f"  wrote {DEMO / f'{name}.mp3'} (note: mixing your mic audio + answer "
          "cleanly needs a short manual edit, or screen-record the session instead)")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tts", action="store_true", help="synthesize Q+A with TTS (no mic)")
    g.add_argument("--record", action="store_true", help="record your voice per question")
    args = ap.parse_args()

    DEMO.mkdir(parents=True, exist_ok=True)
    ret = pipeline.get_retriever()

    # vivo_0: free choice + a follow-up (doc-08 bonus evidence)
    if args.tts:
        synth_demo(
            ret, "vivo_0",
            OFFICIAL_QUESTIONS["Q-E02"],
            follow_up="And what is the limit under section 80CCD(1B) on top of that?",
        )
        for name, qid in VIVO_DEMO_MAP.items():
            synth_demo(ret, name, OFFICIAL_QUESTIONS[qid])
    else:
        record_demo(ret, "vivo_0", "Q-E02")
        for name, qid in VIVO_DEMO_MAP.items():
            record_demo(ret, name, qid)


if __name__ == "__main__":
    main()
