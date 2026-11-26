"""APICN001 — RAG VoiceBot. Entry point for all four interaction modes.

    python src/app.py                      # interactive menu
    python src/app.py --mode tito          # Text In,  Text Out
    python src/app.py --mode tivo          # Text In,  Voice Out
    python src/app.py --mode vito          # Voice In, Text Out
    python src/app.py --mode vivo          # Voice In, Voice Out  (headline mode)
    python src/app.py --question "What is the 80C limit?"   # one-shot (latency)
    python src/app.py --ui                 # launch the Streamlit web UI

Voice modes need: pip install faster-whisper sounddevice soundfile pyttsx3
Text modes need only an LLM provider configured in .env (SLM/Groq/OpenAI/...).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # noqa: E402

from rag import llm, pipeline  # noqa: E402

load_dotenv()

VOICE_IN = {"vito", "vivo"}
VOICE_OUT = {"tivo", "vivo"}


def _print_sources(turn: pipeline.Turn) -> None:
    srcs = turn.sources()
    if srcs:
        print("\n\033[2mSources: " + "; ".join(srcs) + "\033[0m")
    print(
        f"\033[2m[retrieval {turn.retrieval_s*1000:.0f} ms"
        + (f" · first token {turn.first_token_s:.1f} s" if turn.first_token_s else "")
        + (f" · total {turn.total_s:.1f} s" if turn.total_s else "")
        + "]\033[0m"
    )


def _get_question(mode: str) -> str | None:
    if mode in VOICE_IN:
        from speech import stt

        wav = stt.record_to_wav()
        question = stt.transcribe(wav)
        if question:
            print(f"\nYou (spoken)> {question}")
        return question
    try:
        return input("\nYou> ").strip()
    except (EOFError, KeyboardInterrupt):
        return None


def run_turn(ret, question: str, history: list[dict], mode: str) -> pipeline.Turn:
    print("\nBot> ", end="", flush=True)
    if mode in VOICE_OUT:
        from speech import tts

        turn = None
        def deltas():
            nonlocal turn
            for delta, t in pipeline.answer_stream(ret, question, history):
                turn = t
                print(delta, end="", flush=True)
                yield delta
        for _ in tts.speak_stream(deltas()):
            pass
    else:
        turn = None
        for delta, t in pipeline.answer_stream(ret, question, history):
            turn = t
            print(delta, end="", flush=True)
    print()
    if turn is None:
        turn = pipeline.Turn(question=question)
    _print_sources(turn)
    return turn


def chat_loop(mode: str) -> None:
    ret = pipeline.get_retriever()
    provider, model, _ = llm.resolve()
    print(f"APICN001 VoiceBot · mode={mode.upper()} · provider={provider}:{model} · retrieval={ret.mode}")
    print("Type 'quit' to exit. Multi-turn context is retained for follow-ups.\n")
    history: list[dict] = []
    while True:
        question = _get_question(mode)
        if question is None or question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        turn = run_turn(ret, question, history, mode)
        history += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": turn.answer[:1800]},
        ]


def one_shot(question: str, mode: str) -> None:
    ret = pipeline.get_retriever()
    t_start = time.time()
    turn = run_turn(ret, question, [], mode)
    print(f"\033[2m[wall {time.time()-t_start:.1f} s]\033[0m")


def menu() -> str:
    print("APICN001 RAG VoiceBot — choose a mode:")
    print("  1) TITO  Text In,  Text Out")
    print("  2) TIVO  Text In,  Voice Out")
    print("  3) VITO  Voice In, Text Out")
    print("  4) VIVO  Voice In, Voice Out")
    choice = input("Select 1-4 [1]: ").strip() or "1"
    return {"1": "tito", "2": "tivo", "3": "vito", "4": "vivo"}.get(choice, "tito")


def main() -> None:
    parser = argparse.ArgumentParser(description="APICN001 RAG VoiceBot")
    parser.add_argument("--mode", choices=["tito", "tivo", "vito", "vivo"])
    parser.add_argument("--question", help="one-shot question, then exit")
    parser.add_argument("--ui", action="store_true", help="launch the Streamlit web UI")
    args = parser.parse_args()

    if args.ui:
        here = Path(__file__).resolve().parent
        os.execvp("streamlit", ["streamlit", "run", str(here / "ui" / "streamlit_app.py")])

    mode = args.mode or (menu() if not args.question else "tito")
    if args.question:
        one_shot(args.question, mode)
    else:
        chat_loop(mode)


if __name__ == "__main__":
    main()
