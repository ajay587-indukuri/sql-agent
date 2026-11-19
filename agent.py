import os
import json

from dotenv import load_dotenv

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------------
# 1. DATABASE DATA: embedded directly in this Python file
# ---------------------------------------------------------
data = json.loads(r'''
{
    "database": "QueryPilot_DBMS_Lab",
    "dialect": "Oracle SQL / PL/SQL",
    "description": "Synthetic practice dataset covering concepts from DBMS Tasks 1–12. These records are illustrative, not copied from Oracle's HR sample schema.",
    "tables": {
        "DEPARTMENTS": {
            "columns": {
                "DEPARTMENT_ID": "NUMBER(4) PRIMARY KEY",
                "DEPARTMENT_NAME": "VARCHAR2(30)",
                "LOCATION": "VARCHAR2(30)"
            },
            "rows": [
                {
                    "DEPARTMENT_ID": 10,
                    "DEPARTMENT_NAME": "Administration",
                    "LOCATION": "Hyderabad"
                },
                {
                    "DEPARTMENT_ID": 20,
                    "DEPARTMENT_NAME": "Marketing",
                    "LOCATION": "Mumbai"
                },
                {
                    "DEPARTMENT_ID": 30,
                    "DEPARTMENT_NAME": "Engineering",
                    "LOCATION": "Bengaluru"
                },
                {
                    "DEPARTMENT_ID": 40,
                    "DEPARTMENT_NAME": "Finance",
                    "LOCATION": "Chennai"
                },
                {
                    "DEPARTMENT_ID": 50,
                    "DEPARTMENT_NAME": "Human Resources",
                    "LOCATION": "Pune"
                },
                {
                    "DEPARTMENT_ID": 60,
                    "DEPARTMENT_NAME": "Operations",
                    "LOCATION": "Kochi"
                }
            ]
        },
        "JOBS": {
            "columns": {
                "JOB_ID": "VARCHAR2(10) PRIMARY KEY",
                "JOB_TITLE": "VARCHAR2(35)",
                "MIN_SALARY": "NUMBER(8,2)",
                "MAX_SALARY": "NUMBER(8,2)"
            },
            "rows": [
                {
                    "JOB_ID": "AD_VP",
                    "JOB_TITLE": "Administration Vice President",
                    "MIN_SALARY": 12000,
                    "MAX_SALARY": 25000
                },
                {
                    "JOB_ID": "FI_MGR",
                    "JOB_TITLE": "Finance Manager",
                    "MIN_SALARY": 9000,
                    "MAX_SALARY": 18000
                },
                {
                    "JOB_ID": "IT_PROG",
                    "JOB_TITLE": "Programmer",
                    "MIN_SALARY": 5000,
                    "MAX_SALARY": 15000
                },
                {
                    "JOB_ID": "MK_REP",
                    "JOB_TITLE": "Marketing Representative",
                    "MIN_SALARY": 4000,
                    "MAX_SALARY": 9000
                },
                {
                    "JOB_ID": "HR_REP",
                    "JOB_TITLE": "HR Representative",
                    "MIN_SALARY": 4000,
                    "MAX_SALARY": 10000
                },
                {
                    "JOB_ID": "SA_REP",
                    "JOB_TITLE": "Sales Representative",
                    "MIN_SALARY": 5000,
                    "MAX_SALARY": 12000
                },
                {
                    "JOB_ID": "CLERK",
                    "JOB_TITLE": "Clerk",
                    "MIN_SALARY": 2000,
                    "MAX_SALARY": 5000
                }
            ]
        },
        "EMPLOYEES": {
            "columns": {
                "EMPLOYEE_ID": "NUMBER(6) PRIMARY KEY",
                "FIRST_NAME": "VARCHAR2(20)",
                "LAST_NAME": "VARCHAR2(25) NOT NULL",
                "EMAIL": "VARCHAR2(50) UNIQUE",
                "HIRE_DATE": "DATE",
                "JOB_ID": "VARCHAR2(10) REFERENCES JOBS(JOB_ID)",
                "SALARY": "NUMBER(8,2) DEFAULT 5000 CHECK (SALARY > 0)",
                "COMMISSION_PCT": "NUMBER(4,2) NULL",
                "MANAGER_ID": "NUMBER(6) REFERENCES EMPLOYEES(EMPLOYEE_ID)",
                "DEPARTMENT_ID": "NUMBER(4) REFERENCES DEPARTMENTS(DEPARTMENT_ID)"
            },
            "rows": [
                {
                    "EMPLOYEE_ID": 100,
                    "FIRST_NAME": "Steven",
                    "LAST_NAME": "King",
                    "EMAIL": "SKING",
                    "HIRE_DATE": "1998-06-17",
                    "JOB_ID": "AD_VP",
                    "SALARY": 24000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": null,
                    "DEPARTMENT_ID": 10
                },
                {
                    "EMPLOYEE_ID": 101,
                    "FIRST_NAME": "Neena",
                    "LAST_NAME": "Kochhar",
                    "EMAIL": "NKOCHHAR",
                    "HIRE_DATE": "1998-09-21",
                    "JOB_ID": "FI_MGR",
                    "SALARY": 17000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 100,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 102,
                    "FIRST_NAME": "Lex",
                    "LAST_NAME": "De Haan",
                    "EMAIL": "LDEHAAN",
                    "HIRE_DATE": "1999-01-13",
                    "JOB_ID": "IT_PROG",
                    "SALARY": 12000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 100,
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 103,
                    "FIRST_NAME": "Alexander",
                    "LAST_NAME": "Hunold",
                    "EMAIL": "AHUNOLD",
                    "HIRE_DATE": "1998-01-03",
                    "JOB_ID": "IT_PROG",
                    "SALARY": 9000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 102,
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 104,
                    "FIRST_NAME": "Bruce",
                    "LAST_NAME": "Ernst",
                    "EMAIL": "BERNST",
                    "HIRE_DATE": "2001-05-21",
                    "JOB_ID": "IT_PROG",
                    "SALARY": 6000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 103,
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 105,
                    "FIRST_NAME": "David",
                    "LAST_NAME": "Austin",
                    "EMAIL": "DAUSTIN",
                    "HIRE_DATE": "2002-06-25",
                    "JOB_ID": "IT_PROG",
                    "SALARY": 4800,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 103,
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 106,
                    "FIRST_NAME": "Nancy",
                    "LAST_NAME": "Greenberg",
                    "EMAIL": "NGREENBE",
                    "HIRE_DATE": "1998-08-17",
                    "JOB_ID": "FI_MGR",
                    "SALARY": 12000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 107,
                    "FIRST_NAME": "Daniel",
                    "LAST_NAME": "Faviet",
                    "EMAIL": "DFAVIET",
                    "HIRE_DATE": "2005-08-16",
                    "JOB_ID": "FI_MGR",
                    "SALARY": 9000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 106,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 108,
                    "FIRST_NAME": "John",
                    "LAST_NAME": "Chen",
                    "EMAIL": "JCHEN",
                    "HIRE_DATE": "2006-09-28",
                    "JOB_ID": "CLERK",
                    "SALARY": 3500,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 106,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 109,
                    "FIRST_NAME": "Ismael",
                    "LAST_NAME": "Sciarra",
                    "EMAIL": "ISCIARRA",
                    "HIRE_DATE": "2007-09-30",
                    "JOB_ID": "CLERK",
                    "SALARY": 3000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 106,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 110,
                    "FIRST_NAME": "Jose",
                    "LAST_NAME": "Urman",
                    "EMAIL": "JURMAN",
                    "HIRE_DATE": "2008-03-07",
                    "JOB_ID": "MK_REP",
                    "SALARY": 7800,
                    "COMMISSION_PCT": 0.1,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 20
                },
                {
                    "EMPLOYEE_ID": 111,
                    "FIRST_NAME": "Luis",
                    "LAST_NAME": "Popp",
                    "EMAIL": "LPOPP",
                    "HIRE_DATE": "2008-12-07",
                    "JOB_ID": "MK_REP",
                    "SALARY": 6900,
                    "COMMISSION_PCT": 0.15,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 20
                },
                {
                    "EMPLOYEE_ID": 112,
                    "FIRST_NAME": "Karen",
                    "LAST_NAME": "Colmenares",
                    "EMAIL": "KCOLMENA",
                    "HIRE_DATE": "2009-01-12",
                    "JOB_ID": "HR_REP",
                    "SALARY": 6500,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 50
                },
                {
                    "EMPLOYEE_ID": 113,
                    "FIRST_NAME": "Michael",
                    "LAST_NAME": "Hartstein",
                    "EMAIL": "MHARTSTE",
                    "HIRE_DATE": "2010-02-17",
                    "JOB_ID": "HR_REP",
                    "SALARY": 9000,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 50
                },
                {
                    "EMPLOYEE_ID": 114,
                    "FIRST_NAME": "Pat",
                    "LAST_NAME": "Fay",
                    "EMAIL": "PFAY",
                    "HIRE_DATE": "2011-08-17",
                    "JOB_ID": "SA_REP",
                    "SALARY": 5000,
                    "COMMISSION_PCT": 0.2,
                    "MANAGER_ID": 100,
                    "DEPARTMENT_ID": 60
                },
                {
                    "EMPLOYEE_ID": 115,
                    "FIRST_NAME": "Shanta",
                    "LAST_NAME": "Vollman",
                    "EMAIL": "SVOLLMAN",
                    "HIRE_DATE": "2012-04-10",
                    "JOB_ID": "SA_REP",
                    "SALARY": 5200,
                    "COMMISSION_PCT": 0.12,
                    "MANAGER_ID": 100,
                    "DEPARTMENT_ID": 60
                },
                {
                    "EMPLOYEE_ID": 116,
                    "FIRST_NAME": "Peter",
                    "LAST_NAME": "Tucker",
                    "EMAIL": "PTUCKER",
                    "HIRE_DATE": "2013-01-30",
                    "JOB_ID": "SA_REP",
                    "SALARY": 5200,
                    "COMMISSION_PCT": 0.15,
                    "MANAGER_ID": 100,
                    "DEPARTMENT_ID": 60
                },
                {
                    "EMPLOYEE_ID": 117,
                    "FIRST_NAME": "Susan",
                    "LAST_NAME": "Jones",
                    "EMAIL": "SJONES",
                    "HIRE_DATE": "2014-11-03",
                    "JOB_ID": "CLERK",
                    "SALARY": 3200,
                    "COMMISSION_PCT": null,
                    "MANAGER_ID": 106,
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 118,
                    "FIRST_NAME": "James",
                    "LAST_NAME": "Ford",
                    "EMAIL": "JFORD",
                    "HIRE_DATE": "2015-07-14",
                    "JOB_ID": "MK_REP",
                    "SALARY": 8000,
                    "COMMISSION_PCT": 0.05,
                    "MANAGER_ID": 101,
                    "DEPARTMENT_ID": 20
                }
            ]
        },
        "JOB_HISTORY": {
            "columns": {
                "EMPLOYEE_ID": "NUMBER(6)",
                "START_DATE": "DATE",
                "END_DATE": "DATE",
                "JOB_ID": "VARCHAR2(10)",
                "DEPARTMENT_ID": "NUMBER(4)"
            },
            "rows": [
                {
                    "EMPLOYEE_ID": 103,
                    "START_DATE": "1997-01-01",
                    "END_DATE": "1998-01-02",
                    "JOB_ID": "CLERK",
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 104,
                    "START_DATE": "1999-01-01",
                    "END_DATE": "2000-05-20",
                    "JOB_ID": "CLERK",
                    "DEPARTMENT_ID": 30
                },
                {
                    "EMPLOYEE_ID": 107,
                    "START_DATE": "2001-01-01",
                    "END_DATE": "2004-08-15",
                    "JOB_ID": "AD_VP",
                    "DEPARTMENT_ID": 40
                },
                {
                    "EMPLOYEE_ID": 110,
                    "START_DATE": "2005-01-01",
                    "END_DATE": "2007-03-06",
                    "JOB_ID": "CLERK",
                    "DEPARTMENT_ID": 20
                },
                {
                    "EMPLOYEE_ID": 114,
                    "START_DATE": "2008-01-01",
                    "END_DATE": "2010-08-16",
                    "JOB_ID": "MK_REP",
                    "DEPARTMENT_ID": 60
                }
            ]
        },
        "DEPT": {
            "columns": {
                "DEPTNO": "NUMBER(3) PRIMARY KEY",
                "DNAME": "VARCHAR2(10)",
                "LOC": "VARCHAR2(10)"
            },
            "rows": [
                {
                    "DEPTNO": 10,
                    "DNAME": "ADMIN",
                    "LOC": "HYDERABAD"
                },
                {
                    "DEPTNO": 20,
                    "DNAME": "MKTG",
                    "LOC": "MUMBAI"
                },
                {
                    "DEPTNO": 30,
                    "DNAME": "SALES",
                    "LOC": "BENGALURU"
                },
                {
                    "DEPTNO": 40,
                    "DNAME": "FINANCE",
                    "LOC": "CHENNAI"
                },
                {
                    "DEPTNO": 50,
                    "DNAME": "HR",
                    "LOC": "PUNE"
                }
            ]
        },
        "EMP": {
            "columns": {
                "EMPNO": "NUMBER(6) PRIMARY KEY CHECK (EMPNO > 100)",
                "ENAME": "VARCHAR2(30)",
                "JOB": "VARCHAR2(20)",
                "MGRID": "NUMBER(6)",
                "DEPTNO": "NUMBER(3) REFERENCES DEPT(DEPTNO)",
                "SAL": "NUMBER(7,2) DEFAULT 5000 NOT NULL",
                "COMM": "NUMBER(7,2) NULL",
                "DOB": "DATE"
            },
            "rows": [
                {
                    "EMPNO": 101,
                    "ENAME": "Ravi",
                    "JOB": "CLERK",
                    "MGRID": 105,
                    "DEPTNO": 10,
                    "SAL": 3500,
                    "COMM": null,
                    "DOB": "2002-04-12"
                },
                {
                    "EMPNO": 102,
                    "ENAME": "Anita",
                    "JOB": "ADMIN",
                    "MGRID": 105,
                    "DEPTNO": 20,
                    "SAL": 6200,
                    "COMM": null,
                    "DOB": "2001-09-03"
                },
                {
                    "EMPNO": 103,
                    "ENAME": "Kiran",
                    "JOB": "CLERK",
                    "MGRID": 105,
                    "DEPTNO": 30,
                    "SAL": 4200,
                    "COMM": null,
                    "DOB": "2003-01-22"
                },
                {
                    "EMPNO": 104,
                    "ENAME": "Meena",
                    "JOB": "ANALYST",
                    "MGRID": 106,
                    "DEPTNO": 40,
                    "SAL": 7800,
                    "COMM": 500,
                    "DOB": "2000-11-15"
                },
                {
                    "EMPNO": 105,
                    "ENAME": "Arjun",
                    "JOB": "MANAGER",
                    "MGRID": null,
                    "DEPTNO": 10,
                    "SAL": 12000,
                    "COMM": null,
                    "DOB": "1995-07-08"
                },
                {
                    "EMPNO": 106,
                    "ENAME": "Priya",
                    "JOB": "MANAGER",
                    "MGRID": null,
                    "DEPTNO": 40,
                    "SAL": 11000,
                    "COMM": null,
                    "DOB": "1996-02-19"
                },
                {
                    "EMPNO": 107,
                    "ENAME": "Suresh",
                    "JOB": "CLERK",
                    "MGRID": 105,
                    "DEPTNO": 50,
                    "SAL": 3900,
                    "COMM": null,
                    "DOB": "2002-12-01"
                },
                {
                    "EMPNO": 108,
                    "ENAME": "Divya",
                    "JOB": "SALESMAN",
                    "MGRID": 106,
                    "DEPTNO": 30,
                    "SAL": 5600,
                    "COMM": 1000,
                    "DOB": "2001-06-27"
                },
                {
                    "EMPNO": 109,
                    "ENAME": "Rahul",
                    "JOB": "ADMIN",
                    "MGRID": 106,
                    "DEPTNO": 20,
                    "SAL": 5100,
                    "COMM": null,
                    "DOB": "2000-03-14"
                },
                {
                    "EMPNO": 110,
                    "ENAME": "Sneha",
                    "JOB": "ANALYST",
                    "MGRID": 106,
                    "DEPTNO": 50,
                    "SAL": 8300,
                    "COMM": 750,
                    "DOB": "1999-10-05"
                },
                {
                    "EMPNO": 111,
                    "ENAME": "Vikram",
                    "JOB": "CLERK",
                    "MGRID": 105,
                    "DEPTNO": 30,
                    "SAL": 3700,
                    "COMM": null,
                    "DOB": "2003-08-30"
                }
            ]
        }
    },
    "concept_coverage": {
        "task_1_2": [
            "CREATE",
            "ALTER",
            "DROP",
            "TRUNCATE",
            "PRIMARY KEY",
            "FOREIGN KEY",
            "CHECK",
            "NOT NULL",
            "DEFAULT",
            "INSERT",
            "UPDATE",
            "DELETE"
        ],
        "task_3_5": [
            "SELECT",
            "DISTINCT",
            "WHERE",
            "BETWEEN",
            "IN",
            "LIKE",
            "IS NULL",
            "ORDER BY",
            "aliases",
            "arithmetic expressions",
            "COUNT",
            "SUM",
            "AVG",
            "MAX",
            "MIN",
            "GROUP BY",
            "HAVING",
            "string functions",
            "date functions",
            "NVL"
        ],
        "task_6": [
            "single-row subqueries",
            "multi-row subqueries",
            "ANY",
            "ALL",
            "correlated subqueries",
            "CREATE TABLE AS SELECT"
        ],
        "task_7": [
            "INNER JOIN",
            "LEFT OUTER JOIN",
            "FULL OUTER JOIN",
            "SELF JOIN",
            "UNION",
            "UNION ALL",
            "MINUS",
            "INTERSECT"
        ],
        "task_8": [
            "CREATE VIEW",
            "WITH CHECK OPTION",
            "WITH READ ONLY",
            "view metadata",
            "DML through views"
        ],
        "task_9": [
            "SEQUENCE",
            "INDEX",
            "PL/SQL variables",
            "SELECT INTO",
            "input parameters",
            "explicit cursors",
            "cursor loops"
        ],
        "task_10": [
            "SAVEPOINT",
            "ROLLBACK TO SAVEPOINT",
            "ROLLBACK",
            "COMMIT"
        ],
        "task_11": [
            "TRIGGER",
            "OLD",
            "NEW",
            "PROCEDURE",
            "FUNCTION",
            "parameters",
            "RETURN"
        ],
        "task_12": [
            "predefined exceptions",
            "user-defined exceptions",
            "RAISE",
            "PACKAGE specification",
            "PACKAGE body",
            "INSERT",
            "UPDATE",
            "DELETE",
            "retrieve data"
        ]
    },
    "notes": [
        "All rows are synthetic practice data.",
        "EMP and DEPT are separate custom tables; EMPLOYEES, DEPARTMENTS, JOBS and JOB_HISTORY form the HR-style practice schema.",
        "JSON stores schema metadata and rows. Views, sequences, indexes, transactions, triggers, procedures, functions, packages and exception handling must be implemented in Oracle SQL/PLSQL."
    ]
}
''')

# ---------------------------------------------------------
# 2. GEMINI MODEL
# ---------------------------------------------------------
# Load the API key from the .env file in this project folder.
# The file may contain either GEMINI_API_KEY=..., GOOGLE_API_KEY=..., or a
# raw key on the first non-comment line.
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    try:
        with open(env_path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                value = line.strip()
                if value and not value.startswith("#") and "=" not in value:
                    api_key = value
                    break
    except OSError as error:
        raise ValueError(f"Unable to read the .env file: {error}") from error

if not api_key:
    raise ValueError("Please set GEMINI_API_KEY or GOOGLE_API_KEY in the .env file.")

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    google_api_key=api_key
)

# ---------------------------------------------------------
# 3. PROMPT: pass the embedded JSON through {data}
# ---------------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are QueryPilot AI, an expert Oracle SQL and PL/SQL assistant.

The complete practice database schema and sample records are:
{data}

Use this database to answer the user's DBMS questions.
Support concepts from DBMS Lab Tasks 1–12:
- DDL, DML, DQL and constraints
- SQL operators, ORDER BY and SQL functions
- Aggregate functions, GROUP BY and HAVING
- Nested and correlated queries
- Joins and set operators
- Views, sequences and indexes
- PL/SQL blocks and cursors
- COMMIT, ROLLBACK and SAVEPOINT
- Triggers, procedures and functions
- Predefined/user-defined exceptions and packages

Rules:
1. Use Oracle SQL and PL/SQL syntax.
2. Use only tables and columns present in the supplied data.
3. EMP/DEPT are separate from EMPLOYEES/DEPARTMENTS/JOBS/JOB_HISTORY.
4. The sample records are synthetic, not the official Oracle HR dataset.
5. Generate code for review; do not claim that SQL or PL/SQL was executed.
6. Do not invent missing tables, columns, or records.
7. If the question requires information not present in the schema, say so.
8. Explain the query in clear, student-friendly language.

Format:
1. Understanding
2. SQL / PL/SQL Code
3. Explanation
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# ---------------------------------------------------------
# 4. AGENT EXECUTOR
# ---------------------------------------------------------
database_json = json.dumps(data, indent=2, ensure_ascii=False)

tools = []
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
querypilot_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    max_iterations=5,
    handle_parsing_errors=True
)

# ---------------------------------------------------------
# 5. ASK QUESTIONS AND INVOKE THE PIPELINE
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n========== QueryPilot AI | Gemini Agent ==========")
    print("Available tables:", ", ".join(data["tables"].keys()))
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask your DBMS question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("QueryPilot AI closed.")
            break

        if not question:
            continue

        try:
            response = querypilot_agent.invoke({
                "input": question,
                "data": database_json
            })

            output = response["output"]
            if isinstance(output, list):
                output = "\n".join(
                    item.get("text", "")
                    for item in output
                    if isinstance(item, dict) and item.get("type") == "text"
                )

            print("\nQueryPilot AI:")
            print(output)
            print("\n-----------------------------------------------\n")

        except Exception as error:
            print("\nError:", error)
            print("Check your API key, model access, and installed package versions.\n")
