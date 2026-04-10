import streamlit as st
import base64
from pathlib import Path


def get_base64_video(video_path):
    file = Path(video_path)
    if not file.exists():
        return ""
    video_bytes = file.read_bytes()
    encoded = base64.b64encode(video_bytes).decode()
    return f"data:video/mp4;base64,{encoded}"


def render():
    video_src = get_base64_video("assets/stars.mp4")

    st.markdown("""<style>
    .video-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        overflow: hidden;
        pointer-events: none;
    }
    .video-bg video {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        min-width: 100%;
        min-height: 100%;
        object-fit: cover;
        opacity: 0.35;
    }
    </style>""", unsafe_allow_html=True)

    if video_src:
        st.markdown(f"""<div class="video-bg">
<video autoplay muted loop playsinline>
<source src="{video_src}" type="video/mp4">
</video>
</div>""", unsafe_allow_html=True)