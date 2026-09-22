import os
import sqlite3
import json
import urllib.request
import urllib.error
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income','expense')),
        date TEXT NOT NULL,
        note TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        limit_amount REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target REAL NOT NULL,
        saved REAL NOT NULL DEFAULT 0,
        deadline TEXT DEFAULT ''
    );
    """)
    count = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count == 0:
        demo = [
            ("Salary", "Salary", 55000, "income", "2026-09-01", "Monthly salary"),
            ("Freelance", "Freelance", 8500, "income", "2026-09-08", "Design project"),
            ("Rent", "Housing", 12000, "expense", "2026-09-02", "PG / rent"),
            ("Groceries", "Food", 4200, "expense", "2026-09-04", "Monthly groceries"),
            ("Transport", "Transport", 1800, "expense", "2026-09-07", "Travel"),
            ("Subscriptions", "Entertainment", 999, "expense", "2026-09-10", "Streaming"),
            ("College", "Education", 3500, "expense", "2026-09-11", "Study expenses"),
            ("Shopping", "Shopping", 2400, "expense", "2026-09-14", "Clothes"),
            ("Emergency fund", "Savings", 5000, "expense", "2026-09-15", "Moved to savings"),
        ]
        db.executemany("""INSERT INTO transactions
            (title,category,amount,type,date,note) VALUES (?,?,?,?,?,?)""", demo)
        db.executemany("""INSERT OR IGNORE INTO budgets(category,limit_amount)
            VALUES (?,?)""", [
            ("Housing",15000),("Food",6000),("Transport",3000),
            ("Education",5000),("Entertainment",2000),("Shopping",3000)
        ])
        db.executemany("""INSERT INTO goals(name,target,saved,deadline)
            VALUES (?,?,?,?)""", [
            ("Emergency Fund", 100000, 25000, "2027-03-31"),
            ("New Laptop", 90000, 36000, "2027-01-31")
        ])
    db.commit()
    db.close()

def summary():
    db = get_db()
    income = db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='income'").fetchone()[0]
    expense = db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='expense'").fetchone()[0]
    by_cat = db.execute("""SELECT category, ROUND(SUM(amount),2) amount
        FROM transactions WHERE type='expense' GROUP BY category ORDER BY amount DESC""").fetchall()
    monthly = db.execute("""SELECT substr(date,1,7) month,
        ROUND(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),2) income,
        ROUND(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),2) expense
        FROM transactions GROUP BY substr(date,1,7) ORDER BY month""").fetchall()
    budgets = db.execute("""SELECT b.category,b.limit_amount,
        COALESCE(SUM(CASE WHEN t.type='expense' THEN t.amount ELSE 0 END),0) spent
        FROM budgets b LEFT JOIN transactions t ON t.category=b.category
        GROUP BY b.id ORDER BY b.category""").fetchall()
    goals = db.execute("SELECT * FROM goals ORDER BY id DESC").fetchall()
    return {
        "income": round(income,2),
        "expense": round(expense,2),
        "balance": round(income-expense,2),
        "savings_rate": round(((income-expense)/income*100) if income else 0,1),
        "categories": [dict(x) for x in by_cat],
        "monthly": [dict(x) for x in monthly],
        "budgets": [dict(x) for x in budgets],
        "goals": [dict(x) for x in goals]
    }

def local_advice(data):
    advice = []
    if data["savings_rate"] < 10:
        advice.append("Your current savings rate is below 10%. Try setting an automatic savings target before discretionary spending.")
    elif data["savings_rate"] < 20:
        advice.append("You are saving, but a 20% target could create more breathing room for emergencies and goals.")
    else:
        advice.append("Your savings rate is healthy in this sample dashboard. Keep goal contributions consistent.")
    if data["categories"]:
        top = data["categories"][0]
        advice.append(f"{top['category']} is your largest expense category at ₹{top['amount']:,.0f}. Review recurring or avoidable costs there first.")
    for b in data["budgets"]:
        if b["spent"] > b["limit_amount"]:
            advice.append(f"{b['category']} is over budget by ₹{b['spent']-b['limit_amount']:,.0f}.")
    if not advice:
        advice.append("Add more transactions to receive personalized insights.")
    return advice

def gemini_answer(message, data):
    if not GEMINI_API_KEY:
        return None
    prompt = f"""You are a personal finance planning assistant. Give educational, practical guidance,
not regulated financial advice or guaranteed investment returns. Use INR and Indian context where useful.
Dashboard data:
{json.dumps(data, indent=2)}
User question: {message}
Respond in concise plain text with 3-6 useful bullet points. Mention assumptions if needed."""
    body = json.dumps({
        "contents":[{"parts":[{"text":prompt}]}]
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            payload = json.loads(r.read().decode())
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

@app.route("/")
def index():
    return render_template("index.html", page="dashboard")

@app.route("/transactions")
def transactions():
    return render_template("transactions.html", page="transactions")

@app.route("/budgets")
def budgets():
    return render_template("budgets.html", page="budgets")

@app.route("/goals")
def goals():
    return render_template("goals.html", page="goals")

@app.route("/assistant")
def assistant():
    return render_template("assistant.html", page="assistant")

@app.get("/api/summary")
def api_summary():
    return jsonify(summary())

@app.get("/api/transactions")
def api_transactions():
    rows = get_db().execute("SELECT * FROM transactions ORDER BY date DESC,id DESC").fetchall()
    return jsonify([dict(x) for x in rows])

@app.post("/api/transactions")
def add_transaction():
    data = request.get_json(force=True)
    try:
        amount = float(data["amount"])
        if amount <= 0: raise ValueError()
    except Exception:
        return jsonify({"error":"Amount must be a positive number"}), 400
    db = get_db()
    db.execute("""INSERT INTO transactions(title,category,amount,type,date,note)
        VALUES (?,?,?,?,?,?)""", (
        data.get("title","Untitled"), data.get("category","Other"), amount,
        data.get("type","expense"), data.get("date",datetime.now().date().isoformat()),
        data.get("note","")
    ))
    db.commit()
    return jsonify({"ok":True})

@app.delete("/api/transactions/<int:txid>")
def delete_transaction(txid):
    db = get_db()
    db.execute("DELETE FROM transactions WHERE id=?", (txid,))
    db.commit()
    return jsonify({"ok":True})

@app.post("/api/budgets")
def add_budget():
    data = request.get_json(force=True)
    try: limit = float(data["limit"])
    except: return jsonify({"error":"Invalid limit"}),400
    db=get_db()
    db.execute("""INSERT INTO budgets(category,limit_amount) VALUES (?,?)
        ON CONFLICT(category) DO UPDATE SET limit_amount=excluded.limit_amount""",
        (data["category"],limit))
    db.commit()
    return jsonify({"ok":True})

@app.post("/api/goals")
def add_goal():
    data=request.get_json(force=True)
    try:
        target=float(data["target"])
        saved=float(data.get("saved",0))
    except: return jsonify({"error":"Invalid amount"}),400
    db=get_db()
    db.execute("INSERT INTO goals(name,target,saved,deadline) VALUES (?,?,?,?)",
               (data["name"],target,saved,data.get("deadline","")))
    db.commit()
    return jsonify({"ok":True})

@app.post("/api/assistant")
def api_assistant():
    data=summary()
    msg=request.get_json(force=True).get("message","")
    ai=gemini_answer(msg,data)
    if ai:
        return jsonify({"answer":ai,"source":"Gemini AI"})
    joined="\n".join("• "+x for x in local_advice(data))
    return jsonify({"answer":joined + "\n\nTip: add GEMINI_API_KEY to .env to enable Gemini-powered answers.","source":"Smart local advisor"})

@app.post("/api/reset-demo")
def reset_demo():
    db=get_db()
    db.execute("DELETE FROM transactions")
    db.execute("DELETE FROM budgets")
    db.execute("DELETE FROM goals")
    db.commit()
    init_db()
    return jsonify({"ok":True})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
