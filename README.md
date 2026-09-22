# FinPilot — Personal Finance Advisor Bot

A full-stack Flask + SQLite personal finance planning app inspired by the project brief in the supplied screenshots.

## Included
- Dashboard with income, expenses, balance and savings rate
- Cash-flow and spending charts
- Transaction ledger with search/filter/delete
- Category budgets with overspending detection
- Savings goals and progress
- Gemini AI assistant with a no-key local fallback
- Responsive UI
- Demo data so the project looks populated immediately
- SQLite local database

## Run on Windows / VS Code

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open Terminal and run:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

4. Install:
```bash
pip install -r requirements.txt
```

5. Optional Gemini AI:
- Copy `.env.example` to `.env`
- Put your Gemini API key in `GEMINI_API_KEY`.
- Or set it as an environment variable.

6. Start:
```bash
python app.py
```

7. Open:
`http://127.0.0.1:5000`

## Notes
The app works without a Gemini key. In that mode, the AI page uses a local rule-based financial insight engine.

This is an educational budgeting tool, not a substitute for a regulated financial adviser.
