# Data collection - getting public Play Store reviews responsibly

## What to collect (minimum)
`review_id, rating, date, text, app_version, source, source_url`
Example: `abc123, 1, 2026-09-01, "Booking failed after selecting my shift", 8.2.1, Google Play, https://play.google.com/...`

## Option A - Manual (recommended for submission accuracy)
1. Open the official MoveInSync app listing on Google Play.
2. Copy 200-500 recent reviews across star levels with date, rating, text, app version if shown.
3. Paste into this header and save as `data/collected_reviews.csv`.
4. Keep the Play Store URL in `source_url` where permitted; never invent URLs.
5. Note collection date and listing URL in your submission.

## Option B - Assisted script
1. Check Play Store terms and applicable rules first.
2. `pip install google-play-scraper`
3. `python scripts/collect_play_reviews.py --app-id com.moveinsync.mis --count 500 --out data/collected_reviews.csv`
4. Verify the app ID matches the official listing before running.
5. Open the CSV, remove duplicates, confirm dates/versions, then upload in the dashboard.

## Quality checks before analysis
- Deduplicate by `review_id`, then by `rating+date+text`.
- Drop rows with missing text or out-of-range ratings (the app logs these).
- Keep unparseable dates visible in the audit; fix or exclude explicitly.
- Record coverage: date range, versions, total rows, any filters applied.

## What NOT to do
- Do not scrape at high volume, bypass controls, or collect personal data beyond the public review.
- Do not present `data/sample_reviews.csv` as real evidence; it is synthetic (`source=synthetic_demo`).
