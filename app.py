import streamlit as st
import streamlit.components.v1 as components
import json
import os
from groq import Groq
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
    page_title="शिक्षा सेतु - एक नई उड़ान",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 शिक्षा सेतु - एक नई उड़ान")
st.caption("Ultra-Fast Voice & Chat Study Companion (Powered by Groq)")

# 1. API Key Clean & Safe Verification
raw_key = st.secrets.get("GROQ_API_KEY", None) or os.environ.get("GROQ_API_KEY", None)

if not raw_key:
    st.error("⚠️ GROQ_API_KEY Secrets me nahi mili! 'Manage app -> Settings -> Secrets' check karein.")
    st.stop()

api_key = str(raw_key).strip().replace('"', '').replace("'", "")

if not api_key.startswith("gsk_"):
    st.error(f"⚠️ Invalid Key Format: Key 'gsk_' se shuru honi chahiye. Aapki key '{api_key[:4]}...' se shuru ho rahi hai.")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_INSTRUCTION = (
    "Aap 'Shiksha Setu - Ek Nayi Udan' AI hain. "
    "Aap school/college students ke concepts aasan Hindi/Hinglish mein 2-3 lines mein samjhate hain. "
    "Jawab to-the-point aur encouraging rakhein. Markdown symbols jaise *, # use na karein."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Browser Audio Output
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

# 3. Quick Topics Buttons
st.markdown("💡 **Quick Topics:**")
q1, q2, q3, q4 = st.columns(4)
btn_prompt = None

with q1:
    if st.button("🔬 Science"):
        btn_prompt = "Science kya hai aur iska main use kya hai?"
with q2:
    if st.button("📐 Maths"):
        btn_prompt = "Maths calculation ki koi aasan trick bataiye."
with q3:
    if st.button("🇮🇳 Itihaas"):
        btn_prompt = "Bharat ke itihas ke bare mein do line bataiye."
with q4:
    if st.button("🤖 AI"):
        btn_prompt = "AI kya hota hai aasan shabdo mein samjhayein."

st.divider()

# 4. Old Messages Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. Dual Inputs (Mic + Chat)
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

final_prompt = btn_prompt or voice_input or text_input

# 6. Stream Response
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.write(final_prompt)

    def groq_stream():
        messages_payload = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
        for m in st.session_state.messages[-4:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
                max_tokens=200,
                temperature=0.6,
                stream=True
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"⚠️ Groq API Error: {str(e)}"

    with st.chat_message("assistant"):
        bot_reply = st.write_stream(groq_stream)

    speak_in_browser(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
