import streamlit as st
import streamlit.components.v1 as components
import json
import os
from google import genai
from google.genai import types
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
    page_title="शिक्षा सेतु - एक नई उड़ान",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 शिक्षा सेतु - एक नई उड़ान")
st.caption("Superfast Voice-to-Voice & Text AI Companion")

# 1. API Client
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY", None)
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY missing hai! Streamlit Cloud Secrets mein key add karein.")
        st.stop()
    return genai.Client(api_key=api_key.strip())

client = get_client()

# 2. Fast Audio Persona (Short & Clear)
SYSTEM_INSTRUCTION = (
    "Aap 'Shiksha Setu - Ek Nayi Udan' AI hain. "
    "Rule: Aasan bhasha (Hindi/Hinglish) mein sirf 2 se 3 lines ke andar "
    "seedha jawab dein taaki bolne aur sunne mein bilkul natural aur fast lage. "
    "Special symbols jaise *, #, ya markdown bullets use na karein."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Zero-Lag Browser TTS (Seedhe speaker se aawaz niklegi)
def speak_in_browser(text):
    safe_text = json.dumps(text)
    js_code = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance({safe_text});
            utterance.lang = 'hi-IN';
            utterance.rate = 1.05;
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    components.html(js_code, height=0, width=0)

# 4. Quick Suggestion Buttons
st.markdown("💡 **Quick Topics:**")
q1, q2, q3, q4 = st.columns(4)
btn_prompt = None

with q1:
    if st.button("🔬 Science"):
        btn_prompt = "Science kya hai aur iske fayde kya hain?"
with q2:
    if st.button("📐 Maths Trick"):
        btn_prompt = "Koi aasan maths calculation trick bataiye."
with q3:
    if st.button("🇮🇳 Chandrayaan"):
        btn_prompt = "Chandrayaan mission ke bare mein 2 line bataiye."
with q4:
    if st.button("🤖 AI Kya Hai"):
        btn_prompt = "AI kya hota hai aasan bhasha mein samjhayein."

st.divider()

# Purani chat render karein
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. Dual Input: Mic + Text
col_mic, col_txt = st.columns([1, 4])

with col_mic:
    voice_input = speech_to_text(
        language='hi-IN',
        start_prompt="🎙️ Bolien",
        stop_prompt="⏹️ Rukiye",
        key='mic_btn'
    )

with col_txt:
    text_input = st.chat_input("Ya sawal yahan likhein...")

# Jo bhi input pehle mile
final_prompt = btn_prompt or voice_input or text_input

# 6. Instant Streaming & Speech Execution
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.write(final_prompt)

    def fast_stream():
        recent = st.session_state.messages[-4:]
        context_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent])

        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=context_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=150,
                temperature=0.6
            )
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    with st.chat_message("assistant"):
        bot_reply = st.write_stream(fast_stream)

    # Text aate hi direct speaker bolega
    speak_in_browser(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
