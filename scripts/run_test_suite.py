"""Run all 13 official questions through the bot (TITO) and write a filled
report/test_results.md that matches the doc-05 template exactly.

    python scripts/run_test_suite.py

Requires a configured LLM provider in .env. This is the honest way to produce
the "Answer given" column — it is the bot's real, verbatim output. Re-run it
after changing the provider/model so the committed report reflects reality.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from rag import llm, pipeline  # noqa: E402
from rag.questions import OFFICIAL_QUESTIONS  # noqa: E402

load_dotenv()

GROUPS = {"Easy": "Q-E", "Medium": "Q-M", "Complex": "Q-C"}
TRUNC = 400


def truncate(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= TRUNC else text[:TRUNC].rstrip() + "…"


def main() -> None:
    ret = pipeline.get_retriever()
    provider, model, _ = llm.resolve()
    import os

    top_k = int(os.getenv("TOP_K", 5))

    results: dict[str, pipeline.Turn] = {}
    for qid, q in OFFICIAL_QUESTIONS.items():
        print(f"running {qid} ...")
        results[qid] = pipeline.answer(ret, q, [])

    out = [
        f"# TITO Test Results — {ROOT.name}",
        "",
        f"- Date tested: {dt.date.today().isoformat()}",
        f"- LLM_PROVIDER: {provider}",
        f"- LLM_MODEL: {model}",
        f"- Retrieved top-k: {top_k}",
        f"- Vector store: {ret.mode}",
        "",
    ]
    for title, prefix in GROUPS.items():
        out += [
            f"## {title}",
            "",
            "| ID | Question | Answer given | Correct? (yes/partial/no) | Evaluator note | Sources cited |",
            "|----|----------|--------------|---------------------------|----------------|---------------|",
        ]
        for qid, q in OFFICIAL_QUESTIONS.items():
            if not qid.startswith(prefix):
                continue
            t = results[qid]
            ans = truncate(t.answer).replace("|", "\\|")
            srcs = "; ".join(t.sources()).replace("|", "\\|")
            out.append(f"| {qid} | {q} | {ans} | | | {srcs} |")
        out.append("")

    (ROOT / "report" / "test_results.generated.md").write_text("\n".join(out), encoding="utf-8")
    print("Wrote report/test_results.generated.md — review, self-assess the Correct? column, "
          "then rename to test_results.md.")


if __name__ == "__main__":
    main()
