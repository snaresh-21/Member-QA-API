# qa_logic.py
import re, json, requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# -------------------- Regex Setup --------------------
NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?)\b",
    re.I
)

# -------------------- Intent Detection --------------------
def detect_intent(q: str) -> Optional[str]:
    q = q.lower()
    if any(k in q for k in ["trip", "travel", "visit"]) and any(k in q for k in ["when", "date", "day"]):
        return "trip_when"
    if "how many" in q and any(k in q for k in ["car", "vehicle"]):
        return "car_count"
    if any(k in q for k in ["favorite", "favourite", "fav"]) and any(k in q for k in ["restaurant", "dining", "food"]):
        return "fav_restaurants"
    return None

# -------------------- Entity Extraction --------------------
def extract_name(q: str) -> Optional[str]:
    """Extract likely member name from a question."""
    excluded = {"When","How","What","Jan","February","March","April","May","June","July","August","September","October","November","December"}
    for cand in NAME_RE.findall(q):
        parts = [p for p in cand.split() if p not in excluded]
        if parts:
            return " ".join(parts)
    return None

# -------------------- Message Utilities --------------------
def text_blob(m: Dict[str, Any]) -> str:
    """Return combined message text from possible keys."""
    out = []
    for k in ["message", "text", "body", "content", "snippet", "note", "description"]:
        v = m.get(k)
        if isinstance(v, str):
            out.append(v)
    if not out:
        out.append(json.dumps(m, ensure_ascii=False))
    return " \n ".join(out)

def filter_by_name(msgs: List[Dict[str, Any]], name: str) -> List[Dict[str, Any]]:
    key = name.lower().strip()
    return [m for m in msgs if key in json.dumps(m, ensure_ascii=False).lower()]

# -------------------- Answer Functions --------------------
def answer_trip_when(name: str, msgs: List[Dict[str, Any]]) -> Optional[str]:
    """Find trip-related messages and extract possible travel date."""
    for m in msgs:
        t = text_blob(m)
        if any(w in t.lower() for w in ["trip", "travel", "vacation", "visit"]):
            match = DATE_RE.search(t)
            if match:
                return f"{name} is planning a trip on {match.group(0)}."
    return None

def answer_car_count(name: str, msgs: List[Dict[str, Any]]) -> Optional[str]:
    """Extract how many cars a user has."""
    patterns = [
        re.compile(r"has\s+(\d+)\s+cars?", re.I),
        re.compile(r"owns\s+(\d+)\s+cars?", re.I),
        re.compile(r"has\s+(\d+)\s+vehicles?", re.I),
        re.compile(r"owns\s+(\d+)\s+vehicles?", re.I),
    ]
    for m in msgs:
        t = text_blob(m)
        for p in patterns:
            match = p.search(t)
            if match:
                n = match.group(1)
                return f"{name} has {n} car{'s' if n != '1' else ''}."
    return None

def answer_fav_restaurants(name: str, msgs: List[Dict[str, Any]]) -> Optional[str]:
    """Find mentions of favorite restaurants."""
    hints = ("restaurant", "diner", "bistro", "bar", "cafe", "eatery", "steakhouse", "pizzeria", "sushi", "tapas")
    results = set()
    proper = re.compile(r"\b([A-Z][\w'&]+(?:\s+[A-Z][\w'&]+){0,3})\b")

    for m in msgs:
        for line in text_blob(m).splitlines():
            lo = line.lower()
            if any(h in lo for h in hints) and any(f in lo for f in ["favorite", "favourite", "fav"]):
                for cand in proper.findall(line):
                    if cand.lower() not in ["favorite restaurants", "restaurants"] and len(cand.split()) <= 4:
                        results.add(cand.strip())
    if results:
        return f"{name}'s favorite restaurants: {', '.join(sorted(results))}."
    return None

# -------------------- Main QA Function --------------------
def answer_question(q: str, corpus: List[Dict[str, Any]]) -> str:
    """Dispatch to appropriate handler based on intent and question."""
    intent = detect_intent(q)
    name = extract_name(q) or "The member"
    msgs = filter_by_name(corpus, name) or corpus

    if intent == "trip_when":
        return answer_trip_when(name, msgs) or f"Sorry, I couldn’t find a date for {name}'s trip."
    if intent == "car_count":
        return answer_car_count(name, msgs) or f"Sorry, I couldn’t determine how many cars {name} has."
    if intent == "fav_restaurants":
        return answer_fav_restaurants(name, msgs) or f"Sorry, I couldn’t find {name}'s favorite restaurants."

    # fallback generic search
    terms = [w for w in re.findall(r"\w+", q.lower()) if len(w) > 2]
    best, score = None, 0
    for m in msgs:
        for line in text_blob(m).splitlines():
            s = sum(1 for t in terms if t in line.lower())
            if s > score:
                score, best = s, line.strip()
    return best or "Sorry, I couldn’t find an answer."
