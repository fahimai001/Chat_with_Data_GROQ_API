import trafilatura
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def fetch_website_content(url):
    """Fetches and extracts text content from the given URL."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return None


def generate_answer_from_content(llm, content, question):
    """Generates an answer based on the provided website content."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that answers questions based on the provided website content. Use the following context to answer the question:\n\n{context}"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": content, "question": question})