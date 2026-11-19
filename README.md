# SQL Agent

### A clean, human-friendly Oracle SQL assistant powered by Gemini

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Oracle](https://img.shields.io/badge/Database-Oracle-F80000.svg?logo=oracle&logoColor=white)](https://www.oracle.com/database/)
[![Gemini](https://img.shields.io/badge/AI-Gemini-8E75B2.svg)](https://ai.google.dev/)

> Ask database questions in plain English, review the generated Oracle SQL, and run it against your database only when you choose.

## Contents

- [What it does](#what-it-does)
- [Workflow](#workflow)
- [Features](#features)
- [Setup](#setup)
- [Database connection](#database-connection)
- [Project structure](#project-structure)
- [Safety notes](#safety-notes)

## What it does

SQL Agent combines a Flask web interface, LangChain, Gemini, and SQLAlchemy to make Oracle work easier:

1. Reads the live Oracle schema.
2. Converts a natural-language request into Oracle SQL.
3. Shows the SQL in a readable code cell.
4. Executes it only after clicking **Run in database**.
5. Displays query rows, changed-row counts, and database errors.

## Workflow

```text
Plain-English question
        ↓
Live Oracle schema + Gemini
        ↓
Reviewable Oracle SQL
        ↓
Run in database (optional)
        ↓
Rows, changes, or a clear error
```

## Features

| Feature | Description |
| :--- | :--- |
| Natural-language SQL | Ask questions without writing SQL manually. |
| Live schema context | Uses tables and columns from the connected Oracle database. |
| Optional execution | SQL is never executed automatically. |
| Result rendering | Displays rows in the browser after execution. |
| Oracle support | Uses `oracledb` through SQLAlchemy. |
| Friendly errors | Shows useful Gemini, connection, privilege, and SQL errors. |
| Clean workspace | Includes a focused dark UI with readable SQL code cells. |

## Setup

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

4. Add your Gemini and Oracle credentials to `.env`.

5. Start the app:

   ```bash
   python3 app.py
   ```

6. Open [http://127.0.0.1:5001/#workspace](http://127.0.0.1:5001/#workspace).

## Database connection

The default Oracle connection uses:

```text
Host: localhost
Port: 1521
Service: FREEPDB1
```

The connected user needs the privileges required by the SQL it runs, such as `CREATE TABLE` and a tablespace quota for DDL.

## Project structure

```text
SQL AGENT/
├── agent.py        # Gemini and LangChain SQL generation
├── app.py          # Flask API and Oracle execution
├── index.html      # QueryPilot interface
├── requirements.txt
├── .env.example
└── .gitignore
```

## Safety notes

- `.env` is ignored and must never be committed.
- Review generated SQL before running it.
- DDL and DML changes are committed by the database transaction after execution.
- Use a restricted Oracle user for development and testing.
