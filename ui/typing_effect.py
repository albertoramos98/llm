import streamlit as st
import time

def render_typing_effect(text: str, complemento: str = ""):
    words = text.split()
    typed_text = ""
    content_box = st.empty()
    delay = 0.1 if len(words) < 20 else 0.07 if len(words) < 50 else 0.05
    for word in words:
        typed_text += word + " "
        content_box.markdown(f"<p style='font-size:1.2rem'>{typed_text.strip()}</p>", unsafe_allow_html=True)
        time.sleep(delay)
    final = f"<p style='font-size:1.2rem'>{typed_text.strip()}</p>"
    if complemento:
        final += f"<p style='font-size:1.1rem; color:gray'><em>{complemento}</em></p>"
    content_box.markdown(final, unsafe_allow_html=True)
