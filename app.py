import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.helper_func import (
    get_schema_from_df, get_sample_data, extract_sql_query,
    generate_sql_query, create_temp_db, execute_query
)

load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="gemma2-9b-it")

def main():
    st.title("Text to SQL Query Generator")
    st.write("Upload your dataset and ask questions to get SQL queries")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        table_name = st.text_input("Enter a table name for your dataset", "my_table")
        schema = get_schema_from_df(df, table_name)
        sample_data = get_sample_data(df)
        conn = create_temp_db(df, table_name)

        question = st.text_area("Ask a question about your data", "")
        if st.button("Generate SQL Query") and question:
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql_query(llm, question, schema, sample_data, table_name)

            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            st.subheader("Query Results")
            results = execute_query(conn, sql_query)
            if isinstance(results, pd.DataFrame):
                st.dataframe(results)
            else:
                st.error(f"Error executing query: {results}")

if __name__ == "__main__":
    main()
