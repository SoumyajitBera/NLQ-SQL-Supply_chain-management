# Supply-Chain NLQ → SQL Demo

Turn plain-English questions into **validated SQL** and live answers on your MySQL database — zero SQL required from the user.

---

## Table of Contents
1. [Features](#features)  
2. [Quick Start](#quick-start)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Environment Variables](#environment-variables)  
6. [Database Setup](#database-setup)  
7. [Running the App](#running-the-app)  
8. [How It Works](#how-it-works)  
  

---

## Features
- **Ask in English, get SQL** – A CrewAI agent (via OpenRouter.ai) converts questions to safe `SELECT` statements.  
- **Automatic validation** – Blocks non-SELECT keywords, checks syntax, and repairs faulty SQL.  
- **Live execution** – Queries run directly on your MySQL instance; results stream back to the chat widget.  
- **Natural-language answers** – A second agent explains result sets in bullet-point English.  
- **Rich landing page** – Hero section, feature cards, and a floating chat widget — all in Dash.  
- **Transparent metrics** – Generation/execution time, row & column counts, complexity score, and more.  

---

## Quick Start
```bash
# 1 Clone
git clone https://github.com/<you>/supply-chain-nlq-sql.git
cd supply-chain-nlq-sql

# 2 Create & activate virtual-env
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# 3 Install deps
pip install -r requirements.txt

# 4 Configure .env
cp .env.example .env              # then fill in values

# 5 Run the app
python app.py


** Prerequisites** 


| Requirement           | Version / Notes           |
| --------------------- | ------------------------- |
| **Python**            | 3.9 – 3.12                |
| **MySQL**             | 8.x (local or remote)     |
| **OpenRouter.ai key** | Free or paid model access |
| **pip / virtualenv**  | Recommended for isolation |
