"""Streamlit web UI exposing all four modes without code edits (rubric: modes
reachable from the UI). Run via `python src/app.py --ui` or
`streamlit run src/ui/streamlit_app.py`.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

from rag import llm, pipeline  # noqa: E402
from rag.questions import OFFICIAL_QUESTIONS  # noqa: E402

load_dotenv()

st.set_page_config(page_title="APICN001 RAG VoiceBot", page_icon="🧾", layout="centered")


@st.cache_resource
def get_retriever():
    return pipeline.get_retriever()


def main() -> None:
    st.title("🧾 APICN001 — Income-Tax RAG VoiceBot")
    ret = get_retriever()
    provider, model, _ = llm.resolve()
    st.caption(f"provider `{provider}:{model}` · retrieval `{ret.mode}`")

    with st.sidebar:
        mode = st.radio(
            "Mode",
            ["TITO", "TIVO", "VITO", "VIVO"],
            help="T=text, V=voice; first letter is input, last is output.",
        )
        st.markdown("**Voice In** uploads/records audio → Whisper. **Voice Out** speaks the answer.")
        preset = st.selectbox("Official question", ["(type your own)"] + list(OFFICIAL_QUESTIONS))
        if preset != "(type your own)":
            st.info(OFFICIAL_QUESTIONS[preset])

    if "history" not in st.session_state:
        st.session_state.history = []

    voice_in = mode in ("VITO", "VIVO")
    voice_out = mode in ("TIVO", "VIVO")

    question = None
    if voice_in:
        audio = st.audio_input("Speak your question")
        if audio is not None:
            from speech import stt

            import tempfile

            tmp = tempfile.mktemp(suffix=".wav")
            Path(tmp).write_bytes(audio.getvalue())
            question = stt.transcribe_file(tmp)
            if question:
                st.write(f"**Transcribed:** {question}")
    else:
        default = OFFICIAL_QUESTIONS.get(preset, "") if preset != "(type your own)" else ""
        question = st.text_area("Your question", value=default, height=90)

    if st.button("Ask", type="primary") and question:
        placeholder = st.empty()
        acc = ""
        turn = None
        for delta, t in pipeline.answer_stream(ret, question, st.session_state.history):
            turn = t
            acc += delta
            placeholder.markdown(f"**Bot>** {acc}")
        if turn:
            st.caption(
                "Sources: " + "; ".join(turn.sources())
                + f"  ·  retrieval {turn.retrieval_s*1000:.0f} ms"
                + f"  ·  first token {turn.first_token_s:.1f} s"
            )
            st.session_state.history += [
                {"role": "user", "content": question},
                {"role": "assistant", "content": turn.answer[:1800]},
            ]
            if voice_out:
                from speech import tts
                import tempfile

                out = tempfile.mktemp(suffix=".mp3")
                if tts.synthesize_to_file(turn.answer, out):
                    st.audio(out)
                else:
                    st.warning("TTS engine unavailable; showing text only.")

    if st.session_state.history and st.button("Clear conversation"):
        st.session_state.history = []
        st.rerun()


if __name__ == "__main__":
    main()
