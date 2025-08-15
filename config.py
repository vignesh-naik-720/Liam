import os
from dotenv import load_dotenv

load_dotenv()

MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MURF_TTS_ENDPOINT = "https://api.murf.ai/v1/speech/generate"

OUTPUT_DIR = "generated_audio"
UPLOAD_DIR = "uploads"
FRONTEND_DIR = "frontend"

FALLBACK_FILENAME = "fallback.mp3"
FALLBACK_TEXT = "I'm having trouble connecting right now. Please try again later."
