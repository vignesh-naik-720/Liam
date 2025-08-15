import os
import uuid
import logging
import threading
from flask import Flask, request, jsonify, send_from_directory, url_for
from config import OUTPUT_DIR, UPLOAD_DIR, FRONTEND_DIR
from services.stt_service import transcribe_audio
from services.llm_service import generate_response
from services.tts_service import synthesize_speech
from utils.fallback import ensure_fallback_audio, get_fallback_payload

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
logging.basicConfig(level=logging.INFO)

CHAT_STORE = {}
CHAT_LOCK = threading.Lock()

ensure_fallback_audio()

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/agent/chat/<session_id>", methods=["POST"])
def agent_chat(session_id):
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    ext = os.path.splitext(audio_file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    audio_file.save(filepath)

    try:
        input_text = transcribe_audio(filepath)
    except Exception as e:
        logging.exception("STT failed")
        return jsonify(get_fallback_payload({"error": "Speech-to-text failed"})), 200

    if not input_text:
        return jsonify(get_fallback_payload({"error": "Empty transcription"})), 200

    with CHAT_LOCK:
        CHAT_STORE.setdefault(session_id, []).append({"role": "user", "text": input_text, "audio": url_for("serve_uploads", fname=filename)})

    try:
        output_text = generate_response(CHAT_STORE[session_id][-20:])
    except Exception:
        logging.exception("LLM failed")
        return jsonify(get_fallback_payload({"transcription": input_text, "error": "LLM failed"})), 200

    try:
        audio_urls = synthesize_speech(output_text)
    except Exception:
        logging.exception("TTS failed")
        return jsonify(get_fallback_payload({"transcription": input_text, "llm_response": output_text, "error": "TTS failed"})), 200

    with CHAT_LOCK:
        CHAT_STORE[session_id].append({"role": "assistant", "text": output_text, "audio_urls": audio_urls})

    return jsonify({"transcription": input_text, "llm_response": output_text, "audio_urls": audio_urls})

@app.route("/uploads/<path:fname>")
def serve_uploads(fname):
    return send_from_directory(UPLOAD_DIR, fname)

@app.route("/fallback.mp3")
def serve_fallback():
    return send_from_directory(FRONTEND_DIR, "fallback.mp3")

@app.route("/agent/history/<session_id>", methods=["GET"])
def get_history(session_id):
    with CHAT_LOCK:
        return jsonify({"session_id": session_id, "history": CHAT_STORE.get(session_id, [])})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
