import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="शिक्षा सेतु - एक नई उड़ान", page_icon="🚀", layout="centered")
st.title("🚀 शिक्षा सेतु - एक नई उड़ान")
st.caption("Aapka AI Study Companion | Super Fast & Responsive")

# API Client initialization
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY", None)
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY missing hai! Streamlit Cloud Secrets me add karein.")
        st.stop()
    return genai.Client(api_key=api_key.strip())

client = get_client()

SYSTEM_INSTRUCTION = (
    "Aap 'Shiksha Setu - Ek Nayi Udan' AI hain, ek encouraging aur helpful student mentor. "
    "Aap school/college students ke sawalon ke jawab aasan bhasha (Hindi/Hinglish) mein dete hain. "
    "Jawab to-the-point aur aasan bhasha mein rakhein."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Apna sawal yahan poochein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    def fast_stream():
        recent = st.session_state.messages[-4:]
        context_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent])

        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=context_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=300,
                temperature=0.7
            )
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    with st.chat_message("assistant"):
        bot_reply = st.write_stream(fast_stream)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
