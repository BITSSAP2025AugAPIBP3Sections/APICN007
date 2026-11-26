"""Text-to-speech with sentence-wise streaming so the first words are spoken
while the rest of the answer is still being generated (the main latency lever
for TIVO/VIVO).

Engines (``TTS_PROVIDER``): pyttsx3 (offline, default, works on macOS SAPI/NSSS),
edge (Microsoft Edge neural voices, cloud), piper (offline neural, CLI).
"""
from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable, Iterator

from dotenv import load_dotenv

load_dotenv()

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
# Strip inline citations like "(bs2024_25.pdf, p.12)" before speaking — they are
# shown on screen but sound clumsy read aloud.
_CITE = re.compile(r"\((?:[\w\-&]+\.pdf)[^)]*\)")


def _clean(text: str) -> str:
    return _CITE.sub("", text).replace("  ", " ").strip()


# ---- engines: each speaks one ready chunk ----
def _speak_pyttsx3(text: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    if os.getenv("TTS_VOICE"):
        engine.setProperty("voice", os.getenv("TTS_VOICE"))
    engine.setProperty("rate", int(os.getenv("TTS_RATE", 185)))
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def _speak_edge(text: str) -> None:
    import asyncio

    import edge_tts

    voice = os.getenv("TTS_VOICE", "en-IN-NeerjaNeural")

    async def run() -> None:
        import tempfile

        out = tempfile.mktemp(suffix=".mp3")
        await edge_tts.Communicate(text, voice).save(out)
        _play_file(out)

    asyncio.run(run())


def _speak_piper(text: str) -> None:
    model = os.getenv("TTS_VOICE", "")
    import tempfile

    out = tempfile.mktemp(suffix=".wav")
    subprocess.run(["piper", "--model", model, "--output_file", out], input=text.encode(), check=False)
    _play_file(out)


def _play_file(path: str) -> None:
    for player in (["afplay", path], ["ffplay", "-nodisp", "-autoexit", path], ["aplay", path]):
        try:
            subprocess.run(player, check=False, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            continue


def _engine():
    provider = os.getenv("TTS_PROVIDER", "pyttsx3").lower()
    return {"pyttsx3": _speak_pyttsx3, "edge": _speak_edge, "piper": _speak_piper}.get(
        provider, _speak_pyttsx3
    )


def speak(text: str) -> None:
    """Speak a complete answer (used by TIVO one-shot)."""
    cleaned = _clean(text)
    if cleaned:
        _engine()(cleaned)


def speak_stream(deltas: Iterable[str]) -> Iterator[str]:
    """Consume a stream of text deltas; speak each complete sentence as soon as
    it is available. Re-yields the deltas so the caller can also print them."""
    engine = _engine()
    buffer = ""
    for delta in deltas:
        buffer += delta
        yield delta
        while True:
            match = _SENT_SPLIT.search(buffer)
            if not match:
                break
            sentence, buffer = buffer[: match.start() + 1], buffer[match.end() :]
            cleaned = _clean(sentence)
            if cleaned:
                engine(cleaned)
    tail = _clean(buffer)
    if tail:
        engine(tail)


def synthesize_to_file(text: str, out_path: str) -> str | None:
    """Best-effort render of text to an audio file (used by scripts/make_demos).
    Returns the path on success, else None."""
    provider = os.getenv("TTS_PROVIDER", "pyttsx3").lower()
    cleaned = _clean(text)
    try:
        if provider == "edge":
            import asyncio

            import edge_tts

            asyncio.run(
                edge_tts.Communicate(cleaned, os.getenv("TTS_VOICE", "en-IN-NeerjaNeural")).save(out_path)
            )
        elif provider == "piper":
            subprocess.run(
                ["piper", "--model", os.getenv("TTS_VOICE", ""), "--output_file", out_path],
                input=cleaned.encode(),
                check=True,
            )
        else:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", int(os.getenv("TTS_RATE", 185)))
            engine.save_to_file(cleaned, out_path)
            engine.runAndWait()
            engine.stop()
        return out_path if os.path.exists(out_path) else None
    except Exception as exc:  # noqa: BLE001
        print(f"[tts] synthesize_to_file failed: {exc}")
        return None
