import streamlit as st


def fmt(x):
    return f"{int(round(x)):,}"


def load_css(path):
    css = path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
