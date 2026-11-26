"""Speech-to-text. Local faster-whisper by default; Groq / OpenAI Whisper via
``.env``. Recording is press-Enter-to-start, press-Enter-to-stop (press-to-talk),
which needs no VAD and works over SSH/terminals.
"""
from __future__ import annotations

import os
import queue
import tempfile
import threading
import time

from dotenv import load_dotenv

load_dotenv()

_whisper_model = None  # cache across turns so the model loads once


def record_to_wav(max_seconds: float | None = None) -> str | None:
    """Capture mic audio to a 16 kHz mono WAV. Returns the path, or None if the
    audio stack is missing."""
    try:
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("Voice in needs: pip install sounddevice soundfile faster-whisper")
        return None

    sr = 16_000
    audio_q: queue.Queue = queue.Queue()
    running = {"on": True}

    def callback(indata, frames, time_info, status):  # noqa: ANN001
        if running["on"]:
            audio_q.put(indata.copy())

    print("  REC> press Enter to start speaking...")
    input()
    with sd.InputStream(samplerate=sr, channels=1, dtype="int16", callback=callback):
        def stopper():
            input("  REC> speaking... press Enter to stop.\n")
            running["on"] = False

        t = threading.Thread(target=stopper, daemon=True)
        t.start()
        start = time.time()
        frames = []
        while running["on"]:
            try:
                frames.append(audio_q.get(timeout=0.2))
            except queue.Empty:
                pass
            if max_seconds and time.time() - start > max_seconds:
                running["on"] = False

    if not frames:
        return None
    audio = np.concatenate(frames, axis=0)
    path = tempfile.mktemp(suffix=".wav")
    sf.write(path, audio, sr)
    return path


def _transcribe_cloud(wav_path: str, provider: str) -> str:
    import requests

    url = (
        "https://api.groq.com/openai/v1/audio/transcriptions"
        if provider == "groq"
        else "https://api.openai.com/v1/audio/transcriptions"
    )
    model = "whisper-large-v3-turbo" if provider == "groq" else "whisper-1"
    key_env = "GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"
    with open(wav_path, "rb") as fh:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {os.getenv(key_env, '')}"},
            files={"file": fh},
            data={"model": model},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()["text"].strip()


def _transcribe_local(wav_path: str) -> str:
    global _whisper_model
    from faster_whisper import WhisperModel

    if _whisper_model is None:
        size = os.getenv("STT_MODEL", "base")
        _whisper_model = WhisperModel(size, device="auto", compute_type="auto")
    segments, _info = _whisper_model.transcribe(wav_path, vad_filter=True)
    return " ".join(s.text for s in segments).strip()


def transcribe(wav_path: str | None) -> str | None:
    if not wav_path:
        return None
    provider = os.getenv("STT_PROVIDER", "local").lower()
    t0 = time.time()
    text = _transcribe_cloud(wav_path, provider) if provider in ("groq", "openai") else _transcribe_local(wav_path)
    print(f"  [stt {provider} {time.time()-t0:.1f}s] {text}")
    return text


def transcribe_file(path: str) -> str | None:
    """Transcribe an existing audio file (used by scripts/tests, no mic)."""
    return transcribe(path)
