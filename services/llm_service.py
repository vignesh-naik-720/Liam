import google.generativeai as genai
import logging
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_response(messages: list) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing Gemini API key")
    convo_lines = [f"{'User' if m['role']=='user' else 'Assistant'}: {m['text']}" for m in messages]
    convo_lines.append("Assistant:")
    final_prompt = "\n".join(convo_lines)
    model = genai.GenerativeModel("gemini-2.5-flash")
    llm_response = model.generate_content(final_prompt)
    return llm_response.text.strip() if hasattr(llm_response, "text") else str(llm_response)
