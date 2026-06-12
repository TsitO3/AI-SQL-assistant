from google import genai
from schema import get_schema
import os
from dotenv import load_dotenv
import re
from db import get_db_type

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


MODEL_SQL = "gemini-2.5-flash"
MODEL_ANSWER = "gemma-4-31b-it"

MODEL_ANSWER = MODEL_SQL

DB_TYPE = get_db_type()

SYSTEM_PROMPT = f"""
You are an expert {DB_TYPE.upper()} database assistant.

You have access to the database schema.

Rules:

1. Use ONLY the tables and columns present in the schema.

2. If the question can be answered using SQL on the schema or database contents, generate a valid {DB_TYPE.upper()} query.

3. Questions about:
   - tables
   - columns
   - schema
   - row counts
   - database structure
   are considered valid questions.

4. Never invent tables, columns, or relationships.

5. Never use information outside the database.

6. You must detect indirect relationships between tables.
   Relationships can be:
   - direct foreign keys
   - or multi-hop via intermediate tables

If a relationship exists through joins, you MUST generate SQL.

7. If the question cannot be answered using the schema or data, respond EXACTLY:
NOT_IN_DATABASE

8. Return ONLY:
   - a valid {DB_TYPE.upper()} query
   - OR NOT_IN_DATABASE

9. Do not use markdown.

10. Never use SELECT * in JOIN queries.

11. Always explicitly select columns.

12. Always alias columns when joins are used to avoid duplicates.

13. Use SQL syntax compatible with {DB_TYPE.upper()}:
"""

DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE",
    "ALTER", "CREATE", "TRUNCATE",
    "ATTACH", "DETACH", "REPLACE"
]

def is_safe_sql(query: str) -> bool:

    q = query.upper()

    if ";" in query:
        return False

    # interdit si mot dangereux présent
    for word in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{word}\b", q):
            return False

    return True



def clean_sql(response: str):

    response = re.sub(r"```sql", "", response, flags=re.IGNORECASE)
    response = response.replace("```", "")

    response = response.strip().strip(";")

    return response


def generate_sql(question):
    schema = get_schema()
    db_type = get_db_type()
    print(db_type,"$$$$$$$$$$$$$$$$$$$$")

    prompt = f"""
        Database type: 
        {db_type}

        Schema:
        {schema}

        Question:
        {question}
    """

    response = client.models.generate_content(
        model=MODEL_SQL,
        contents=SYSTEM_PROMPT + "\n" + prompt
    )

    output = response.text.strip()


    if output == "NOT_IN_DATABASE":
        return None

    output = clean_sql(output)

    return output


def generate_answer(question, sql, df):

    prompt = f"""
        You are an AI database assistant.

        The user asked:

        {question}

        The SQL executed was:

        {sql}

        The result returned was:

        {df.to_string(index=False)}

        Instructions:

        - Answer the user's question directly.
        - Use natural language.
        - Be concise for simple questions.
        - If the question asks "how many", provide the number directly.
        - If the question asks for a list, summarize the list naturally.
        - If the result is large, provide insights and a summary.
        - Do not explain SQL.
        - Do not describe columns unless asked.
        """

    response = client.models.generate_content(
        model=MODEL_ANSWER,
        contents=prompt
    )

    return response.text