# Review Intelligence Summary

Generated: 2026-10-12 22:53
Dataset: synthetic demo

> Interpret this report only in the context of the uploaded dataset. Rule-based categories are triage signals, not verified root causes.

## Dataset overview
- Reviews analysed: 280
- Average rating: 1.73/5
- 1-2 star share: 81.8%

## Cleaning audit
- Input rows: 280
- Output rows: 280
- Invalid rating rows removed: 0
- Empty text rows removed: 0
- Duplicate rows removed: 0
- Rows with unparseable date: 0
- Missing source url rows: 280

## Priority ranking

| Category | Reviews | Low-star share | Priority score | Recommended next action |
|---|---:|---:|---:|---|
| Booking / scheduling | 78 | 93.6% | 62.6 | Verify booking state transitions, date/shift handling, cancellation and retry behaviour; add regression tests. |
| Login / crash / performance | 20 | 100.0% | 54.1 | Segment crashes and auth/API errors by app version and device; fix highest-impact release regressions. |
| GPS / tracking / ETA | 56 | 100.0% | 53.6 | Measure location freshness and ETA error; show last-updated time and avoid presenting stale data as live. |
| Driver / transport operations | 63 | 65.1% | 53.2 | Separate app defects from transport execution using trip event timestamps and operational incident records. |
| Check-in / no-show | 19 | 78.9% | 46.9 | Audit check-in event reliability, reminders and dispute/recovery flows with operations. |
| Notifications / reminders | 32 | 62.5% | 42.7 | Instrument send/delivery/open events and test reminder timing, permissions and fallback paths. |
| Support / account | 9 | 44.4% | 31.5 | Improve help entry points, issue categories, ticket status and support response visibility. |
| Other / unclear | 3 | 0.0% | 16.2 | Manually review examples and refine taxonomy before prioritising. |

## Interpretation and next steps
1. Review representative examples in each high-priority category.
2. Manually label a stratified sample (at least 30 per top category) and measure precision/recall.
3. Compare review signals with internal telemetry, support tickets and operational events.
4. Ship a small fix only after the responsible team validates the underlying failure mode.
5. Repeat the analysis after each release and monitor both rating outcomes and product reliability metrics.

## Limitations
Reviews are self-selected and may not represent all users. Text classification can be wrong. Correlation does not establish causation. Do not present synthetic demo data as actual customer evidence.