"""Provider switch for the answer generator, selected purely from ``.env``.

Supported ``LLM_PROVIDER`` values: slm | groq | openai | anthropic | openrouter.
All but Anthropic share one OpenAI-compatible code path (base URL + bearer key);
Anthropic uses its Messages API. Both a streaming and a blocking entry point are
provided — streaming is what makes TITO time-to-first-token small and lets voice
modes speak the first sentence while the rest is still generating.
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterator

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URLS = {
    "slm": os.getenv("SLM_BASE_URL", "http://localhost:11434/v1"),
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "anthropic": "https://api.anthropic.com/v1",
}

_DEFAULT_MODEL = {
    "slm": "llama3.1:8b",
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
    "openrouter": "meta-llama/llama-3.1-8b-instruct",
}

_KEY_ENV = {
    "slm": "SLM_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

SYSTEM_PROMPT = (
    "You are an Indian Income-Tax assistant answering questions for a student "
    "assignment, grounded in a fixed corpus (the Income-tax Act 1961 as amended "
    "to 2026, Union Budget speeches FY2022-23 to FY2025-26, and CBDT FAQs).\n"
    "Rules:\n"
    "1. Answer ONLY from the provided context. If the context does not support an "
    "answer, say: 'I could not find this in the corpus.' Do not invent figures.\n"
    "2. Cite the source document name (and page) for each key claim, e.g. "
    "(bs2024_25.pdf, p.12).\n"
    "3. For computations, show the working step by step and state any assumption "
    "(regime, assessment year, indexation) explicitly.\n"
    "4. When the question pins a financial year, use that year's provisions.\n"
    "5. Be concise and factual; this answer may be read aloud by a voice bot."
)


def resolve() -> tuple[str, str, str]:
    """Return (provider, model, api_key) from the environment."""
    provider = os.getenv("LLM_PROVIDER", "slm").strip().lower()
    if provider not in BASE_URLS:
        raise SystemExit(f"LLM_PROVIDER={provider!r} not in {sorted(BASE_URLS)}")
    model = os.getenv("LLM_MODEL") or _DEFAULT_MODEL[provider]
    api_key = os.getenv(_KEY_ENV[provider], "") or ("ollama" if provider == "slm" else "")
    return provider, model, api_key


def _build_messages(question: str, context: str, history: list[dict] | None) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages += history
    messages.append(
        {"role": "user", "content": f"Context from corpus:\n{context}\n\nQuestion: {question}"}
    )
    return messages


# ---- OpenAI-compatible (slm / groq / openai / openrouter) ----
def _oai_stream(base, key, model, messages, max_tokens, temperature) -> Iterator[str]:
    with requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        },
        stream=True,
        timeout=180,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line or not line.startswith(b"data: "):
                continue
            payload = line[6:]
            if payload.strip() == b"[DONE]":
                break
            try:
                delta = json.loads(payload)["choices"][0]["delta"].get("content")
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            if delta:
                yield delta


# ---- Anthropic Messages API ----
def _anthropic_stream(key, model, messages, max_tokens, temperature) -> Iterator[str]:
    system_text = "\n".join(m["content"] for m in messages if m["role"] == "system")
    chat_msgs = [m for m in messages if m["role"] != "system"]
    with requests.post(
        f"{BASE_URLS['anthropic']}/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
        json={
            "model": model,
            "system": system_text,
            "messages": chat_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        },
        stream=True,
        timeout=180,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line or not line.startswith(b"data: "):
                continue
            try:
                event = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            if event.get("type") == "content_block_delta":
                piece = event.get("delta", {}).get("text")
                if piece:
                    yield piece


def chat_stream(
    question: str,
    context: str,
    history: list[dict] | None = None,
    max_tokens: int = 800,
    temperature: float = 0.2,
) -> Iterator[str]:
    """Yield answer text incrementally."""
    provider, model, key = resolve()
    messages = _build_messages(question, context, history)
    if provider == "anthropic":
        yield from _anthropic_stream(key, model, messages, max_tokens, temperature)
    else:
        yield from _oai_stream(BASE_URLS[provider], key or "ollama", model, messages, max_tokens, temperature)


def chat(
    question: str,
    context: str,
    history: list[dict] | None = None,
    max_tokens: int = 800,
    temperature: float = 0.2,
) -> str:
    """Blocking convenience wrapper over :func:`chat_stream`."""
    return "".join(chat_stream(question, context, history, max_tokens, temperature))


if __name__ == "__main__":
    prov, mdl, _ = resolve()
    print(f"provider={prov} model={mdl} base={BASE_URLS[prov]}")
