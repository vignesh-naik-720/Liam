import assemblyai as aai
import logging
from config import ASSEMBLYAI_API_KEY

def transcribe_audio(filepath: str) -> str:
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("Missing AssemblyAI API key")
    aai.settings.api_key = ASSEMBLYAI_API_KEY
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filepath)
    if transcript.status == "error":
        raise RuntimeError(transcript.error)
    return transcript.text.strip()
