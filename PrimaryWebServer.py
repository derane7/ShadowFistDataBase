from flask import Flask, request, jsonify
from flask_cors import CORS
from ErrorCodes import build_error_response
from flask import send_from_directory
import pandas as pd
import numpy as np
from DataManager import (
    create_account,
    login,
    create_deck,
    delete_deck,
    add_card_to_deck,
    remove_card_from_deck,
    get_user_decks
)

app = Flask(__name__)
CORS(app, origins="*")

# ----------------------------
# LOAD EXCEL SAFELY
# ----------------------------

# Commented out the hardcoded path, can uncomment if needed
#df = pd.read_excel(
#    "C:/Users/deran/school/Networking/SFproject/Shadowfist_Project_Table.xlsx", header=1
#)

# Created relative path for functionality with or without database
CARD_DATABASE_FILE = "data/Shadowfist_Project_Table.xlsx"

try:
    df = pd.read_excel(CARD_DATABASE_FILE, header=1, engine="openpyxl")
    print("Card database loaded successfully.")
except Exception as e:
    print("Warning: Could not load card database.")
    print("Reason:", e)
    print("Starting server with empty placeholder card data.")
    df = pd.DataFrame()

# Clean card database only if it loaded successfully
if not df.empty:
    df.columns = df.columns.map(str).str.strip()

    # Replace NaN with empty string
    df = df.replace({np.nan: ""})

    # Ensure all used columns exist as strings
    for col in ["Title", "Subtype", "Cost", "Pow", "Bod", "Res"]:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("")
else:
    print("Card database is empty. Search route will use placeholder data.")

# Replace NaN with empty string (VERY IMPORTANT)
df = df.replace({np.nan: ""})

# Ensure all used columns exist as strings
for col in ["Title", "Subtype", "Cost", "Pow", "Bod", "Res"]:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna("")

# ----------------------------
# Directory Serving
# ----------------------------

@app.route("/")
def home():
    return send_from_directory(".", "Login.html")


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
# Account Features
# ----------------------------

@app.route("/create-account", methods=["POST"])
def create_account_route():
    data = request.get_json()
    response = create_account(
        data.get("username", ""),
        data.get("password", "")
    )
    return jsonify(response)


@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    response = login(
        data.get("username", ""),
        data.get("password", "")
    )
    return jsonify(response)


@app.route("/create-deck", methods=["POST"])
def create_deck_route():
    data = request.get_json()
    response = create_deck(
        data.get("username", ""),
        data.get("deckName", "")
    )
    return jsonify(response)


@app.route("/delete-deck", methods=["POST"])
def delete_deck_route():
    data = request.get_json()
    response = delete_deck(
        data.get("username", ""),
        data.get("deckName", "")
    )
    return jsonify(response)


@app.route("/add-card", methods=["POST"])
def add_card_route():
    data = request.get_json()
    response = add_card_to_deck(
        data.get("username", ""),
        data.get("deckName", ""),
        data.get("cardID", ""),
        data.get("cardName", "")
    )
    return jsonify(response)


@app.route("/remove-card", methods=["POST"])
def remove_card_route():
    data = request.get_json()
    response = remove_card_from_deck(
        data.get("username", ""),
        data.get("deckName", ""),
        data.get("cardID", "")
    )
    return jsonify(response)


@app.route("/user-decks", methods=["POST"])
def user_decks_route():
    data = request.get_json()
    response = get_user_decks(data.get("username", ""))
    return jsonify(response)

# ----------------------------
# SEARCH ENDPOINT
# ----------------------------

@app.route("/search", methods=["POST"])

def search_cards():
    # If the card database file is missing, df will be empty
    # This lets the server keep running and returns placeholder data for testing
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
                    "text": "This is a manually created test card for deck testing."
                }
            ]
        })

    try:
        data = request.get_json() or {}
        print("REQUEST RECEIVED:", data)
        print("🔥 RAW DATA:", request.get_json())
        print("🔥 DF COLUMNS:", df.columns.tolist())
        

        results = df.copy()
        
        # ------------------------
        # INPUTS (safe conversion)
        # ------------------------
        Subtype = str(data.get("Subtype", "")).strip()
        keyword = str(data.get("keywordSearch", "")).strip()
        
        print("Subtype INPUT:", repr(Subtype))
        print("SAMPLE DF VALUES:", df["Subtype"].head(10).tolist()) 
        print("FILTER CHECK:", Subtype)
        print(df["Subtype"].unique()[:10])

        cost = str(data.get("Cost", "")).strip()
        pow= str(data.get("Pow", "")).strip()
        bod = str(data.get("Bod", "")).strip()
        res = str(data.get("Res", "")).strip()

        # ------------------------
        # Subtype FILTER
        # ------------------------
        if Subtype:
            results = results[
                results["Subtype"]
                .str.casefold()
                .str.contains(Subtype.casefold(), na=False)
            ]

        print(results["Subtype"].value_counts().head(20))

        # ------------------------
        # COST FILTER
        # ------------------------
        if cost:
            results = results[
                results["Cost"].astype(str).str.strip().str.contains(cost, na=False)
            ]

        # ------------------------
        # POW FILTER
        # ------------------------
        if pow:
            results = results[
                results["Pow"].astype(str).str.strip().str.contains(pow, na=False)
            ]

        # ------------------------
        # BOD FILTER
        # ------------------------
        if bod:
            results = results[
                results["Bod"].astype(str).str.strip().str.contains(bod, na=False)
            ]

        # ------------------------
        # RES FILTER
        # ------------------------
        if res:
            results = results[
                results["Res"].astype(str).str.strip().str.contains(res, na=False)
            ]

        # ------------------------
        # KEYWORD SEARCH
        # ------------------------
        if keyword:
            results = results[
                results["Title"].astype(str).str.contains(keyword, case=False, na=False)
                | results["Subtype"].astype(str).str.contains(keyword, case=False, na=False)
            ]

        # ------------------------
        # SAFETY LIMIT (optional)
        # ------------------------
        MAX_RESULTS = 1000
        if len(results) > MAX_RESULTS:
            results = results.head(MAX_RESULTS)

        # ------------------------
        # RETURN SAFE JSON
        # ------------------------
        return jsonify({
            "results": results.to_dict(orient="records")
        })

    except Exception as e:
        print("BACKEND ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500


# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    print("SCRIPT IS STARTING")
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    )
