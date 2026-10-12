# Recommendation - What to fix first to raise Play Store ratings

> Status: ILLUSTRATIVE example generated from `data/sample_reviews.csv` (280 synthetic demo rows).
> Do NOT present these numbers as real MoveInSync evidence.
> Re-run the app with a sourced real dataset and replace the tables below.
> Method and ticket structure are the reusable part of this submission.

## TL;DR priority order (default rubric: 0.40 frequency + 0.35 severity + 0.25 confidence)

1. **Booking / scheduling** - 78 reviews (27.9%), avg 1.35, 93.6% low-star, priority 62.6
2. **Login / crash / performance** - 20 reviews (7.1%), avg 1.15, 100% low-star, priority 54.1
3. **GPS / tracking / ETA** - 56 reviews (20.0%), avg 1.14, 100% low-star, priority 53.6
4. **Driver / transport operations** - 63 reviews (22.5%), avg 2.29, 65.1% low-star, priority 53.2
5. **Check-in / no-show** - 19 reviews, avg 2.11, priority 46.9
6. **Notifications / reminders** - 32 reviews, avg 2.22, priority 42.7

Overall demo health: avg 1.73/5, ~82% 1-2 star, flat 1.63-1.93 monthly Apr-Oct 2026.
No version shows a clear regression in demo (8.1.0: 1.75, 8.2.0: 1.70, 8.2.1: 1.75).

## Why this order

- Booking is both most frequent AND severity 5. Self-booking is the primary trip-creation path, so a failure here blocks everything downstream.
- Login/crash is infrequent but severity 5 with 100% low-star. A crash on open or sign-in guarantees a 1-star review.
- GPS and Driver/ops look similar in volume, but GPS is 100% low-star while Driver/ops mixes app defects with operational execution. Separate them before staffing.
- Safety note: any safety-tagged review must escalate immediately regardless of priority score.

## P1 tickets (start tomorrow)

### T1 - Booking state and shift-date handling
- Evidence: `issue_category == Booking / scheduling`, filter rating <= 2 in Review explorer. Examples: wrong date after shift select, retry does not help, cancellation not updating.
- Owner: App + rostering/backend. Support: operations.
- Fix: single source of truth for shift/date/slot, idempotent retry, explicit booking-confirmed vs pending states, cancellation propagation test.
- Acceptance: reproduce all three demo failure texts on a test build, then confirm correct date/slot after retry and after cancel.
- Metric: booking-failure review share + booking success rate by version; target rating lift in Booking cohort.

### T2 - Crash and login regression triage
- Evidence: `Login / crash / performance`, 100% low-star. Examples: freeze on booking page, crash on tracking open, sign-in after password reset, morning server error.
- Owner: Mobile + backend/auth.
- Fix: segment crashes and auth/API errors by version/device/OS, fix top 2 stacks, add login retry and clear error copy.
- Acceptance: zero repro of listed crash texts on latest version, login success logged.
- Metric: crash-free sessions, login error rate, related 1-star share.

### T3 - Live tracking freshness
- Evidence: `GPS / tracking / ETA`. Examples: location not moving, stale map, ETA swinging 5 to 25 min.
- Owner: Mobile + location pipeline.
- Fix: measure location age, show last-updated time, never present stale data as live, ETA confidence band.
- Acceptance: stale feed shows explicit stale state, ETA error logged.
- Metric: ETA error, stale-feed rate, GPS-category low-star share.

### T4 - Separate app vs operations for driver/late issues
- Evidence: `Driver / transport operations`. Requires trip-event timestamps + incident records to split.
- Owner: Operations + product, with app logging support.
- Fix: join reviews to trip events (assigned, arrived, no-show) before assigning blame.
- Acceptance: every late/no-arrival review mapped to app-gap or ops-gap.
- Metric: on-time pickup rate vs app-attributed late rate.

## Next 2 weeks
- Check-in/no-show audit with operations (dispute/recovery flow).
- Notification instrumentation: send/delivery/open, permission and fallback paths.
- Support entry-point cleanup (visible ticket status).

## How to re-run with real data
1. Collect per `docs/DATA_COLLECTION.md` (keep reviewId, date, rating, text, appVersion, source URL).
2. `streamlit run app.py`, upload CSV, check Data quality audit.
3. Read 10-15 examples per top category, adjust weights in sidebar if needed.
4. Export CSV + Markdown, paste real tables over the illustrative ones above.
