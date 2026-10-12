from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.clean_reviews import clean_reviews
from src.classify_reviews import classify_reviews
from src.analytics import rating_summary, monthly_trend, category_summary, low_star_share, version_summary, version_category_matrix
from src.prioritization import prioritize_categories
from src.report_export import build_summary_report
from src.auto_fetch import try_live_fetch, save_rows, freshness_label, get_store_meta, APP_ID, COLLECTED

st.set_page_config(page_title="MoveInSync Review Intelligence", page_icon=":bus:", layout="wide")

BRAND = "#0E7C6B"
BRAND_DARK = "#0B2B26"
ACCENT = "#FF6B35"

CAT_ICON = {
    "Booking / scheduling": "Cal",
    "GPS / tracking / ETA": "GPS",
    "Notifications / reminders": "Bell",
    "Login / crash / performance": "Key",
    "Check-in / no-show": "Tick",
    "Driver / transport operations": "Bus",
    "Support / account": "Help",
    "Other / unclear": "Box",
}

def cat_label(c):
    return f"[{CAT_ICON.get(c, '-')}] {c}"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.stApp { background: #F4F7F6; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E3ECEA; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 { color: #0B2B26 !important; }
.hero { background: linear-gradient(135deg, #0B2B26 0%, #0E7C6B 60%, #12A48C 100%); border-radius: 18px; padding: 22px 26px; color: white; margin-bottom: 18px; box-shadow: 0 10px 30px rgba(11,43,38,.25); }
.hero h1 { margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -.5px; color: white !important; }
.hero p { margin: 4px 0 0 0; opacity: .85; font-size: 14px; color: white !important; }
.badge { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px; margin-right: 8px; }
.badge-live { background: #22C55E; color: #06281F; }
.badge-cache { background: #FACC15; color: #422006; }
.badge-demo { background: #FDA4AF; color: #4C0519; }
.badge-meta { background: rgba(255,255,255,.18); color: white; border: 1px solid rgba(255,255,255,.35); }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 6px 0 16px 0; }
.kpi { background: #FFFFFF; border-radius: 16px; padding: 16px 18px; border: 1px solid #E3ECEA; box-shadow: 0 4px 14px rgba(11,43,38,.06); }
.kpi .top { font-size: 12px; font-weight: 700; color: #63746F; text-transform: uppercase; letter-spacing: .6px; }
.kpi .val { font-size: 30px; font-weight: 800; color: #0B2B26; margin: 6px 0 2px 0; }
.kpi .sub { font-size: 13px; color: #63746F; }
.card { background: #FFFFFF; border-radius: 16px; padding: 18px; border: 1px solid #E3ECEA; box-shadow: 0 4px 14px rgba(11,43,38,.06); margin-bottom: 14px; }
.card h3 { margin: 0 0 10px 0; font-size: 16px; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background: white; border-radius: 999px; padding: 8px 16px; border: 1px solid #E3ECEA; font-weight: 600; }
.stTabs [aria-selected="true"] { background: #0B2B26 !important; color: white !important; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## :bus: MoveInSync")
    st.caption("Review Intelligence")
    st.divider()
    st.markdown("#### Data")
    auto_live = st.toggle("Auto-fetch live Play data", value=True)
    fetch_count = st.slider("Reviews per fetch", 200, 1000, 600, 50)
    col_a, col_b = st.columns(2)
    with col_a:
        lang = st.selectbox("Language", ["en"], index=0)
    with col_b:
        country = st.selectbox("Country", ["in", "us"], index=0)
    refresh = st.button("Refresh live now", use_container_width=True)
    st.divider()
    uploaded = st.file_uploader("Upload review CSV", type=["csv"])
    with st.expander("Priority weights"):
        fw = st.slider("Frequency", 0.0, 1.0, 0.40, 0.05)
        sw = st.slider("Severity", 0.0, 1.0, 0.35, 0.05)
        cw = st.slider("Confidence", 0.0, 1.0, 0.25, 0.05)
    st.divider()
    st.markdown("#### Store baseline")
    store_score_in = st.number_input("Store rating", 1.0, 5.0, 4.6, 0.1)
    store_total_in = st.number_input("Store total ratings", 0, 10000000, 114880, 1000)

@st.cache_data(ttl=6 * 3600, show_spinner="Fetching live Google Play reviews...")
def cached_live_fetch(count, lang, country):
    rows, err = try_live_fetch(APP_ID, count=count, lang=lang, country=country)
    return rows, err

def resolve_data():
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            return df, "upload", "Uploaded file"
        except Exception as exc:
            st.error(f"Could not read upload: {exc}")
            st.stop()
    if auto_live or refresh:
        with st.spinner("Contacting Google Play..."):
            rows, err = cached_live_fetch(fetch_count, lang, country)
        if rows:
            try:
                save_rows(rows)
            except Exception:
                pass
            return pd.DataFrame(rows), "live", f"{len(rows)} fresh reviews"
        st.warning(f"Live fetch failed ({err}). Using cached file.")
    if COLLECTED.exists():
        try:
            df = pd.read_csv(COLLECTED)
            return df, "cache", f"{freshness_label()} | {len(df)} rows"
        except Exception as exc:
            st.error(f"Cached file unreadable: {exc}")
    st.error("No review data available. Turn on auto-fetch or upload a review CSV.")
    st.stop()

raw, mode, mode_note = resolve_data()

try:
    cleaned, cleaning_log = clean_reviews(raw)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
if cleaned.empty:
    st.warning("No valid rows after cleaning.")
    st.stop()

classified = classify_reviews(cleaned)
weights = {"frequency": fw, "severity": sw, "confidence": cw}
priorities = prioritize_categories(classified, weights=weights)
dataset_label = {"live": "live Google Play", "cache": "data/collected_reviews.csv", "upload": "uploaded CSV"}[mode]

badge_cls = {"live": "badge-live", "cache": "badge-cache", "upload": "badge-cache"}[mode]
badge_txt = {"live": "LIVE PLAY STORE", "cache": "CACHED FILE", "upload": "UPLOADED FILE"}[mode]

st.markdown(f"""
<div class="hero">
<h1>MoveInSync Review Intelligence</h1>
<p>Play-Store review triage for the employee transport app</p>
<div style="margin-top:10px;"><span class="badge {badge_cls}">{badge_txt}</span><span class="badge badge-meta">{mode_note}</span></div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=6 * 3600, show_spinner=False)
def cached_store_meta(lang, country):
    meta, err = get_store_meta(APP_ID, lang=lang, country=country)
    return meta, err

_store_meta, _store_err = cached_store_meta(lang, country)
if _store_meta and _store_meta.get("score"):
    try:
        store_score = float(_store_meta.get("score"))
        store_total = int(_store_meta.get("ratings") or store_total_in)
        store_note = "auto-fetched from Play"
    except Exception:
        store_score, store_total, store_note = float(store_score_in), int(store_total_in), "manual baseline"
else:
    store_score, store_total, store_note = float(store_score_in), int(store_total_in), "manual baseline"

avg = classified["rating"].mean()
low_share = low_star_share(classified)
cats = classified["issue_category"].nunique()
st.markdown(f"""
<div class="kpi-grid">
<div class="kpi"><div class="top">Reviews</div><div class="val">{len(classified):,}</div><div class="sub">After cleaning</div></div>
<div class="kpi"><div class="top">Sample avg</div><div class="val">{avg:.2f} / 5</div><div class="sub">Fetched text reviews</div></div>
<div class="kpi"><div class="top">Store rating</div><div class="val">{store_score:.2f} / 5</div><div class="sub">{store_total:,} lifetime ratings</div></div>
<div class="kpi"><div class="top">1-2 star share</div><div class="val">{low_share:.0%}</div><div class="sub">Triage pool</div></div>
</div>
""", unsafe_allow_html=True)

with st.expander("Why sample average differs from the store rating"):
    st.markdown("Store rating covers all lifetime ratings, including star-only ratings with no text. The dashboard sample covers only written reviews, which skew negative. Report both numbers.")

tabs = st.tabs(["Overview", "Issues", "Versions", "Explorer", "Validation", "Export"])

with tabs[0]:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('<div class="card"><h3>Rating distribution</h3>', unsafe_allow_html=True)
        summary = rating_summary(classified)
        fig = px.bar(summary, x="rating", y="reviews", text="reviews", color="rating", color_continuous_scale=["#FECACA", "#FED7AA", "#FDE68A", "#A7F3D0", "#0E7C6B"])
        fig.update_layout(template="plotly_white", showlegend=False, height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>Average rating by month</h3>', unsafe_allow_html=True)
        trend = monthly_trend(classified)
        if not trend.empty:
            fig = px.line(trend, x="month", y="average_rating", markers=True)
            fig.update_traces(line_color=BRAND, marker_color=ACCENT, line_width=3)
            fig.update_yaxes(range=[1, 5])
            fig.update_layout(template="plotly_white", height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add valid dates to see trend.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>Priority queue</h3>', unsafe_allow_html=True)
    if not priorities.empty:
        show = priorities.copy()
        show["issue"] = show["issue_category"].map(cat_label)
        fig = px.bar(show.sort_values("priority_score"), x="priority_score", y="issue", orientation="h", text="review_count", color="priority_score", color_continuous_scale=["#A7F3D0", "#0E7C6B", "#0B2B26"])
        fig.update_layout(template="plotly_white", height=340, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(priorities[["issue_category", "review_count", "low_star_share", "severity", "confidence", "priority_score", "recommended_action"]], use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="card"><h3>Reviews by issue category</h3>', unsafe_allow_html=True)
    cat = category_summary(classified)
    cat["issue"] = cat["issue_category"].map(cat_label)
    fig = px.bar(cat.sort_values("review_count"), x="review_count", y="issue", orientation="h", text="review_count", color="low_star_share", color_continuous_scale=["#FDE68A", "#FF6B35", "#B91C1C"])
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(cat[["issue_category", "review_count", "average_rating", "low_star_share"]], use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="card"><h3>Version comparison</h3>', unsafe_allow_html=True)
    vsum = version_summary(classified)
    if not vsum.empty:
        fig = px.bar(vsum, x="app_version", y="average_rating", text="review_count", color="average_rating", color_continuous_scale=["#FECACA", "#FDE68A", "#0E7C6B"])
        fig.update_layout(template="plotly_white", height=320, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(vsum, use_container_width=True, hide_index=True)
        st.markdown("**Version x category matrix**")
        st.dataframe(version_category_matrix(classified), use_container_width=True, hide_index=True)
    else:
        st.info("Add an app_version column to compare releases.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="card"><h3>Review explorer</h3>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.2, 1, 1.6])
    cats_list = ["All"] + sorted(classified["issue_category"].dropna().unique().tolist())
    with f1:
        sel = st.selectbox("Issue category", cats_list, format_func=lambda c: "All" if c == "All" else cat_label(c))
    with f2:
        max_r = st.selectbox("Max stars", [5, 4, 3, 2, 1], index=0)
    with f3:
        q = st.text_input("Search text", placeholder="e.g. otp, gps, booking...")
    view = classified.copy()
    if sel != "All":
        view = view[view["issue_category"] == sel]
    view = view[view["rating"] <= max_r]
    if q.strip():
        view = view[view["text"].str.contains(q.strip(), case=False, na=False)]
    st.write(f"**{len(view):,}** matching reviews")
    cols = [c for c in ["date", "rating", "issue_category", "text", "app_version", "source"] if c in view.columns]
    st.dataframe(view[cols], use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="card"><h3>Data quality</h3>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Input rows", f"{cleaning_log.get('input_rows', 0):,}")
    m2.metric("Kept rows", f"{cleaning_log.get('output_rows', 0):,}")
    m3.metric("Duplicates removed", f"{cleaning_log.get('duplicate_rows_removed', 0):,}")
    st.caption("Rule-based categories are triage hypotheses. Read examples in Explorer before acting.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]:
    st.markdown('<div class="card"><h3>Export</h3>', unsafe_allow_html=True)
    st.download_button("Classified reviews (CSV)", classified.to_csv(index=False).encode("utf-8"), "classified_reviews.csv", "text/csv", use_container_width=True)
    report = build_summary_report(classified, priorities, cleaning_log, dataset_label=dataset_label)
    st.download_button("Summary report (Markdown)", report.encode("utf-8"), "analysis_summary.md", "text/markdown", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"MoveInSync Review Intelligence | {mode_note} | Store {store_score:.2f} ({store_note})")
