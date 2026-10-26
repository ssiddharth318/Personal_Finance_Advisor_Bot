from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "finance.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    )""")
    con.commit()
    con.close()

def db_rows():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "POST":
        data = request.get_json() or {}
        try:
            amount = float(data.get("amount", 0))
        except ValueError:
            amount = 0
        if amount <= 0 or not data.get("category") or data.get("kind") not in ("income", "expense"):
            return jsonify({"error": "Please enter valid transaction details."}), 400
        con = sqlite3.connect(DB)
        con.execute(
            "INSERT INTO transactions(kind,category,amount,note,created_at) VALUES(?,?,?,?,?)",
            (data["kind"], data["category"], amount, data.get("note",""), datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        con.commit()
        con.close()
        return jsonify({"ok": True})
    return jsonify(db_rows())

@app.route("/api/summary")
def summary():
    rows = db_rows()
    income = sum(x["amount"] for x in rows if x["kind"] == "income")
    expense = sum(x["amount"] for x in rows if x["kind"] == "expense")
    by_cat = {}
    for x in rows:
        if x["kind"] == "expense":
            by_cat[x["category"]] = by_cat.get(x["category"], 0) + x["amount"]
    top = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "income": income,
        "expense": expense,
        "balance": income-expense,
        "categories": dict(top),
        "top_category": top[0][0] if top else "—"
    })

@app.route("/api/advice")
def advice():
    s = summary().get_json()
    income, expense = s["income"], s["expense"]
    if income == 0:
        return jsonify({"title":"Start with your income","text":"Add your monthly income and a few expenses. The advisor will then generate a personalized budget suggestion."})
    ratio = expense / income
    if ratio > 0.8:
        text = "Your expenses are above 80% of income. Try reducing discretionary spending and aim to keep an emergency-saving amount aside."
    elif ratio > 0.6:
        text = "Your spending is moderate. Review your highest category and consider moving 10–20% of income toward savings."
    else:
        text = "Great control so far. Keep essential spending stable and consider building an emergency fund with part of your remaining balance."
    return jsonify({"title":"AI-style financial insight","text":text})

@app.route("/health")
def health():
    return jsonify({"status":"Personal Finance Advisor Bot is running"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
