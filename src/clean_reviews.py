import pandas as pd

REQUIRED_COLUMNS = {"rating", "date", "text"}

def clean_reviews(raw: pd.DataFrame):
    df = raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

    before = len(df)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    invalid_rating = int((~df["rating"].between(1, 5)).sum())
    df = df[df["rating"].between(1, 5)].copy()
    df["rating"] = df["rating"].astype(int)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_convert(None)
    df["text"] = df["text"].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    empty_text = int(df["text"].eq("").sum())
    df = df[df["text"].ne("")].copy()
    df["text_length"] = df["text"].str.len()

    if "review_id" in df.columns:
        df["review_id"] = df["review_id"].astype(str).str.strip()
        dup_mask = df["review_id"].ne("") & df["review_id"].ne("nan") & df["review_id"].duplicated(keep="first")
        duplicate_count = int(dup_mask.sum())
        df = df[~dup_mask].copy()
    else:
        duplicate_count = int(df.duplicated(subset=["rating", "date", "text"], keep="first").sum())
        df = df.drop_duplicates(subset=["rating", "date", "text"], keep="first").copy()

    for col, default in [("source", "unspecified"), ("source_url", ""), ("app_version", "unknown")]:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default).astype(str).str.strip()
            df[col] = df[col].replace("", default)

    df = df.sort_values("date", na_position="last").reset_index(drop=True)
    log = {
        "input_rows": int(before),
        "output_rows": int(len(df)),
        "invalid_rating_rows_removed": invalid_rating,
        "empty_text_rows_removed": empty_text,
        "duplicate_rows_removed": duplicate_count,
        "rows_with_unparseable_date": int(df["date"].isna().sum()),
        "missing_source_url_rows": int(df["source_url"].astype(str).str.strip().eq("").sum()
                                        + (df["source_url"] == "unspecified").sum()),
    }
    return df, log
