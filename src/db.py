import os
import sqlite3
import pandas as pd

def create_database(uploaded_files):
    db_path = "database/user_database.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    table_info = {}


    for file in uploaded_files:
        ext = file.name.split('.')[-1].lower()
        df = pd.read_csv(file) if ext == 'csv' else pd.read_excel(file)
        table_name = ''.join(c if c.isalnum() else '_' for c in file.name.split('.')[0])
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        table_info[table_name] = {
            "columns": [col[1] for col in columns],
            "sample_data": df.head(5).to_dict('records')
        }



    schema = get_schema_details(conn)
    conn.close()
    return db_path, table_info, schema



def get_schema_details(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()
        col_info = ', '.join([f"{col[1]} ({col[2]})" for col in cols])
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample = cursor.fetchall()
        schema.append(f"Table: {table_name}\nColumns: {col_info}\nSample data: {sample}\n")
    return "\n".join(schema)



def execute_query(query, db_path):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return str(e)
