from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app, origins="*")

# ----------------------------
# LOAD EXCEL SAFELY
# ----------------------------
df = pd.read_excel(
    "C:/Users/deran/school/Networking/SFproject/Shadowfist_Project_Table.xlsx", header=1
)

# Clean column names
df.columns = df.columns.str.strip()

# Replace NaN with empty string (VERY IMPORTANT)
df = df.replace({np.nan: ""})

# Ensure all used columns exist as strings
for col in ["Title", "subtype", "Cost", "Pow", "Bod", "Res"]:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna("")


# ----------------------------
# SEARCH ENDPOINT
# ----------------------------

@app.route("/search", methods=["POST"])

def search_cards():
    try:
        data = request.get_json() or {}
        print("REQUEST RECEIVED:", data)
        print("🔥 RAW DATA:", request.get_json())
        print("🔥 DF COLUMNS:", df.columns.tolist())

        results = df.copy()

        # ------------------------
        # INPUTS (safe conversion)
        # ------------------------
        subtype = str(data.get("subtype", "")).strip()
        keyword = str(data.get("keywordSearch", "")).strip()

        cost = str(data.get("Cost", "")).strip()
        pow_ = str(data.get("Pow", "")).strip()
        bod = str(data.get("Bod", "")).strip()
        res = str(data.get("Res", "")).strip()

        # ------------------------
        # SUBTYPE FILTER
        # ------------------------
        if subtype:
            results = results[
                results["subtype"]
                .astype(str)
                .str.strip()
                .str.lower()
                .str.contains(subtype.strip().lower(), na=False)
            ]

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
        if pow_:
            results = results[
                results["Pow"].astype(str).str.strip().str.contains(pow_, na=False)
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
                | results["subtype"].astype(str).str.contains(keyword, case=False, na=False)
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
