from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    audio: bytes  # raw audio file

class ChatResponse(BaseModel):
    transcription: Optional[str]
    llm_response: Optional[str]
    audio_urls: List[str] = []
    fallback_text: Optional[str] = None
    error: Optional[str] = None
