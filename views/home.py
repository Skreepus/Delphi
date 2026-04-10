import streamlit as st

def render():
    st.markdown("""
    <div class="hero">
        <p class="eyebrow">Welcome</p>
        <h1>The <em>Delphi</em><br>Project</h1>
        <p>Your content goes here.<br>This is the home page.</p>
    </div>
    """, unsafe_allow_html=True)