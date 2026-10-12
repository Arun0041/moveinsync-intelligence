import pandas as pd
from src.classify_reviews import SEVERITY

ACTIONS = {
    "Booking / scheduling": "Verify booking state transitions, date/shift handling, cancellation and retry behaviour; add regression tests.",
    "GPS / tracking / ETA": "Measure location freshness and ETA error; show last-updated time and avoid presenting stale data as live.",
    "Notifications / reminders": "Instrument send/delivery/open events and test reminder timing, permissions and fallback paths.",
    "Login / crash / performance": "Segment crashes and auth/API errors by app version and device; fix highest-impact release regressions.",
    "Check-in / no-show": "Audit check-in event reliability, reminders and dispute/recovery flows with operations.",
    "Driver / transport operations": "Separate app defects from transport execution using trip event timestamps and operational incident records.",
    "Support / account": "Improve help entry points, issue categories, ticket status and support response visibility.",
    "Other / unclear": "Manually review examples and refine taxonomy before prioritising.",
}

def prioritize_categories(df: pd.DataFrame, weights=None):
    weights = weights or {"frequency": 0.40, "severity": 0.35, "confidence": 0.25}
    total = sum(weights.values()) or 1
    weights = {k: v / total for k, v in weights.items()}
    if df.empty:
        return pd.DataFrame(columns=[
            "issue_category", "review_count", "low_star_share", "severity",
            "confidence", "frequency_score", "priority_score", "recommended_action"
        ])
    rows = []
    total_reviews = len(df)
    for category, group in df.groupby("issue_category"):
        frequency_score = 100 * len(group) / total_reviews
        severity = float(SEVERITY.get(category, 1)) * 20
        confidence = float(group["classification_confidence"].mean()) * 100
        low_share = float(group["rating"].le(2).mean())
        # Frequency is the category share; severity and confidence are rubric-based inputs.
        score = (weights["frequency"] * frequency_score +
                 weights["severity"] * severity +
                 weights["confidence"] * confidence)
        rows.append({
            "issue_category": category,
            "review_count": int(len(group)),
            "low_star_share": low_share,
            "severity": severity,
            "confidence": confidence,
            "frequency_score": frequency_score,
            "priority_score": score,
            "recommended_action": ACTIONS.get(category, ACTIONS["Other / unclear"]),
        })
    return pd.DataFrame(rows).sort_values("priority_score", ascending=False).reset_index(drop=True)
