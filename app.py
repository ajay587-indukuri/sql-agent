
import os
import re
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from sqlalchemy import create_engine, inspect, text

from agent import data, querypilot_agent
import json

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)

database_json = json.dumps(data, indent=2, ensure_ascii=False)

def oracle_engine():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST", "localhost")
    port = os.getenv("ORACLE_PORT", "1521")
    service_name = os.getenv("ORACLE_SERVICE") or os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1")

    if not user or not password:
        raise RuntimeError(
            "Oracle is not configured. Set ORACLE_USER and ORACLE_PASSWORD in .env."
        )

    return create_engine(
        f"oracle+oracledb://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/?service_name={quote_plus(service_name)}",
        pool_pre_ping=True,
    )

def live_schema():
    inspector = inspect(oracle_engine())
    tables = {}
    for table_name in inspector.get_table_names():
        tables[table_name] = {
            "columns": {
                column["name"]: str(column["type"])
                for column in inspector.get_columns(table_name)
            }
        }
    return json.dumps({"database": "Oracle", "tables": tables}, indent=2)

def sql_from_response(response):
    match = re.search(r"```(?:sql|plsql)?\s*([\s\S]*?)```", response, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def split_sql(sql):
    cleaned = re.sub(r"--[^\r\n]*", "", sql).strip()
    if re.match(r"(?is)^(begin|declare|create\s+or\s+replace)", cleaned):
        return [cleaned.rstrip(";").rstrip("/").strip()]

    statements = []
    current = []
    quoted = False
    index = 0
    while index < len(cleaned):
        character = cleaned[index]
        if character == "'":
            current.append(character)
            if quoted and index + 1 < len(cleaned) and cleaned[index + 1] == "'":
                current.append("'")
                index += 1
            else:
                quoted = not quoted
        elif character == ";" and not quoted:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(character)
        index += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements

def execute_sql(sql):
    if not sql:
        return {"executed": False, "error": "No SQL code block was generated."}

    print(f"\n[QueryPilot] SQL:\n{sql}", flush=True)
    with oracle_engine().begin() as conn:
        row_count = 0
        columns = None
        rows = []
        for statement in split_sql(sql):
            if statement.upper() in {"COMMIT", "ROLLBACK"}:
                continue
            result = conn.execute(text(statement))
            if result.returns_rows:
                columns = list(result.keys())
                rows = [dict(row) for row in result.mappings().fetchmany(100)]
            elif result.rowcount and result.rowcount > 0:
                row_count += result.rowcount

        if columns is None:
            print(f"[QueryPilot] Executed successfully: {row_count} row(s) changed.", flush=True)
            return {"executed": True, "row_count": row_count}
        print(f"[QueryPilot] Result: {len(rows)} row(s)", flush=True)
        print(" | ".join(columns), flush=True)
        for row in rows:
            print(" | ".join(str(row.get(column, "")) for column in columns), flush=True)
        return {
            "executed": True,
            "columns": columns,
            "rows": [[str(row.get(column, "")) for column in columns] for row in rows],
            "row_count": len(rows),
        }

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/api/oracle/status")
def oracle_status():
    try:
        with oracle_engine().connect() as conn:
            conn.execute(text("SELECT 1 FROM dual"))
        return jsonify({
            "connected": True,
            "service": os.getenv("ORACLE_SERVICE") or os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1"),
        })
    except Exception as error:
        return jsonify({"connected": False, "error": str(error)}), 503

@app.route("/api/schema")
def schema():
    return jsonify(data)

@app.route("/ask", methods=["POST"])
def call():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        schema_json = live_schema()
        response = querypilot_agent.invoke({
            "input": question,
            "data": schema_json
        })

        output = response["output"]
        if isinstance(output, list):
            output = "\n".join(
                item.get("text", "")
                for item in output
                if isinstance(item, dict) and item.get("type") == "text"
            )

        return jsonify({"response": output, "sql": sql_from_response(output)})
    except Exception as error:
        message = str(error)
        if "429" in message or "RESOURCE_EXHAUSTED" in message or "quota" in message.lower():
            return jsonify({
                "error": "Gemini quota exceeded. Add billing or wait for the quota to reset, then try again."
            }), 429
        return jsonify({"error": f"Assistant request failed: {message}"}), 500

@app.route("/execute", methods=["POST"])
def execute():
    payload = request.get_json(silent=True) or {}
    sql = payload.get("sql", "").strip()
    if not sql:
        return jsonify({"error": "sql is required"}), 400

    try:
        return jsonify(execute_sql(sql))
    except Exception as error:
        return jsonify({"executed": False, "error": str(error)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
