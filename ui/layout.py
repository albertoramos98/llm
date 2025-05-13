import streamlit as st

def apply_custom_styles():
    custom_style = """
        <style>
        #MainMenu, footer {visibility: hidden;}
        .block-container {
            padding-top: 4rem;
            padding-bottom: 4rem;
            max-width: 800px;
            margin: auto;
        }
        .stTextInput>div>div>input {
            font-size: 1.1rem;
            height: 2.6rem;
            padding: 0.4rem;
        }
        h1 {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 2rem;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 50%;
            height: 2.6rem;
            width: 2.6rem;
            font-size: 1rem;
            padding: 0;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #3e8e41;
        }
        </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)
