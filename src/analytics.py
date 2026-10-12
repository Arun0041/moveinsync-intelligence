import pandas as pd

def rating_summary(df):
    counts = df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
    return pd.DataFrame({"rating": counts.index.astype(int), "reviews": counts.values.astype(int)})

def low_star_share(df):
    if df.empty:
        return 0.0
    return float(df["rating"].le(2).mean())

def monthly_trend(df):
    valid = df.copy()
    valid["date"] = pd.to_datetime(valid["date"], errors="coerce", utc=True).dt.tz_convert(None)
    valid = valid.dropna(subset=["date"])
    if valid.empty:
        return pd.DataFrame(columns=["month", "average_rating", "review_count"])
    valid["month"] = valid["date"].dt.to_period("M").astype(str)
    return valid.groupby("month", as_index=False).agg(
        average_rating=("rating", "mean"),
        review_count=("rating", "size"),
    ).sort_values("month")

def category_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["issue_category", "review_count", "average_rating", "low_star_share"])
    return df.groupby("issue_category", as_index=False).agg(
        review_count=("rating", "size"),
        average_rating=("rating", "mean"),
        low_star_share=("is_low_star", "mean"),
    ).sort_values(["review_count", "low_star_share"], ascending=[False, False])

def version_summary(df):
    if df.empty or "app_version" not in df.columns:
        return pd.DataFrame(columns=["app_version", "review_count", "average_rating", "low_star_share"])
    clean = df.copy()
    clean["app_version"] = clean["app_version"].fillna("unknown").astype(str)
    return clean.groupby("app_version", as_index=False).agg(
        review_count=("rating", "size"),
        average_rating=("rating", "mean"),
        low_star_share=("is_low_star", "mean"),
    ).sort_values("app_version")

def version_category_matrix(df):
    if df.empty:
        return pd.DataFrame(columns=["app_version", "issue_category", "review_count", "average_rating"])
    clean = df.copy()
    clean["app_version"] = clean["app_version"].fillna("unknown").astype(str)
    return clean.groupby(["app_version", "issue_category"], as_index=False).agg(
        review_count=("rating", "size"),
        average_rating=("rating", "mean"),
    ).sort_values(["app_version", "review_count"], ascending=[True, False])
