import streamlit as st
import base64
from pathlib import Path


def get_base64_image(image_path):
    img_bytes = Path(image_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    suffix = Path(image_path).suffix.replace(".", "")
    if suffix == "jpg":
        suffix = "jpeg"
    return f"data:image/{suffix};base64,{encoded}"


def render():
    earth_img = get_base64_image("assets/earth.jpg")

    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&display=swap');

    @keyframes fadeSlideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes glowPulse {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
    }}
    @keyframes earthFadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 0.15; }}
    }}

    .about-page {{
        max-width: 900px;
        margin: 0 auto;
        padding: 4rem 2rem;
        position: relative;
        z-index: 2;
    }}

    .bg-layers {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }}
    .bg-earth {{
        position: absolute;
        bottom: -42%;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        max-width: 900px;
        opacity: 0;
        visibility: visible;
        mask-image: radial-gradient(ellipse 75% 75% at center, black 30%, transparent 70%);
        -webkit-mask-image: radial-gradient(ellipse 75% 75% at center, black 30%, transparent 70%);
        animation: earthFadeIn 0.6s ease-out 0.2s forwards;
                
        
                
    }}

    .about-section {{
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out;
        position: relative;
        z-index: 2;
    }}
    .about-section:nth-child(2) {{ animation-delay: 0.1s; }}
    .about-section:nth-child(4) {{ animation-delay: 0.2s; }}
    .about-section:nth-child(6) {{ animation-delay: 0.3s; }}

    .about-section-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.9rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1rem;
        text-align: center;
    }}
    .about-section h2 {{
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 2.8rem;
        color: #e8e2d9;
        margin-bottom: 1.2rem;
        line-height: 1.2;
        text-align: center;
    }}
    .about-section p {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.05rem;
        color: #6b6560;
        line-height: 2;
        max-width: 700px;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
    }}

    .fancy-divider {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 0 4rem 0;
        position: relative;
        z-index: 2;
    }}
    .fancy-divider .line {{
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2a2a2a, transparent);
    }}
    .fancy-divider .diamond {{
        color: #c9a96e;
        font-size: 0.5rem;
        animation: glowPulse 3s ease-in-out infinite;
    }}

    .team-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
        margin-top: 1.5rem;
    }}
    .team-card {{
        background: rgba(22, 22, 22, 0.85);
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 2.5rem 2.5rem;
        text-align: center;
        transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }}
    .team-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #c9a96e, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .team-card:hover {{
        border-color: #c9a96e;
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(201,169,110,0.08);
    }}
    .team-card:hover::before {{
        opacity: 1;
    }}
    .team-card .name {{
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.6rem;
        color: #e8e2d9;
        margin-bottom: 0.4rem;
    }}
    .team-card .role {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.9rem;
        color: #6b6560;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }}
    .team-card .card-line {{
        width: 30px;
        height: 1px;
        background: #2a2a2a;
        margin: 0 auto;
    }}

    .footer-line {{
        margin-top: 5rem;
        text-align: center;
    }}
    .footer-line p {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.95rem;
        letter-spacing: 0.15em;
        text-transform: lowercase;
        color: #e8e2d9;
    }}

    @media (max-width: 768px) {{
        .about-page {{ padding: 2.5rem 1rem 3rem !important; }}
        .about-section h2 {{ font-size: clamp(1.75rem, 7vw, 2.8rem) !important; }}
        .about-section p {{ font-size: 0.98rem !important; max-width: 100% !important; }}
        .team-grid {{ grid-template-columns: 1fr !important; gap: 1.5rem !important; }}
        .team-card {{ padding: 1.75rem 1.25rem !important; }}
    }}
    </style>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="bg-layers">
<img class="bg-earth" src="{earth_img}" alt="">
</div>

<div class="about-page">

<div class="about-section">
<p class="about-section-label">01 — Our Goal</p>
<h2>Sustainable Satellite Usage</h2>
<p>As low-Earth orbit becomes increasingly congested, the need for responsible satellite operations has never been greater. Sustainability in space starts with transparency. Our goal is to give operators, regulators, and insurers the tools to make informed decisions and hold the space industry accountable for the orbital environment we all share.</p>
</div>

<div class="fancy-divider">
<div class="line"></div>
<span class="diamond">◆</span>
<div class="line"></div>
</div>

<div class="about-section">
<p class="about-section-label">02 — Our Innovation</p>
<h2>Predictions Based on ML</h2>
<p>We combine historical and real-time satellite data to build a comprehensive picture of orbital risk, one that goes far beyond what any single data source can offer. With our data in conjunction with the rules and regulations set by the UN Office for Outer Space Affairs, we created the Delphi risk compliance scoring system (DRCS). A global satellite metric that not only assesses the current satellites in orbit, but is also a predictive model to anticipate accidents and malfunctions before they happen.</p>
</div>

<div class="fancy-divider">
<div class="line"></div>
<span class="diamond">◆</span>
<div class="line"></div>
</div>

<div class="about-section">
<p class="about-section-label">03 — Our Team</p>
<h2>Hackathon Goats</h2>
<div class="team-grid">
<div class="team-card">
<p class="name">Kenneth</p>
<p class="role">why am i here?</p>
<div class="card-line"></div>
</div>
<div class="team-card">
<p class="name">Srineer</p>
<p class="role">great guy they say</p>
<div class="card-line"></div>
</div>
<div class="team-card">
<p class="name">Vimal</p>
<p class="role">havent decided what titles yet</p>
<div class="card-line"></div>
</div>
<div class="team-card">
<p class="name">Vinn</p>
<p class="role">these are pretty much just placeholders</p>
<div class="card-line"></div>
</div>
</div>
</div>

<div class="footer-line">
<p>made for coldbrew 2026</p>
</div>

</div>""", unsafe_allow_html=True)