import csv
from datetime import datetime, timezone
from pathlib import Path

APP_ID = "com.moveinsync.ets"
COLLECTED = Path("data/collected_reviews.csv")

def try_live_fetch(app_id=APP_ID, count=600, lang="en", country="in"):
    try:
        from google_play_scraper import Sort, reviews
    except ImportError:
        return None, "google-play-scraper not installed. Run: pip install google-play-scraper"
    try:
        rows, token = [], None
        while len(rows) < count:
            batch, token = reviews(app_id, lang=lang, country=country, sort=Sort.NEWEST, count=min(200, count - len(rows)), continuation_token=token)
            if not batch:
                break
            rows.extend(batch)
            if token is None:
                break
        out = []
        for r in rows:
            out.append({
                "review_id": r.get("reviewId", ""),
                "rating": r.get("score", ""),
                "date": r.get("at", ""),
                "text": (r.get("content", "") or "").strip(),
                "app_version": r.get("reviewCreatedVersion") or "unknown",
                "source": "Google Play",
                "source_url": f"https://play.google.com/store/apps/details?id={app_id}",
            })
        return out, ""
    except Exception as exc:
        return None, str(exc)

def save_rows(rows, path=COLLECTED):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["review_id", "rating", "date", "text", "app_version", "source", "source_url"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path

def freshness_label(path=COLLECTED):
    p = Path(path)
    if not p.exists():
        return "no cached file"
    age_h = (datetime.now(timezone.utc).timestamp() - p.stat().st_mtime) / 3600
    if age_h < 1:
        return f"updated {int(age_h*60)} min ago"
    if age_h < 24:
        return f"updated {int(age_h)} hr ago"
    return f"updated {int(age_h/24)} days ago"


def get_store_meta(app_id=APP_ID, lang="en", country="in"):
    try:
        from google_play_scraper import app as gapp
        a = gapp(app_id, lang=lang, country=country)
        return {"score": a.get("score"), "ratings": a.get("ratings"), "histogram": a.get("histogram"), "title": a.get("title")}, ""
    except Exception as exc:
        return None, str(exc)[:300]
