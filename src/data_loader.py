import pandas as pd

REQUIRED_COLUMNS = {"rating", "date", "text"}

def load_reviews(path_or_buffer):
    """Read a CSV and validate the minimum required columns."""
    df = pd.read_csv(path_or_buffer)
    missing = REQUIRED_COLUMNS - set(df.columns.str.lower())
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df
