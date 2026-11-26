"""Measure latency on the three benchmark questions (doc 05) and print a table
you can paste straight into report/latency_results.md.

    python scripts/benchmark.py            # 3 runs each, mean
    python scripts/benchmark.py --runs 5

Requires a configured LLM provider in .env. STT/TTS rows are measured only if
those engines are installed; otherwise they print "n/a (engine not installed)".
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv  # noqa: E402

from rag import llm, pipeline  # noqa: E402
from rag.questions import OFFICIAL_QUESTIONS  # noqa: E402

load_dotenv()

BENCH = {"Easy Q (Q-E02)": "Q-E02", "Medium Q (Q-M01)": "Q-M01", "Complex Q (Q-C01)": "Q-C01"}


def mean(xs: list[float]) -> float:
    return round(statistics.mean(xs), 1) if xs else 0.0


def measure_text(ret, question: str, runs: int) -> tuple[float, float]:
    first_tokens, totals = [], []
    for _ in range(runs):
        turn = pipeline.answer(ret, question, [])
        first_tokens.append(turn.first_token_s)
        totals.append(turn.total_s)
    return mean(first_tokens), mean(totals)


def measure_tts(sample: str) -> float | None:
    try:
        from speech import tts
    except Exception:  # noqa: BLE001
        return None
    import tempfile

    out = tempfile.mktemp(suffix=".mp3")
    t0 = time.time()
    ok = tts.synthesize_to_file(sample, out)
    return round(time.time() - t0, 1) if ok else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    args = ap.parse_args()

    ret = pipeline.get_retriever()
    provider, model, _ = llm.resolve()
    print(f"Configuration: provider={provider}, model={model}, retrieval={ret.mode}\n")

    ttft, full = {}, {}
    for label, qid in BENCH.items():
        print(f"benchmarking {label} ...")
        ttft[label], full[label] = measure_text(ret, OFFICIAL_QUESTIONS[qid], args.runs)

    tts_s = measure_tts("This is a one sentence latency probe for the text to speech engine.")

    cols = list(BENCH)
    print("\n| Metric | " + " | ".join(cols) + " |")
    print("|--------|" + "|".join(["----------------"] * len(cols)) + "|")
    print("| TITO time-to-first-token (s) | " + " | ".join(f"{ttft[c]}" for c in cols) + " |")
    print("| TITO full answer time (s) | " + " | ".join(f"{full[c]}" for c in cols) + " |")
    print("| STT transcript time (s) | " + " | ".join(["n/a (mic run)"] * len(cols)) + " |")
    tts_cell = f"{tts_s}" if tts_s is not None else "n/a (engine not installed)"
    print("| TTS first audible output (s) | " + " | ".join([tts_cell] * len(cols)) + " |")
    print("| VIVO end-to-end (question spoken -> answer starts) (s) | "
          + " | ".join(f"{round(ttft[c] + (tts_s or 0), 1)}" for c in cols) + " |")
    print("\n(VIVO end-to-end here = TTFT + TTS warmup; add your measured STT time for the "
          "true figure. Run voice modes with a mic for STT numbers.)")


if __name__ == "__main__":
    main()
