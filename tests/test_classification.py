import pandas as pd
from src.classify_reviews import classify_text, classify_reviews
from src.clean_reviews import clean_reviews

def test_booking_classification():
    category, confidence = classify_text("Booking showed the wrong date")
    assert category == "Booking / scheduling"
    assert 0 <= confidence <= 1

def test_gps_classification():
    category, _ = classify_text("GPS location and ETA are incorrect")
    assert category == "GPS / tracking / ETA"

def test_unknown_classification():
    category, _ = classify_text("I like the colour")
    assert category == "Other / unclear"

def test_cleaning_removes_invalid_and_duplicates():
    raw = pd.DataFrame([
        {"rating": 5, "date": "2026-01-01", "text": "Nice", "review_id": "a"},
        {"rating": 5, "date": "2026-01-01", "text": "Nice", "review_id": "a"},
        {"rating": 8, "date": "2026-01-02", "text": "Bad", "review_id": "b"},
    ])
    cleaned, log = clean_reviews(raw)
    assert len(cleaned) == 1
    assert log["invalid_rating_rows_removed"] == 1
    assert log["duplicate_rows_removed"] == 1
