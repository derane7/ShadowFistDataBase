"""
Shadowfist Database — Flask web server.

Serves the static HTML/CSS pages and exposes the JSON endpoints used by
the frontend:
    /                    -> Login.html
    /Login.html          -> Login.html
    /CreateAccount.html  -> CreateAccount.html
    /Account.html        -> Account.html
    /Search.html         -> Search.html
    /Result.html         -> Result.html
    /Styles.css          -> Styles.css

    POST /create-account -> create_account()
    POST /login          -> login()
    POST /create-deck    -> create_deck()
    POST /delete-deck    -> delete_deck()
    POST /add-card       -> add_card_to_deck()
    POST /remove-card    -> remove_card_from_deck()
    POST /user-decks     -> get_user_decks()
    POST /search         -> search_cards()  (this file)

Run:
    python PrimaryWebServer.py
Then open http://127.0.0.1:5000/ in a browser.

The card database is read from data/Shadowfist_Project_Table.xlsx. If that
file is missing, /search returns a single placeholder card so the rest of
the app still works for testing.
"""

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import pandas as pd
import numpy as np

from DataManager import (
    create_account,
    login,
    create_deck,
    delete_deck,
    add_card_to_deck,
    remove_card_from_deck,
    get_user_decks,
)

app = Flask(__name__)
CORS(app, origins="*")

# Prevent browsers from caching HTML pages. Without this, Flask sets ETags
# and browsers serve stale cached copies of HTML files even after you update
# them — causing "304 Not Modified" with the old file content.
@app.after_request
def no_cache_html(response):
    if response.content_type and "text/html" in response.content_type:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ----------------------------
# LOAD CARD DATABASE
# ----------------------------
CARD_DATABASE_FILE = "data/Shadowfist_Project_Table.xlsx"

# Columns the search code reads. If the spreadsheet uses different headers,
# update this list.
SEARCH_COLUMNS = ["Title", "Subtype", "Cost", "Pow", "Bod", "Res"]

try:
    df = pd.read_excel(CARD_DATABASE_FILE, header=1, engine="openpyxl")
    print("Card database loaded ({} raw rows).".format(len(df)))
except Exception as e:
    print("Warning: Could not load card database.")
    print("Reason:", e)
    print("Starting server with empty placeholder card data.")
    df = pd.DataFrame()

if not df.empty:
    # ---- CONFIRMED COLUMNS (from actual spreadsheet inspection) ----
    # Title, Subtype, Cost, Bod, Pow, Res, Designator, Keyword, Text, Tag,
    # Artist, Expansion, Rarity
    # ----------------------------------------------------------------

    # 1. Drop rows where Title is missing (section dividers like "Unaligned Sites"
    #    that have nothing else). dropna treats NaN and empty cells as missing.
    df = df.dropna(subset=["Title"])

    # 2. Drop repeated header rows — the spreadsheet restates column names between
    #    every section. After dropna(Title) these rows have Title="Title".
    #    BUG IN NAIVE CODE: .strip().lower() on a Series operates on the object,
    #    not element-wise. Must use .str.strip().str.lower().
    df = df[df["Title"].astype(str).str.strip().str.lower() != "title"]

    # 3. Drop section-divider rows that have a Title but no Subtype
    #    (e.g. the lone "Unaligned Feng Shui Sites" label row).
    df = df.dropna(subset=["Subtype"])

    # 4. Normalize non-breaking spaces ( ) to regular spaces.
    #    "Architects of the Flesh" and "Eaters of the Lotus" entries in the
    #    spreadsheet use   instead of space, so without this fix the dropdown
    #    filter (which sends regular spaces) would never match those cards.
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.replace("\xa0", " ", regex=False)

    # 5. Strip whitespace from key string columns
    for col in ["Title", "Subtype"]:
        if col in df.columns:
            df[col] = df[col].str.strip()

    # 6. Replace NaN residuals with empty string
    df = df.replace({np.nan: "", "nan": "", "None": ""})

    # 7. Clean numeric stat columns: pandas reads Excel numbers as floats
    #    (5 → 5.0). Convert whole numbers to int strings ("5"), leave
    #    non-numeric values like "X" or "H 2" as-is.
    def _clean_num(v):
        s = str(v).strip()
        if s in ("", "nan", "None", "NaN"):
            return ""
        try:
            f = float(s)
            return str(int(f)) if f == int(f) else s
        except (ValueError, TypeError):
            return s  # keep non-numeric values ("X", "H 2", etc.)

    for col in ["Cost", "Bod", "Pow"]:
        if col in df.columns:
            df[col] = df[col].apply(_clean_num)

    print("Card database ready: {} cards after cleaning.".format(len(df)))
    print("Columns:", df.columns.tolist())

# ----------------------------
# STATIC PAGES
# ----------------------------

@app.route("/")
def home():
    # Land on Search.html so the user sees the catalog right away.
    # If you'd rather force login first, change this to "Login.html".
    return send_from_directory(".", "Search.html")


@app.route("/Login.html")
def login_page():
    return send_from_directory(".", "Login.html")


@app.route("/CreateAccount.html")
def create_account_page():
    return send_from_directory(".", "CreateAccount.html")


@app.route("/Account.html")
def account_page():
    return send_from_directory(".", "Account.html")


@app.route("/Search.html")
def search_page():
    return send_from_directory(".", "Search.html")


@app.route("/Result.html")
def result_page():
    return send_from_directory(".", "Result.html")


@app.route("/Styles.css")
def styles():
    return send_from_directory(".", "Styles.css")


# ----------------------------
# ACCOUNT / DECK ENDPOINTS
# ----------------------------

@app.route("/create-account", methods=["POST"])
def create_account_route():
    data = request.get_json() or {}
    return jsonify(create_account(data.get("username", ""), data.get("password", "")))


@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json() or {}
    return jsonify(login(data.get("username", ""), data.get("password", "")))


@app.route("/create-deck", methods=["POST"])
def create_deck_route():
    data = request.get_json() or {}
    return jsonify(create_deck(data.get("username", ""), data.get("deckName", "")))


@app.route("/delete-deck", methods=["POST"])
def delete_deck_route():
    data = request.get_json() or {}
    return jsonify(delete_deck(data.get("username", ""), data.get("deckName", "")))


@app.route("/add-card", methods=["POST"])
def add_card_route():
    data = request.get_json() or {}
    return jsonify(add_card_to_deck(
        data.get("username", ""),
        data.get("deckName", ""),
        data.get("cardID", ""),
        data.get("cardName", ""),
    ))


@app.route("/remove-card", methods=["POST"])
def remove_card_route():
    data = request.get_json() or {}
    return jsonify(remove_card_from_deck(
        data.get("username", ""),
        data.get("deckName", ""),
        data.get("cardID", ""),
    ))


@app.route("/user-decks", methods=["POST"])
def user_decks_route():
    data = request.get_json() or {}
    return jsonify(get_user_decks(data.get("username", "")))


# ----------------------------
# SEARCH ENDPOINT
# ----------------------------

@app.route("/search", methods=["POST"])
def search_cards():
    """
    Filter the card dataframe by Subtype / Cost / Pow / Bod / Res / keyword.
    All filters are case-insensitive substring matches against the string
    representation of the cell value (so "1" matches "1", "11", "21", etc).
    """
    # Placeholder response if the Excel file isn't available
    if df.empty:
        return jsonify({
            "status": "success",
            "message": "Card database not loaded. Returning test card.",
            "results": [
                {
                    "id": "TEST-001",
                    "Title": "Test Dragon Warrior",
                    "Cost": "3",
                    "Pow": "5",
                    "Bod": "4",
                    "Res": "1",
                    "Subtype": "Dragon Character",
                    "text": "This is a manually created test card for deck testing.",
                }
            ]
        })

    try:
        data = request.get_json() or {}
        results = df.copy()

        # ---- Inputs ----
        # Subtype may be a JSON array (sent by faction grid) or a plain string
        # (sent by the manual dropdown).  We normalize to a list either way so
        # the OR filter below works consistently.
        raw_subtype = data.get("Subtype", [])
        if isinstance(raw_subtype, list):
            subtypes = [s.strip() for s in raw_subtype if str(s).strip()]
        else:
            subtypes = [str(raw_subtype).strip()] if str(raw_subtype).strip() else []

        keyword = str(data.get("keywordSearch", "")).strip()
        cost    = str(data.get("Cost", "")).strip()
        pow_    = str(data.get("Pow", "")).strip()
        bod     = str(data.get("Bod", "")).strip()
        res     = str(data.get("Res", "")).strip()

        # ---- Helper: single-value case-insensitive substring filter ----
        def filter_contains(frame, col, value):
            if not value or col not in frame.columns:
                return frame
            return frame[
                frame[col].astype(str).str.casefold()
                          .str.contains(value.casefold(), na=False, regex=False)
            ]

        # ---- Subtype: OR filter across all selected types ----
        # e.g. ['Dragon Characters', 'Dragon Sites'] → cards matching EITHER type
        if subtypes and "Subtype" in results.columns:
            mask = pd.Series([False] * len(results), index=results.index)
            col_cf = results["Subtype"].astype(str).str.casefold()
            for st in subtypes:
                mask = mask | col_cf.str.contains(st.casefold(), na=False, regex=False)
            results = results[mask]

        # ---- Stat filters (single-value substring) ----
        results = filter_contains(results, "Cost", cost)
        results = filter_contains(results, "Pow",  pow_)
        results = filter_contains(results, "Bod",  bod)
        results = filter_contains(results, "Res",  res)

        # Keyword: search in Title OR Subtype
        if keyword and ("Title" in results.columns or "Subtype" in results.columns):
            mask = pd.Series([False] * len(results), index=results.index)
            if "Title" in results.columns:
                mask = mask | results["Title"].astype(str).str.contains(keyword, case=False, na=False, regex=False)
            if "Subtype" in results.columns:
                mask = mask | results["Subtype"].astype(str).str.contains(keyword, case=False, na=False, regex=False)
            results = results[mask]

        # Safety limit
        MAX_RESULTS = 1000
        if len(results) > MAX_RESULTS:
            results = results.head(MAX_RESULTS)

        return jsonify({
            "status": "success",
            "results": results.to_dict(orient="records"),
        })

    except Exception as e:
        print("BACKEND ERROR:", e)
        return jsonify({"status": "error", "error": str(e)}), 500


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("Shadowfist server starting on http://127.0.0.1:5000")
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False,
    )
