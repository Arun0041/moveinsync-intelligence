"""Collect public Play Store reviews into the CSV format used by the app.

Preferred: manual collection with source URLs (most reliable for a submission).
Optional automated helper uses `google-play-scraper` if installed:
    pip install google-play-scraper
    python scripts/collect_play_reviews.py --app-id com.moveinsync.ets --count 500 --out data/collected_reviews.csv

You must check Play Store terms, robots, and applicable rules before collecting.
Retain reviewId, date, rating, text, appVersion and review URL for traceability.
"""
import argparse
import csv
from pathlib import Path

APP_ID = "com.moveinsync.ets"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-id", default=APP_ID)
    ap.add_argument("--count", type=int, default=500)
    ap.add_argument("--out", default="data/collected_reviews.csv")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--country", default="in")
    args = ap.parse_args()

    try:
        from google_play_scraper import Sort, reviews
    except ImportError:
        print("google-play-scraper is not installed.")
        print("Install with: pip install google-play-scraper")
        print("Or collect manually using docs/DATA_COLLECTION.md template.")
        raise SystemExit(1)

    all_rows = []
    token = None
    while len(all_rows) < args.count:
        batch, token = reviews(
            args.app_id, lang=args.lang, country=args.country,
            sort=Sort.NEWEST, count=min(200, args.count - len(all_rows)),
            continuation_token=token,
        )
        if not batch:
            break
        all_rows.extend(batch)
        if token is None:
            break

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["review_id", "rating", "date", "text", "app_version", "source", "source_url"])
        w.writeheader()
        for r in all_rows:
            rid = r.get("reviewId", "")
            w.writerow({
                "review_id": rid,
                "rating": r.get("score", ""),
                "date": r.get("at", ""),
                "text": (r.get("content", "") or "").strip(),
                "app_version": r.get("reviewCreatedVersion") or "unknown",
                "source": "Google Play",
                "source_url": f"https://play.google.com/store/apps/details?id={args.app_id}",
            })
    print(f"Wrote {len(all_rows)} rows to {out}")
    print("Verify dates, versions and deduplicate in the app before analysis.")

if __name__ == "__main__":
    main()
