from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript
)
from pytube import extract
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    """
    return extract.video_id(url)


def get_transcript(video_id: str, target_language: str = "en") -> str | None:
    """
    Fetch the transcript for video_id. If it exists in another language,
    auto-translate it into `target_language` before returning.
    """
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)


        try:
            transcript = transcripts.find_manually_created_transcript(
                transcripts._manually_created_transcripts.keys()
            )
        except Exception:

            transcript = transcripts.find_generated_transcript(
                transcripts._generated_transcripts.keys()
            )


        if transcript.language_code != target_language:
            transcript = transcript.translate(target_language)


        segments = transcript.fetch()
        return " ".join(segment.text for segment in segments)

    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript):
        return None


def summarize_youtube(llm, transcript: str | None, url: str) -> str:
    """
    Given an LLM and the transcript text, return a bullet-point summary.
    """
    if not transcript:
        return "No transcript available for this video."

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Summarize this YouTube video transcript in bullet points.
Include key points and main takeaways.

Transcript:
{transcript}""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript[:15000]})
