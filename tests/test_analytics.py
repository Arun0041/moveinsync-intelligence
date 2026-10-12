import pandas as pd
from src.analytics import rating_summary, low_star_share, monthly_trend
from src.classify_reviews import classify_reviews

def sample_df():
    raw = pd.DataFrame({
        "rating": [1, 5, 2],
        "date": ["2026-01-01", "2026-01-15", "2026-02-01"],
        "text": ["booking failed", "great app", "GPS not working"],
    })
    return classify_reviews(raw)

def test_rating_summary_contains_all_star_values():
    result = rating_summary(sample_df())
    assert list(result["rating"]) == [1, 2, 3, 4, 5]
    assert result["reviews"].sum() == 3

def test_low_star_share():
    assert low_star_share(sample_df()) == 2 / 3

def test_monthly_trend():
    result = monthly_trend(sample_df())
    assert list(result["month"]) == ["2026-01", "2026-02"]
