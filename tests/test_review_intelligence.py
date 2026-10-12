import pandas as pd
from src.classify_reviews import classify_text, classify_reviews, match_all_categories
from src.clean_reviews import clean_reviews
from src.analytics import version_summary, version_category_matrix
from src.validation import precision_recall_per_category, overall_accuracy

def test_multi_label_keeps_first_match_as_primary():
    cats = match_all_categories("Booking failed and GPS location is wrong")
    assert "Booking / scheduling" in [c for c, _ in cats]
    assert "GPS / tracking / ETA" in [c for c, _ in cats]
    primary, _ = classify_text("Booking failed and GPS location is wrong")
    assert primary == "Booking / scheduling"

def test_version_summary_groups_correctly():
    raw = pd.DataFrame({
        "rating": [1, 5, 2, 4],
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "text": ["booking failed", "great app", "gps wrong", "late cab"],
        "app_version": ["8.1.0", "8.1.0", "8.2.0", "8.2.0"],
    })
    classified = classify_reviews(raw)
    vsum = version_summary(classified)
    assert set(vsum["app_version"]) == {"8.1.0", "8.2.0"}
    assert vsum["review_count"].sum() == 4

def test_validation_metrics():
    manual = pd.DataFrame({
        "issue_category": ["Booking / scheduling", "GPS / tracking / ETA", "Booking / scheduling"],
        "manual_category": ["Booking / scheduling", "Booking / scheduling", "Booking / scheduling"],
    })
    table = precision_recall_per_category(manual)
    assert "precision" in table.columns
    assert overall_accuracy(manual) == 2 / 3

def test_version_category_matrix():
    raw = pd.DataFrame({
        "rating": [1, 2],
        "date": ["2026-01-01", "2026-01-02"],
        "text": ["booking failed", "gps wrong"],
        "app_version": ["8.1.0", "8.1.0"],
    })
    classified = classify_reviews(raw)
    m = version_category_matrix(classified)
    assert len(m) == 2
