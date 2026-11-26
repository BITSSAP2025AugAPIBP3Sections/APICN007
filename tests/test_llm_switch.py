import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag import llm  # noqa: E402
from rag.retriever import detect_year  # noqa: E402


def _set(monkeyenv: dict):
    for k, v in monkeyenv.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_provider_switch_slm_default():
    _set({"LLM_PROVIDER": "slm", "LLM_MODEL": None, "SLM_API_KEY": "ollama"})
    provider, model, key = llm.resolve()
    assert provider == "slm"
    assert model == "llama3.1:8b"
    assert key == "ollama"


def test_provider_switch_groq_with_model_override():
    _set({"LLM_PROVIDER": "groq", "LLM_MODEL": "llama-3.1-8b-instant", "GROQ_API_KEY": "gsk_test"})
    provider, model, key = llm.resolve()
    assert provider == "groq"
    assert model == "llama-3.1-8b-instant"
    assert key == "gsk_test"
    assert llm.BASE_URLS["groq"] == "https://api.groq.com/openai/v1"


def test_all_four_hosted_providers_resolve():
    for prov in ("groq", "openai", "anthropic", "openrouter"):
        _set({"LLM_PROVIDER": prov, "LLM_MODEL": None})
        provider, model, _ = llm.resolve()
        assert provider == prov
        assert model  # a sensible default exists


def test_unknown_provider_raises():
    _set({"LLM_PROVIDER": "nope"})
    try:
        llm.resolve()
    except SystemExit:
        return
    raise AssertionError("expected SystemExit for unknown provider")


def test_detect_year_handles_ay_mapping():
    assert detect_year("slab rates for FY 2024-25") == "FY2024-25"
    assert detect_year("rates for AY 2025-26") == "FY2024-25"
    assert detect_year("what is section 80C") is None
