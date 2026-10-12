# MoveInSync Review Intelligence

I built this for the FDE case study on the MoveInSync ETS app (com.moveinsync.ets). It pulls real Play Store reviews, groups the low-rated ones into issue categories, and ranks what to fix first.

## Data

I collected 600 written reviews from the Google Play listing (Oct 2026, mostly version 12.19.0) into `data/collected_reviews.csv`, keeping review id, rating, date, text, app version and source URL for traceability. The app also fetches fresh reviews automatically on launch and falls back to this file when offline. One thing worth knowing: the Play header shows ~4.6 because it counts every star-only rating ever given, while my 600 written reviews average 3.77 since unhappy users are the ones who write. Both numbers are shown in the dashboard.

## What I found

Out of 600 reviews, 29% are 1-2 stars. After classifying them, the top actionable groups were:

- Booking / scheduling (31 reviews) - roster and return-trip booking failures, date mismatches
- Driver / transport operations (32) - late pickups, missed cabs, route issues
- GPS / tracking / ETA (26) - stale driver location, wrong ETAs
- Login / crash / performance (25) - app not opening, post-update crashes
- Notifications / reminders (19) - OTP and reminder problems

A large share of reviews are short 5-star notes with no clear issue, which is why Other is the biggest bucket. Those were left out of the priority ranking.

## How to run

```bash
git clone https://github.com/Arun0041/moveinsync-intelligence.git
cd moveinsync-intelligence
python -m venv .venv
```

Activate it (Windows: `.\.venv\Scripts\Activate.ps1`, macOS/Linux: `source .venv/bin/activate`), then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `python -m pytest -q`

To collect fresh reviews: `python scripts/collect_play_reviews.py --app-id com.moveinsync.ets --count 500 --out data/collected_reviews.csv`

## How it is built

- `app.py` - Streamlit dashboard (overview, issues, versions, explorer, export)
- `src/clean_reviews.py` - dedupe and validation
- `src/classify_reviews.py` - keyword rules, first match wins, all matches kept
- `src/prioritization.py` - priority = 0.40 frequency + 0.35 severity + 0.25 confidence
- `src/auto_fetch.py` - Play Store fetching and caching
- `scripts/collect_play_reviews.py` - one-off collection script

## Limitations

Rule-based labels are only a first pass and will misfire on some reviews. I validated by reading examples per category in the explorer, but a manual labelled sample would make the precision numbers solid. Reviews alone also cannot prove root cause - crash logs and trip data would be needed to confirm.
