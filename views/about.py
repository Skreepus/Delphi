import streamlit as st


def render():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&display=swap');
    .about-page {
        max-width: 900px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }
    .about-section {
        margin-bottom: 4rem;
    }
    .about-section-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.9rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1rem;
    }
    .about-section h2 {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 2.8rem;
        color: #e8e2d9;
        margin-bottom: 1.2rem;
        line-height: 1.2;
    }
    .about-section p {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.05rem;
        color: #6b6560;
        line-height: 2;
        max-width: 700px;
    }
    .about-divider {
        border: none;
        border-top: 1px solid #2a2a2a;
        margin: 0 0 4rem 0;
    }
    .innovation-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .innovation-list li {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.05rem;
        color: #6b6560;
        line-height: 2;
        padding-left: 1.5rem;
        position: relative;
        margin-bottom: 0.8rem;
    }
    .innovation-list li::before {
        content: "◆";
        position: absolute;
        left: 0;
        color: #c9a96e;
        font-size: 0.6rem;
        top: 0.45rem;
    }
    .team-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
        margin-top: 1.5rem;
    }
    .team-card {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 2rem 2.5rem;
        text-align: center;
        transition: border-color 0.3s;
    }
    .team-card:hover {
        border-color: #c9a96e;
    }
    .team-card .name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.6rem;
        color: #e8e2d9;
        margin-bottom: 0.4rem;
    }
    .team-card .role {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.9rem;
        color: #6b6560;
        letter-spacing: 0.05em;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown("""<div class="about-page">
<div class="about-section">
<p class="about-section-label">01 — Our Goal</p>
<h2>Pushing for Sustainable Satellite Usage</h2>
<p>As low-Earth orbit becomes increasingly congested, the need for responsible satellite operations has never been greater. We believe that sustainability in space starts with transparency — giving operators, regulators, and insurers the tools to make informed decisions and hold the industry accountable for the orbital environment we all share.</p>
</div>
<hr class="about-divider">
<div class="about-section">
<p class="about-section-label">02 — Our Innovation</p>
<h2>Data-Driven Orbital Intelligence</h2>
<p>We combine historical and real-time satellite data to build a comprehensive picture of orbital risk — one that goes far beyond what any single data source can offer.</p>
<br>
<ul class="innovation-list">
<li>Merging current and archival satellite data to deliver a comprehensive assessment of operational risk</li>
<li>A compliance-risk scoring system that benchmarks operators against industry best practices</li>
<li>A predictive model designed to anticipate accidents and malfunctions before they happen — reducing collisions, failures, and the growing problem of orbital debris</li>
</ul>
</div>
<hr class="about-divider">
<div class="about-section">
<p class="about-section-label">03 — Our Team</p>
<h2>The People Behind Delphi</h2>
<div class="team-grid">
<div class="team-card">
<p class="name">Tom</p>
<p class="role">Co-Founder</p>
</div>
<div class="team-card">
<p class="name">Jerry</p>
<p class="role">Co-Founder</p>
</div>
<div class="team-card">
<p class="name">Dill</p>
<p class="role">Co-Founder</p>
</div>
<div class="team-card">
<p class="name">Doe</p>
<p class="role">Co-Founder</p>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)