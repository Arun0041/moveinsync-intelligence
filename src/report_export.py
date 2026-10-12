from datetime import datetime

def build_summary_report(df, priorities, cleaning_log, dataset_label="uploaded dataset"):
    lines = [
        "# Review Intelligence Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Dataset: {dataset_label}",
        "",
        "> Interpret this report only in the context of the uploaded dataset. Rule-based categories are triage signals, not verified root causes.",
        "",
        "## Dataset overview",
        f"- Reviews analysed: {len(df)}",
        f"- Average rating: {df['rating'].mean():.2f}/5" if len(df) else "- Average rating: N/A",
        f"- 1-2 star share: {df['rating'].le(2).mean():.1%}" if len(df) else "- 1-2 star share: N/A",
        "",
        "## Cleaning audit",
    ]
    lines += [f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in cleaning_log.items()]
    lines += ["", "## Priority ranking", ""]
    if priorities.empty:
        lines.append("No categories available.")
    else:
        lines += ["| Category | Reviews | Low-star share | Priority score | Recommended next action |",
                  "|---|---:|---:|---:|---|"]
        for _, row in priorities.iterrows():
            action = str(row["recommended_action"]).replace("|", "/")
            lines.append(f"| {row['issue_category']} | {row['review_count']} | {row['low_star_share']:.1%} | {row['priority_score']:.1f} | {action} |")
    lines += [
        "",
        "## Interpretation and next steps",
        "1. Review representative examples in each high-priority category.",
        "2. Manually label a stratified sample (at least 30 per top category) and measure precision/recall.",
        "3. Compare review signals with internal telemetry, support tickets and operational events.",
        "4. Ship a small fix only after the responsible team validates the underlying failure mode.",
        "5. Repeat the analysis after each release and monitor both rating outcomes and product reliability metrics.",
        "",
        "## Limitations",
        "Reviews are self-selected and may not represent all users. Text classification can be wrong. Correlation does not establish causation. Do not present synthetic demo data as actual customer evidence.",
    ]
    return "\n".join(lines)
