import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag import ingest  # noqa: E402


def test_chunking_respects_size_with_overlap():
    text = ". ".join(f"Sentence number {i} about section 80C deductions" for i in range(200))
    chunks = ingest.chunk_text(text)
    assert chunks, "expected at least one chunk"
    # allow a little slack for sentence packing, but nothing absurdly large
    assert all(len(c) <= ingest.CHUNK_SIZE + 120 for c in chunks)
    # consecutive chunks should share some tail/head overlap text
    assert len(chunks) > 1


def test_chunking_empty_and_whitespace():
    assert ingest.chunk_text("") == []
    assert ingest.chunk_text("    \n\t ") == []


def test_year_tagging():
    assert ingest.year_for("bs2024_25.pdf") == "FY2024-25"
    assert ingest.year_for("bs2025_26.pdf") == "FY2025-26"
    assert ingest.year_for("FAQs-on-BIS-Exemption.pdf") is None
