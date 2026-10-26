# Personal Finance Advisor Bot 💰

An AI-style personal finance assistant built with **Python, Flask, SQLite and JavaScript**.

## Features
- Income and expense tracking
- Category-wise spending analysis
- Budget overview and savings estimate
- AI-style personalized financial insights
- Monthly financial summary
- Responsive dashboard UI
- SQLite database for persistent local data
- Demo/fallback advisor mode that works without an external AI API

## Tech Stack
Python • Flask • SQLite • HTML • CSS • JavaScript

## Run locally

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start:
```bash
python app.py
```

Open:
`http://127.0.0.1:5000`

## Project Structure

```text
personal-finance-advisor-bot/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## GitHub submission

Create a new GitHub repository, upload all files, commit them, then submit the repository URL.

> Note: This version includes a reliable local advisor/fallback mode. An external Gemini API can be integrated later if required by the mentor.
