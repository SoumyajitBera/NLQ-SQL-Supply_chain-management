# Supply-Chain NLQ → SQL Demo

Turn plain‑English questions into **validated SQL** and live answers on your MySQL database — zero SQL required from the user.

---

## Table of Contents
1. [Features](#features)  
2. [Quick Start](#quick-start)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Environment Variables](#environment-variables)  
6. [Database Setup](#database-setup)  
7. [Running the App](#running-the-app)  
8. [Troubleshooting](#troubleshooting)  
9. [Project Structure](#project-structure)  
 

---

## Features
- **Ask in English, get SQL** – A CrewAI agent (via OpenRouter.ai) converts questions to safe `SELECT` statements.  
- **Automatic validation** – Blocks non‑SELECT keywords, checks syntax, and repairs faulty SQL.  
- **Live execution** – Queries run directly on your MySQL instance; results stream back to the chat widget.  
- **Natural‑language answers** – A second agent explains result sets in bullet‑point English.  
- **Rich landing page** – Hero section, feature cards, and a floating chat widget — all in Dash.  
- **Transparent metrics** – Generation/execution time, row & column counts, complexity score, and more.  

---

## Quick Start
```bash
# 1 Clone
git clone https://github.com/<you>/supply-chain-nlq-sql.git
cd supply-chain-nlq-sql

# 2 Create & activate virtual‑env
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# 3 Install deps
pip install -r requirements.txt

# 4 Configure .env
cp .env.example .env              # then fill in values

# 5 Run the app
python app.py
```
Open <http://localhost:8050> and start chatting!

---

## Prerequisites
| Requirement           | Version / Notes                |
|-----------------------|--------------------------------|
| **Python**            | 3.9 – 3.12                     |
| **MySQL**             | 8.x (local or remote)          |
| **OpenRouter.ai key** | Free or paid model access      |
| **pip / virtualenv**  | Recommended for isolation      |

---

## Installation
All Python requirements are in `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

## Environment Variables
Create a `.env` file in the project root:

```dotenv
# ─── OpenRouter / LLM ─────────────────────────────
OPENROUTER_API_KEY = sk-********************************
# (optionally change the free model)
# OPENROUTER_MODEL = openrouter/meta-llama/llama-3.3-8b-instruct:free

# ─── MySQL connection ─────────────────────────────
MYSQL_HOST     = localhost
MYSQL_PORT     = 3306
MYSQL_USER     = root
MYSQL_PASSWORD = <your-password>
MYSQL_DATABASE = supply_chain_management
```
> **Tip:** Use a read‑only MySQL account in production.

---

## Database Setup
1. **Create the schema** (tables `suppliers`, `products`, …) using the DDL block in **`nlq_sql.py`**.  
2. **Load sample data** (optional).  
3. Ensure the MySQL user in `.env` can `SELECT` from all tables.

```sql
CREATE DATABASE IF NOT EXISTS supply_chain_management;
-- … create tables …
```

---

## Running the App
```bash
python app.py
```
- Dash starts on <http://127.0.0.1:8050>.  
- Expand the chat (bottom‑right) and ask a question, e.g.:

> *“Which products are out of stock in any warehouse?”*

You’ll receive:
1. **Generated SQL**  
2. **Results** (first few rows)  
3. **Metrics** (timings, counts, complexity)

---


## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `OpenRouter API Error 401` | Missing/invalid API key | Check `.env`, renew key |
| Empty answer (“unable to answer”) | Query returned 0 rows | Refine the question or load data |
| `mysql.connector.Error: 1045` | Bad DB credentials | Update `.env` |
| Chat unresponsive | Empty DB or schema mismatch | Verify schema matches DDL |

---

## Project Structure
```
supply-chain-nlq-sql/
├── app.py            # Dash UI (landing + chat)
├── nlq_sql.py        # CrewAI pipeline + DB handler
├── requirements.txt
├── .env.example
└── README.md
```

---


### Happy querying 🎉
