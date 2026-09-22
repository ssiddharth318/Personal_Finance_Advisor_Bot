# Technical Architecture

Browser (HTML/CSS/JavaScript + Chart.js)
        |
        v
Flask REST/API layer
        |
   +----+----+
   |         |
 SQLite   Gemini REST API (optional)
   |
Transactions / Budgets / Goals

The frontend is responsive and communicates with Flask JSON endpoints. SQLite stores the
finance data locally. Gemini is optional; the project falls back to deterministic local
insights when no API key is configured.
