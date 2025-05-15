from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_video_id(url):
    return extract.video_id(url)

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except:
        return None

def summarize_youtube(llm, transcript, url):
    if not transcript:
        return "No transcript available for this video."
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Summarize this YouTube video transcript in bullet points. Include key points and main takeaways.

Transcript:
{transcript}""")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript[:15000]})  