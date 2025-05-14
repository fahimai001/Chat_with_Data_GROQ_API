import pandas as pd
import sqlite3
import re
from langchain.schema import HumanMessage, SystemMessage

def get_schema_from_df(df, table_name):
    columns = df.columns.tolist()
    datatypes = df.dtypes.astype(str).tolist()
    schema = f"Table: {table_name}\nColumns:\n"
    for col, dtype in zip(columns, datatypes):
        sql_type = "TEXT"
        if "int" in dtype.lower():
            sql_type = "INTEGER"
        elif "float" in dtype.lower():
            sql_type = "REAL"
        elif "date" in dtype.lower():
            sql_type = "DATE"
        schema += f"- {col} ({sql_type})\n"
    return schema

def get_sample_data(df, n=5):
    return df.head(n).to_string()

def extract_sql_query(response):
    sql_pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(sql_pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    sql_pattern = r"SELECT\s+.*?(?:;|$)"
    match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
    return match.group(0).strip() if match else response

def generate_sql_query(llm, question, table_schema, sample_data, table_name):
    prompt_template = """
You are an expert SQL query generator. Your task is to convert natural language questions into precise SQL queries.

DATABASE SCHEMA:
{schema}

SAMPLE DATA:
{sample_data}

GUIDELINES:
1. Generate only the SQL query without explanations.
2. Only use the columns that exist in the provided schema.
3. Don't make assumptions about columns not in the schema.
4. Keep the SQL syntax simple and standards-compliant.
5. Place the SQL query between ```sql and ``` markers.
6. Focus on generating a query that answers the question correctly.
7. Don't hallucinate tables or columns.
8. If the question cannot be answered with the given schema, say "Cannot generate SQL query: [reason]".

Question: {question}

SQL Query (for {table_name}):
```sql
"""
    prompt = prompt_template.format(
        schema=table_schema,
        sample_data=sample_data,
        question=question,
        table_name=table_name
    )
    messages = [
        SystemMessage(content="You are an expert SQL query generator."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages).content
    return extract_sql_query(response)

def create_temp_db(df, table_name):
    conn = sqlite3.connect(':memory:')
    df.to_sql(table_name, conn, index=False)
    return conn

def execute_query(conn, query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        return str(e)
