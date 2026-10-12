import pandas as pd

def precision_recall_per_category(manual: pd.DataFrame, predicted_col="issue_category", truth_col="manual_category"):
    cats = sorted(set(manual[truth_col].dropna().unique()) | set(manual[predicted_col].dropna().unique()))
    rows = []
    for cat in cats:
        tp = int(((manual[truth_col] == cat) & (manual[predicted_col] == cat)).sum())
        fp = int(((manual[truth_col] != cat) & (manual[predicted_col] == cat)).sum())
        fn = int(((manual[truth_col] == cat) & (manual[predicted_col] != cat)).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        rows.append({
            "issue_category": cat,
            "true_count": int((manual[truth_col] == cat).sum()),
            "predicted_count": int((manual[predicted_col] == cat).sum()),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
        })
    return pd.DataFrame(rows).sort_values("true_count", ascending=False).reset_index(drop=True)

def overall_accuracy(manual: pd.DataFrame, predicted_col="issue_category", truth_col="manual_category"):
    if manual.empty:
        return 0.0
    return float((manual[predicted_col] == manual[truth_col]).mean())
