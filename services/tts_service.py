import requests
from config import MURF_API_KEY, MURF_TTS_ENDPOINT

def synthesize_speech(text: str, voice_id="en-US-natalie") -> list:
    if not MURF_API_KEY:
        raise RuntimeError("Missing Murf API key")
    audio_urls = []
    MAX_CHARS = 3000
    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api-key": MURF_API_KEY,
    }
    for chunk in chunks:
        resp = requests.post(
            MURF_TTS_ENDPOINT,
            headers=headers,
            json={"text": chunk, "voiceId": voice_id},
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("audioFile"):
            audio_urls.append(data["audioFile"])
    return audio_urls
