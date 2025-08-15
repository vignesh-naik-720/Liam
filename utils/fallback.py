import os
import logging
from gtts import gTTS
from config import FALLBACK_FILENAME, FALLBACK_TEXT, FRONTEND_DIR

def ensure_fallback_audio():
    path = os.path.join(FRONTEND_DIR, FALLBACK_FILENAME)
    if not os.path.exists(path):
        try:
            logging.info("Generating fallback audio...")
            tts = gTTS(text=FALLBACK_TEXT, lang="en")
            tts.save(path)
            logging.info(f"Fallback audio saved to {path}")
        except Exception as e:
            logging.error("Failed to generate fallback audio: %s", e)
    return path

def get_fallback_payload(extra=None):
    payload = {
        "fallback_text": FALLBACK_TEXT,
        "audio_urls": [f"/{FALLBACK_FILENAME}"] if os.path.exists(os.path.join(FRONTEND_DIR, FALLBACK_FILENAME)) else []
    }
    if extra:
        payload.update(extra)
    return payload
