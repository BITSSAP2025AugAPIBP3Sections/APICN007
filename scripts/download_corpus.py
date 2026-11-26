"""Fetch the assignment corpus into data/.

The small PDFs are committed with the assignment repo; the ~171 MB Income-tax
Act 1961 is a GitHub *Release* asset (too big for the git tree). This script
pulls the Act from the release and leaves the rest alone.

    python scripts/download_corpus.py
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ACT_FILENAME = "Income-tax-Act-1961_2026_2026-06-18_02-47-37_b9326c_en.pdf"
RELEASES_API = "https://api.github.com/repos/BITSSAP2025AugAPIBP3Sections/VoiceBotAssignment/releases"


def find_act_asset_url() -> str | None:
    import json

    try:
        with urllib.request.urlopen(RELEASES_API, timeout=30) as resp:
            releases = json.load(resp)
    except Exception as exc:  # noqa: BLE001
        print(f"Could not query releases: {exc}")
        return None
    for rel in releases:
        for asset in rel.get("assets", []):
            if asset.get("name") == ACT_FILENAME:
                return asset.get("browser_download_url")
    return None


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = DATA_DIR / ACT_FILENAME
    if target.exists():
        print(f"Act already present: {target} ({target.stat().st_size/1e6:.0f} MB)")
        return
    url = find_act_asset_url()
    if not url:
        print(
            "Act release asset not found automatically.\n"
            "Download it manually from:\n"
            "  https://github.com/BITSSAP2025AugAPIBP3Sections/VoiceBotAssignment/releases\n"
            f"and place it at: {target}"
        )
        sys.exit(1)
    print(f"Downloading Act (~171 MB) from {url} ...")
    urllib.request.urlretrieve(url, target)
    print(f"Saved {target} ({target.stat().st_size/1e6:.0f} MB). Now run: python src/rag/ingest.py")


if __name__ == "__main__":
    main()
