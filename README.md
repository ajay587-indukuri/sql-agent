# QueryPilot

QueryPilot is a Flask and Gemini assistant for generating Oracle SQL and optionally executing it against a configured Oracle database.

## Run locally

1. Copy `.env.example` to `.env` and add your Gemini and Oracle credentials.
2. Install the dependencies:

   ```bash
   pip install flask python-dotenv sqlalchemy oracledb langchain langchain-classic langchain-google-genai
   ```

3. Start the app:

   ```bash
   python3 app.py
   ```

4. Open `http://127.0.0.1:5001/#workspace`.

SQL is generated for review first. Use **Run in database** only when you want to execute it.
