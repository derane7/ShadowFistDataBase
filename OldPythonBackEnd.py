from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import re
import logging


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Load CSV
CSV_PATH = "pain.csv"
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

if "release_date" in df.columns:
    df["release_date"] = pd.to_datetime(
        df["release_date"], 
        errors="coerce", 
        infer_datetime_format=True
    ).dt.date.astype(str)  # final format: "YYYY-MM-DD"

# Normalize function for matching
def norm(s):
    return re.sub(r"[\s_\-]+", "", str(s).lower())

# Real column map
real_columns = {norm(c): c for c in df.columns}
logging.info(f"Detected columns: {list(df.columns)}")

# Values that mean "no selection" from frontend dropdowns
DEFAULT_SENTINELS = set(["", None, "default", "--select option---", "--select option--", "all", "any", "none", "select", "select option"])

def normalize_incoming_raw(v):
    """
    Returns raw incoming value unchanged for list types, else string,
    but treats common placeholder values as empty string.
    """
    if v is None:
        return ""
    if isinstance(v, list):
        # keep it as list (we'll handle lists specially)
        return [str(x).strip() for x in v if x is not None and str(x).strip() != ""]
    s = str(v).strip()
    if s.lower() in DEFAULT_SENTINELS:
        return ""
    return s

def find_column(*names):
    """Map expected names to real CSV columns"""
    for n in names:
        if n is None:
            continue
        key = norm(n)
        if key in real_columns:
            return real_columns[key]
    return None

@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}

    # Normalize incoming: keep list as list; convert placeholders to ""
    incoming = {}
    for k, v in data.items():
        incoming[k] = normalize_incoming_raw(v)

    logging.info(f"RECEIVED FILTERS: {incoming}")

    filtered = df.copy()

    # --- NAME: whole-word match on probable name column ---
    name_col = find_column("name")
    name_value = incoming.get("name", "")
    if name_value and name_col:
        # whole-word boundary search, case-insensitive
        pattern = r"\b" + re.escape(name_value.strip().lower()) + r"\b"
        filtered = filtered[filtered[name_col].str.lower().str.contains(pattern, regex=True, na=False)]

    # Generic function that accepts single value OR list-of-values (OR-match)
    def apply_text_tokens_filter(front_key, *csv_candidates):
        nonlocal filtered
        val = incoming.get(front_key, "")
        if not val:
            return
        # find actual column
        col = find_column(*csv_candidates)
        if not col:
            return

        # build token list
        if isinstance(val, list):
            tokens = [t for t in val if t and t.lower() not in DEFAULT_SENTINELS]
        else:
            # split by whitespace so "Fire Water" -> ["Fire","Water"]
            tokens = [t for t in re.split(r"\s+", str(val).strip()) if t and t.lower() not in DEFAULT_SENTINELS]

        if not tokens:
            return

        # build regex matching any token (escape tokens)
        token_pattern = "|".join(re.escape(t) for t in tokens)
        try:
            filtered = filtered[filtered[col].astype(str).str.contains(token_pattern, case=False, na=False, regex=True)]
        except Exception:
            filtered = filtered[filtered[col].astype(str).str.contains(token_pattern, case=False, na=False)]

    # Numeric-ish filters (do substring match to be flexible)
    def apply_numeric_filter(front_key, *csv_candidates):
        nonlocal filtered
        val = incoming.get(front_key, "")
        if not val:
            return
        col = find_column(*csv_candidates)
        if not col:
            return
        s = str(val).strip()
        if s.lower() in DEFAULT_SENTINELS or s == "":
            return
        filtered = filtered[filtered[col].astype(str).str.contains(re.escape(s), case=False, na=False)]

    def apply_text_filter(front_key, *csv_candidates):
        nonlocal filtered
        val = incoming.get(front_key, "")
        if not val:
            return
        if isinstance(val, list):
            apply_text_tokens_filter(front_key, *csv_candidates)
            return
        col = find_column(*csv_candidates)
        if not col:
            return
        s = str(val).strip()
        if s.lower() in DEFAULT_SENTINELS or s == "":
            return
        filtered = filtered[filtered[col].astype(str).str.contains(re.escape(s), case=False, na=False)]

    def apply_date_filter(front_key, *csv_candidates):
        nonlocal filtered
        val = incoming.get(front_key, "")
        if not val:
            return
        
        try:
            user_date = pd.to_datetime(val, errors="raise").date()
        except Exception:
            return
        
        col = find_column(*csv_candidates)
        if not col:
            return
        
        col_dates = pd.to_datetime(filtered[col], errors="coerce").dt.date

        mask = col_dates == user_date
        filtered = filtered[mask]

    # --- Apply all frontend filters properly (map to your CSV's actual columns) ---
    apply_text_tokens_filter("type", "types")
    apply_numeric_filter("hp", "hp")
    apply_numeric_filter("level", "level")
    apply_text_filter("rarity", "rarity")
    apply_text_filter("artist", "artist")
    apply_text_tokens_filter("subtype", "subtypes")
    apply_text_filter("supertypes", "supertype")  # frontend uses 'supertypes' id, csv is 'supertype'
    apply_text_filter("supertype", "supertype")   # support both keys
    apply_text_filter("set", "set")
    apply_text_filter("set_num", "set_num")
    apply_text_filter("evolvesFrom", "evolvesFrom")
    apply_text_filter("evolvesTo", "evolvesTo")
    apply_date_filter("release_date", "release_date")
    apply_date_filter("releasedate", "release_date")
    apply_text_filter("generation", "generation")
    apply_text_filter("publisher", "publisher")
    apply_text_filter("series", "series")
    apply_text_tokens_filter("abilities", "abilities")
    apply_text_tokens_filter("attacks", "attacks")
    apply_text_tokens_filter("weaknesses", "weaknesses")
    apply_text_tokens_filter("resistances", "resistances")
    apply_text_filter("retreatCost", "retreatCost")
    apply_text_filter("convertedRetreatCost", "convertedRetreatCost")
    apply_text_filter("flavorText", "flavorText")
    apply_text_filter("nationalPokedexNumbers", "nationalPokedexNumbers")
    apply_text_filter("legalities", "legalities")
    apply_text_filter("legality", "legalities")
    apply_text_filter("rules", "rules")
    apply_text_filter("regulationMark", "regulationMark")
    apply_text_filter("ancientTrait", "ancientTrait")
    apply_text_filter("id", "id")

    # Keyword search (search multiple columns)
    kw = incoming.get("keywordSearch", "")
    if kw and not (isinstance(kw, list) and len(kw) == 0):
        tokens = kw if isinstance(kw, list) else [t for t in re.split(r"\s+", str(kw).strip()) if t]
        if tokens:
            token_pattern = "|".join(re.escape(t) for t in tokens)
            keyword_cols = ["name", "types", "subtypes", "artist", "rarity", "flavorText", "abilities", "attacks", "rules", "series", "publisher"]
            mask = False
            for c in keyword_cols:
                col = find_column(c)
                if col:
                    mask = mask | filtered[col].astype(str).str.contains(token_pattern, case=False, na=False)
            filtered = filtered[mask]

    # Deduplicate and limit
    filtered = filtered.drop_duplicates().reset_index(drop=True)
    MAX_RESULTS = 1000
    if len(filtered) > MAX_RESULTS:
        filtered = filtered.head(MAX_RESULTS)

    return jsonify({"results": filtered.to_dict(orient="records")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
