# MoveInSync Review Intelligence

Live Play-Store review triage for the MoveInSync ETS employee transport app (`com.moveinsync.ets`). The dashboard fetches real reviews on launch, labels low-rated feedback with transparent rules, ranks fix priorities, and exports submission-ready results.

## How data loading works

1. **Live fetch (default):** on launch the app pulls the newest text reviews from Google Play via `google-play-scraper` and caches them to `data/collected_reviews.csv`. Sidebar toggle: Auto-fetch live Play data. Button: Refresh live now.
2. **Upload override:** any CSV uploaded in the sidebar takes precedence over live data.
3. **Cached fallback:** if live fetch fails (offline, blocked network), the app loads `data/collected_reviews.csv` and shows a CACHED badge with file freshness.
4. **No-data guard:** if live fetch fails and no cache exists, the app stops with an upload prompt instead of showing demo data.

## Store rating vs dashboard average

The Play listing shows ~4.6 across 114,880+ lifetime ratings, including star-only ratings with no text. The dashboard dataset (e.g. 600 newest written reviews from `data/collected_reviews.csv`) averages lower (~3.7) because unhappy users write more and the scraper cannot return silent star-only ratings. The dashboard shows both numbers side by side: Store rating KPI plus Sample avg KPI, with the sidebar Store baseline inputs (defaults 4.6 / 114880) auto-overridden when the live listing lookup succeeds. Report both numbers in your submission.

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the printed local URL (usually `http://localhost:8501`).

## Manual collection (optional)

```powershell
python scripts/collect_play_reviews.py --app-id com.moveinsync.ets --count 500 --out data/collected_reviews.csv
```

Then upload `data/collected_reviews.csv` in the sidebar or turn auto-fetch off. See `docs/DATA_COLLECTION.md` for responsible-collection notes.

## Review CSV format

Required: `rating` (1-5), `date` (ISO recommended), `text`.
Optional: `review_id`, `app_version`, `source`, `source_url`.

## Run tests

```powershell
python -m pytest -q
```

## How it works

Classifier (`src/classify_reviews.py`) uses ordered keyword rules: Booking > GPS > Notifications > Login/crash > Check-in > Driver/ops > Support > Other. Primary category is first match; all matches kept in `all_matched_categories`. Priority default is `0.40 x frequency + 0.35 x severity + 0.25 x confidence`, editable in the sidebar. Severity is a proposed rubric, not company priority. Safety issues escalate separately.

## Structure

```text
app.py
src/clean_reviews.py, classify_reviews.py, analytics.py, prioritization.py, report_export.py, validation.py, auto_fetch.py
scripts/collect_play_reviews.py, generate_demo_data.py
data/collected_reviews.csv (real Play cache)
.streamlit/config.toml
docs/, tests/, assets/
```

## Deploy (Streamlit Cloud)

1. Push to GitHub (do NOT upload `.venv`, `__pycache__`, `.pytest_cache`).
2. On share.streamlit.io create a New app, select the repo, main file `app.py`.
3. Deploy. Live fetch runs on launch; the bundled `data/collected_reviews.csv` covers offline starts.

## Limitations

- No internal telemetry included; reviews alone do not prove root cause.
- Rule labels are triage hypotheses; validate by reading examples in Explorer.
- Public reviews are self-selected and may be outdated or duplicated.
