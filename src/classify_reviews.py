import re
import pandas as pd

RULES = [
    ("Booking / scheduling", [
        r"\bbook(?:ing|ed|s)?\b", r"\breserv(?:e|ation|ed|ing)\b", r"\bschedul(?:e|ing|ed)\b",
        r"\bshift\b", r"\broster\b", r"\bwrong date\b", r"\bdate mismatch\b",
        r"\bcancel(?:lation|led|ed|ling)?\b", r"\bre-?book\b", r"\bslot\b",
        r"\btrip creat\w*\b", r"\bunable to book\b", r"\bbooking fail\w*\b",
    ]),
    ("GPS / tracking / ETA", [
        r"\bgps\b", r"\blocation\b", r"\btrack(?:ing|ed|s)?\b", r"\beta\b",
        r"\bdriver location\b", r"\bmap\b", r"\bnot moving\b", r"\bstale\b",
        r"\bwrong location\b", r"\blive track\w*\b", r"\bvehicle.*not.*show\w*\b",
    ]),
    ("Notifications / reminders", [
        r"\bnotif\w*\b", r"\balert(?:s)?\b", r"\bremind(?:er|ers)?\b",
        r"\bnot notified\b", r"\bmessage delayed\b", r"\botp\b",
        r"\bno.*notif\w*\b", r"\bpush\b", r"\bsms\b",
    ]),
    ("Login / crash / performance", [
        r"\blog\s?in\b", r"\bsign\s?in\b", r"\blogout\b", r"\bcrash(?:es|ed|ing)?\b",
        r"\bfreez(?:e|es|ing|en)\b", r"\bslow\b", r"\berror\b", r"\bserver\b",
        r"\bloading\b", r"\bnot opening\b", r"\bstuck\b", r"\bhang\b",
        r"\bpassword\b.*\breset\b", r"\bauth\w*\b", r"\bupdate.*break\w*\b",
    ]),
    ("Check-in / no-show", [
        r"\bcheck.?in\b", r"\bno.?show\b", r"\battendance\b", r"\bpick.?up missed\b",
        r"\btrip status\b", r"\bboarded\b", r"\bmarked.*absent\b", r"\bqr\b",
    ]),
    ("Driver / transport operations", [
        r"\bdriver\b", r"\bvehicle\b", r"\bcab\b", r"\bbus\b", r"\bshuttle\b",
        r"\bpick.?up\b", r"\bdrop\b", r"\broute\b", r"\blate\b", r"\bwait(?:ed|ing|s)?\b",
        r"\bmissed.*cab\b", r"\bwrong route\b", r"\brash\b", r"\bsafety\b",
        r"\bnever arrived\b", r"\bcancelled.*driver\b",
    ]),
    ("Support / account", [
        r"\bsupport\b", r"\bhelpdesk\b", r"\bcomplaint\b", r"\baccount\b",
        r"\bprofile\b", r"\bresponse\b", r"\brefund\b", r"\bhelp.*number\b",
        r"\bcustomer care\b", r"\bno.*response\b",
    ]),
]

SEVERITY = {
    "Booking / scheduling": 5,
    "GPS / tracking / ETA": 4,
    "Notifications / reminders": 3,
    "Login / crash / performance": 5,
    "Check-in / no-show": 4,
    "Driver / transport operations": 4,
    "Support / account": 2,
    "Other / unclear": 1,
}

def match_all_categories(text):
    text = str(text or "").lower()
    hits = []
    for category, patterns in RULES:
        matched = [p for p in patterns if re.search(p, text)]
        if matched:
            hits.append((category, matched))
    return hits

def classify_text(text):
    hits = match_all_categories(text)
    if not hits:
        return "Other / unclear", 0.35
    primary = hits[0][0]
    confidence = min(0.95, 0.60 + 0.10 * (len(hits) - 1))
    if len(hits[0][1]) >= 2:
        confidence = min(0.95, confidence + 0.05)
    return primary, confidence

def classify_reviews(df: pd.DataFrame):
    result = df.copy()
    pairs = result["text"].apply(classify_text)
    result["issue_category"] = pairs.apply(lambda pair: pair[0])
    result["classification_confidence"] = pairs.apply(lambda pair: pair[1])
    result["all_matched_categories"] = result["text"].apply(
        lambda t: "; ".join([c for c, _ in match_all_categories(t)]) or "Other / unclear"
    )
    result["matched_keyword_count"] = result["text"].apply(lambda t: len(match_all_categories(t)))
    result["severity"] = result["issue_category"].map(SEVERITY).fillna(1).astype(int)
    result["is_low_star"] = result["rating"].le(2)
    return result
