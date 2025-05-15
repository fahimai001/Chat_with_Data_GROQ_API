import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from src.db import create_database, execute_query
from src.helper_func import create_llm, generate_sql_query
from src.web import fetch_website_content, generate_answer_from_content
from src.youtube import get_video_id, get_transcript, summarize_youtube

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Missing GROQ_API_KEY in .env file.")
    st.stop()

st.set_page_config(page_title="Multi-Feature AI Assistant", layout="wide")
st.title("Multi-Feature AI Assistant")


tab1, tab2, tab3 = st.tabs(["Database Query", "Website QA", "YouTube Summary"])

with tab1:
    st.header("Database Query Feature")
    
    if "db_path" not in st.session_state:
        st.session_state.db_path = None
    
    st.subheader("Upload Dataset")
    uploaded_files = st.file_uploader("Upload CSV/Excel files", type=["csv", "xlsx", "xls"], 
                                    accept_multiple_files=True, key="db_uploader")
    
    if uploaded_files and set(f.name for f in uploaded_files) != set(f.name for f in st.session_state.get("uploaded_files", [])):
        st.session_state.uploaded_files = uploaded_files
        with st.spinner("Creating database..."):
            db_path, table_info, schema_details = create_database(uploaded_files)
            st.session_state.db_path = db_path
            st.session_state.table_info = table_info
            st.session_state.schema_details = schema_details
            st.success("Database created successfully!")
    


    if st.session_state.get("table_info"):
        schema_expander = st.expander("View Database Schema")
        with schema_expander:
            for name, info in st.session_state.table_info.items():
                st.subheader(f"Table: {name}")
                st.write(f"Columns: {', '.join(info['columns'])}")
                st.dataframe(pd.DataFrame(info['sample_data']))
    


    if st.session_state.db_path:
        st.subheader("Generate SQL Query")
        question = st.text_area("Enter your data question:", height=100, key="sql_question")
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

with tab2:
    st.header("Website Question Answering")
    web_url = st.text_input("Enter website URL:")
    web_question = st.text_input("Question about the website content:")
    
    if st.button("Get Answer"):
        if web_url and web_question:
            with st.spinner("Analyzing website..."):
                context = fetch_website_content(web_url)
                if context.startswith("Error"):
                    st.error(context)
                else:
                    llm = create_llm(api_key)
                    answer = generate_answer_from_content(llm, context, web_question)
                    st.subheader("Answer:")
                    st.write(answer)
        else:
            st.warning("Please provide both URL and question")


with tab3:
    st.header("YouTube Video Summarizer")
    yt_url = st.text_input("Enter YouTube Video URL:")
    
    if st.button("Summarize Video"):
        if yt_url:
            with st.spinner("Processing video..."):
                try:
                    video_id = get_video_id(yt_url)
                    transcript = get_transcript(video_id)
                    llm = create_llm(api_key)
                    summary = summarize_youtube(llm, transcript, yt_url)
                    st.subheader("Video Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error processing video: {str(e)}")
        else:
            st.warning("Please enter a YouTube URL")