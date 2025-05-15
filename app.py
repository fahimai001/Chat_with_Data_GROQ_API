import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from src.db import create_database, execute_query
from src.helper_func import create_llm, generate_sql_query

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    st.error("Missing GROQ_API_KEY in .env file.")
    st.stop()


st.set_page_config(page_title="Text to SQL Query Generator", layout="wide")
st.title("Text to SQL Query Generator")


if "db_path" not in st.session_state:
    st.session_state.db_path = None
if "table_info" not in st.session_state:
    st.session_state.table_info = None
if "schema_details" not in st.session_state:
    st.session_state.schema_details = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


st.header("Upload Dataset")
uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx", "xls"], accept_multiple_files=True)


if uploaded_files and set(f.name for f in uploaded_files) != set(f.name for f in st.session_state.uploaded_files):
    st.session_state.uploaded_files = uploaded_files
    with st.spinner("Creating database..."):
        db_path, table_info, schema_details = create_database(uploaded_files)
        st.session_state.db_path = db_path
        st.session_state.table_info = table_info
        st.session_state.schema_details = schema_details
        st.success("Database created successfully!")


if st.session_state.table_info:
    with st.expander("View Database Schema"):
        for name, info in st.session_state.table_info.items():
            st.subheader(f"Table: {name}")
            st.write(f"Columns: {', '.join(info['columns'])}")
            st.dataframe(pd.DataFrame(info['sample_data']))


st.header("Generate SQL Query")


if st.session_state.db_path:
    question = st.text_area("Enter your question about the data:", height=100)
    if st.button("Generate SQL Query"):
        if question:
            with st.spinner("Generating SQL..."):
                llm = create_llm(api_key)
                sql = generate_sql_query(llm, st.session_state.schema_details, question)
                st.subheader("Generated SQL Query:")
                st.code(sql, language="sql")
                st.subheader("Query Results:")
                result = execute_query(sql, st.session_state.db_path)
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result)
                else:
                    st.error(f"Error: {result}")
        else:
            st.warning("Please enter a question.")
else:
    st.info("Please upload dataset files first.")
