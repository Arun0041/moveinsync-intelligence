"""Generate deterministic synthetic demo data for the dashboard.

This data is ONLY for exercising the app. It must not be presented
as real MoveInSync customer evidence.
Run: python scripts/generate_demo_data.py
"""
import random
from pathlib import Path
import csv
from datetime import date, timedelta

random.seed(42)
ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "sample_reviews.csv"

TEMPLATES = [
    (1, "Booking / scheduling", [
        "Booking showed the wrong date after I selected my shift",
        "Booking failed after selecting my shift, retry did not help",
        "Booking cancellation did not update after retry",
        "Unable to book return trip for night shift roster",
        "Shift slot missing so I could not create my trip",
    ]),
    (1, "GPS / tracking / ETA", [
        "Driver location is not moving and ETA is incorrect",
        "GPS location appears old and map is not updating",
        "Live tracking froze and showed stale cab position",
        "ETA kept changing from 5 min to 25 min",
    ]),
    (2, "Notifications / reminders", [
        "I did not receive the pickup reminder notification",
        "No OTP SMS arrived so I could not board",
        "Pickup alert came 20 minutes late",
    ]),
    (1, "Login / crash / performance", [
        "Login is slow and the app keeps loading",
        "App crashes when I open tracking",
        "The app froze while loading the booking page",
        "Unable to sign in after password reset",
        "Server error every morning at login time",
    ]),
    (2, "Check-in / no-show", [
        "Check-in failed and trip status marked me as no-show",
        "My check-in was not recorded correctly",
        "Boarded the cab but app still shows not boarded",
    ]),
    (2, "Driver / transport operations", [
        "Driver was late and I waited too long",
        "The bus arrived late and pickup information was confusing",
        "Cab never arrived and no replacement was assigned",
        "Driver took a wrong route and I reached office late",
        "Pickup point changed without informing us",
    ]),
    (3, "Support / account", [
        "Support did not respond to my complaint",
        "I reported an account problem and cannot see support status",
        "Raised a missed-cab issue but got no refund or response",
    ]),
    (5, "Other / unclear", [
        "Works smoothly for my daily commute",
        "Easy to use and pickup details are clear",
        "Generally good for seeing my trip schedule",
        "The app is useful when the cab schedule is correct",
    ]),
]

CATEGORY_WEIGHTS = [0.22, 0.17, 0.10, 0.16, 0.07, 0.18, 0.05, 0.05]
VERSIONS = ["8.1.0", "8.2.0", "8.2.1"]
START = date(2026, 4, 1)
TOTAL = 280

rows = []
cats = [t[1] for t in TEMPLATES]
for i in range(TOTAL):
    idx = random.choices(range(len(TEMPLATES)), weights=CATEGORY_WEIGHTS, k=1)[0]
    base_rating, cat, texts = TEMPLATES[idx]
    jitter = random.choice([-1, 0, 0, 0, 1])
    rating = min(5, max(1, base_rating + jitter))
    if cat == "Other / unclear":
        rating = random.choices([4, 5, 3], weights=[0.45, 0.45, 0.10])[0]
    text = random.choice(texts)
    day_offset = random.randint(0, 190)
    d = (START + timedelta(days=day_offset)).isoformat()
    ver = random.choices(VERSIONS, weights=[0.3, 0.35, 0.35])[0]
    rows.append({
        "review_id": f"demo-{i+1:03d}",
        "rating": rating,
        "date": d,
        "text": text,
        "app_version": ver,
        "source": "synthetic_demo",
        "source_url": "",
    })

rows.sort(key=lambda r: r["date"])
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["review_id", "rating", "date", "text", "app_version", "source", "source_url"])
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {OUT}")
