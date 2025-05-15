import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def create_llm(api_key):
    return ChatGroq(model="gemma2-9b-it", temperature=0.1, groq_api_key=api_key)


def generate_sql_query(llm, schema, question):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert SQL query generator. Your job is to convert natural language questions into SQLite SQL queries.

Guidelines:
1. Only output valid SQL queries for SQLite
2. Return only the query without explanation or markdown
3. Use exact table and column names from the schema

Schema:
         
{schema}"""),
        ("human", "{question}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"schema": schema, "question": question})
