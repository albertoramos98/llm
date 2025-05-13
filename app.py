import streamlit as st
from hubia_app.core.engine import auto_generate_and_run_query
from hubia_app.core.history import init_history_db
from hubia_app.ui.layout import apply_custom_styles
from hubia_app.ui.typing_effect import render_typing_effect

init_history_db()
st.set_page_config(page_title="HuB-IA", page_icon="🏦", layout="centered")
apply_custom_styles()

st.markdown('<h1 aria-label="assistente HuB-IA">O que você quer saber?</h1>', unsafe_allow_html=True)

with st.form(key="consulta_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        question = st.text_input("Pergunte alguma coisa", label_visibility="collapsed", placeholder="Ex: Qual foi o IPCA em Recife?", key="question")
    with col2:
        submit = st.form_submit_button("⬆", use_container_width=True)

if submit and question.strip():
    try:
        resposta = auto_generate_and_run_query(question.strip())
        render_typing_effect(resposta["interpretacao"])
    except Exception as e:
        st.error(f"Erro: {e}")
