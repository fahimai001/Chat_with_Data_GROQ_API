import trafilatura
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

MAX_CONTEXT_CHARS = 6000 

def fetch_website_content(url):
    """Fetches and extracts text content from the given URL."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return None


def truncate_content(content, max_chars=MAX_CONTEXT_CHARS):
    """Truncates the content to avoid exceeding token limits."""
    if content and len(content) > max_chars:
        return content[:max_chars]
    return content


def generate_answer_from_content(llm, content, question):
    """Generates an answer based on the provided website content."""
    content = truncate_content(content)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that answers questions based on the provided website content. Use the following context to answer the question:\n\n{context}"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": content, "question": question})
