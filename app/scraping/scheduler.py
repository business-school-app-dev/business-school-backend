# Cross-platform (Mac/Windows/Linux) daily job runner
# - Runs the scraper immediately, then every 24 hours
# - Enriches events.json -> events_enriched.json with time_updated + id
#
# Requires: your scraper writes events.json in the same folder.

from __future__ import annotations
import json
import hashlib
import uuid
import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

# ---- CONFIG ----
# If your file is named differently, change this:
SCRAPER_FILE = "scraper.py"   
RAW_JSON = Path("events.json")
ENRICHED_JSON = Path("events_enriched.json")
INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours


def stable_event_id(url: str | None, title: str, date: str) -> str:
    """
    Deterministic ID per event across runs:
      - Prefer UUID5 based on URL (stable, unique)
      - If URL missing, hash(title|date) for a short ID
    """
    if url:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
    h = hashlib.sha1(f"{title}|{date}".encode("utf-8")).hexdigest()
    return f"sha1-{h[:12]}"


def run_scraper(scraper_file: str = SCRAPER_FILE) -> None:
    """Call the scraper using the current Python interpreter (blocking)."""
    print(f"\n▶ Running scraper: {scraper_file}")
    cmd = [sys.executable, scraper_file]
    subprocess.run(cmd, check=True)  # waits until scraper fully finishes
    print("Scraper finished.")


def enrich_json(raw_path: Path = RAW_JSON, out_path: Path = ENRICHED_JSON) -> None:
    """Load events.json, add time_updated + id, write events_enriched.json."""
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} not found. Did the scraper run?")

    print(f"Loading {raw_path} …")
    with raw_path.open("r", encoding="utf-8") as f:
        events = json.load(f)

    # ISO 8601 UTC timestamp
    now_iso = datetime.now(timezone.utc).isoformat()
    print(f"time_updated = {now_iso}")

    enriched = []
    for ev in events:
        title = (ev.get("title") or "").strip()
        date = (ev.get("date") or "").strip()
        url = (ev.get("url") or "").strip() or None

        ev_out = dict(ev)
        ev_out["time_updated"] = now_iso
        ev_out["id"] = stable_event_id(url, title, date)
        enriched.append(ev_out)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"📤 Wrote {len(enriched)} events to {out_path.resolve()}")


def run_once():
    """One full cycle: scrape -> enrich."""
    try:
        run_scraper()
        enrich_json()

        print("▶ Ingesting events into Postgres...")
        cmd = [sys.executable, "ingest_events.py"]
        subprocess.run(cmd, check=True)
        
        print("Ingestion complete.")

        print("Job complete (scrape + enrich + ingest).")
    except subprocess.CalledProcessError as e:
        print(f"Scraper or ingest failed (exit code {e.returncode}).")
    except Exception as e:
        print(f"Enrichment or ingestion failed: {e}")


def main():
    """Run immediately, then every 24h."""
    os.chdir(Path(__file__).parent.resolve())

    # Run immediately
    start = time.monotonic()
    run_once()

    # Then repeat every 24h (monotonic avoids drift)
    while True:
        next_run_at = start + INTERVAL_SECONDS
        sleep_s = max(0.0, next_run_at - time.monotonic())
        try:
            print(f"Sleeping for {int(sleep_s)} seconds (~24h)…")
            time.sleep(sleep_s)
        except KeyboardInterrupt:
            print("\nStopping scheduler.")
            break
        start = next_run_at
        run_once()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
