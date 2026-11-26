"""The retrieve-then-generate pipeline, shared by the CLI, the UI, and the
benchmark/test scripts so there is exactly one code path to grade.
"""
from __future__ import annotations

import os
import time
from collections.abc import Iterator
from dataclasses import dataclass, field

from rag import llm
from rag.retriever import Retriever


@dataclass
class Turn:
    question: str
    answer: str = ""
    hits: list[dict] = field(default_factory=list)
    retrieval_s: float = 0.0
    first_token_s: float = 0.0
    total_s: float = 0.0

    def sources(self) -> list[str]:
        seen: list[str] = []
        for h in self.hits:
            key = f"{h['doc']} p.{h['page']}"
            if key not in seen:
                seen.append(key)
        return seen


def build_context(hits: list[dict]) -> str:
    return "\n\n".join(
        f"[{h['doc']} p.{h['page']}] {h['text']}" for h in hits
    )


def retrieve(ret: Retriever, question: str, top_k: int | None = None) -> tuple[list[dict], float]:
    t0 = time.time()
    hits = ret.search(question, top_k=top_k)
    return hits, time.time() - t0


def answer_stream(
    ret: Retriever, question: str, history: list[dict] | None = None, top_k: int | None = None
) -> Iterator[tuple[str, Turn]]:
    """Yield (text_delta, turn) as the answer streams in. The final turn carries
    full timings and sources. Lets callers print/speak incrementally."""
    turn = Turn(question=question)
    hits, turn.retrieval_s = retrieve(ret, question, top_k)
    turn.hits = hits
    context = build_context(hits)

    t0 = time.time()
    got_first = False
    for delta in llm.chat_stream(question, context, history):
        if not got_first:
            turn.first_token_s = time.time() - t0
            got_first = True
        turn.answer += delta
        yield delta, turn
    turn.total_s = time.time() - t0


def answer(
    ret: Retriever, question: str, history: list[dict] | None = None, top_k: int | None = None
) -> Turn:
    """Blocking variant: run the whole turn and return it."""
    turn: Turn | None = None
    for _delta, turn in answer_stream(ret, question, history, top_k):
        pass
    if turn is None:  # streamed nothing
        hits, rs = retrieve(ret, question, top_k)
        turn = Turn(question=question, hits=hits, retrieval_s=rs)
    return turn


def get_retriever() -> Retriever:
    return Retriever(os.getenv("INDEX_DIR", "index"))
