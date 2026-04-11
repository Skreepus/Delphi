import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import streamlit as st
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Home page headline figures (fixed copy; not read from CSV).
_HOME_DISPLAY = {
    "active_satellites": 17_074,
    "dead_in_orbit": 1_468,
    "operators_tracked": 762,
    "high_risk_operators": 163,
}

# ── Tiny local HTTP server so the browser can fetch stars.mp4 via a normal URL
#    instead of a ~3.8 MB base64 data-URI (which newer Streamlit can't render).
_asset_http_lock = threading.Lock()
_asset_http_port: int | None = None


def _ensure_asset_server() -> str | None:
    """Start a daemon HTTP server on 127.0.0.1 serving the assets/ folder.
    Returns the base URL (e.g. http://127.0.0.1:8765) or None on failure."""
    global _asset_http_port
    assets_dir = _PROJECT_ROOT / "assets"
    if not (assets_dir / "stars.mp4").is_file():
        return None
    if _asset_http_port is not None:
        return f"http://127.0.0.1:{_asset_http_port}"

    with _asset_http_lock:
        if _asset_http_port is not None:
            return f"http://127.0.0.1:{_asset_http_port}"

        class _H(SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=str(assets_dir), **kw)
            def log_message(self, *_a):
                pass

        for port in [8765, 8766, 8767, 8770]:
            try:
                httpd = HTTPServer(("127.0.0.1", port), _H)
            except OSError:
                continue
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            _asset_http_port = port
            return f"http://127.0.0.1:{port}"
        return None


def render():
    # Behind nginx/ngrok: set DELPHI_PUBLIC_BASE=https://your-host (no trailing slash) so the
    # browser loads /media/stars.mp4 from FastAPI; localhost asset server only works on-machine.
    public = os.getenv("DELPHI_PUBLIC_BASE", "").strip().rstrip("/")
    if public and (_PROJECT_ROOT / "assets" / "stars.mp4").is_file():
        video_src = f"{public}/media/stars.mp4"
    else:
        base = _ensure_asset_server()
        video_src = f"{base}/stars.mp4" if base else ""
    active = f"{_HOME_DISPLAY['active_satellites']:,}"
    dead = f"{_HOME_DISPLAY['dead_in_orbit']:,}"
    operators = f"{_HOME_DISPLAY['operators_tracked']:,}"
    high_risk = f"{_HOME_DISPLAY['high_risk_operators']:,}"

    # Force every Streamlit wrapper layer transparent so the fixed video shows through
    st.markdown("""<style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div,
    section[data-testid="stMain"],
    section[data-testid="stMain"] > div,
    section[data-testid="stMain"] > div > div,
    section[data-testid="stMain"] .block-container,
    .block-container {
        background: transparent !important;
        background-color: transparent !important;
    }
    </style>""", unsafe_allow_html=True)

    # ── Video Background ──
    if video_src:
        st.markdown(f"""<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;overflow:hidden;pointer-events:none;">
<video autoplay muted loop playsinline style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);min-width:100%;min-height:100%;width:auto;height:auto;object-fit:cover;opacity:0.35;">
<source src="{video_src}" type="video/mp4">
</video>
</div>""", unsafe_allow_html=True)

    # ── Scrollytelling Sections 1 & 2 ──
    st.markdown(f"""
<div style="position:relative;z-index:2;">

<!-- ── Section 1: Opening ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;letter-spacing:0.2em;color:#6b6560;margin-bottom:2rem;">right now, above us</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:11.2rem;color:#e8e2d9;line-height:1;margin-bottom:1rem;">{active}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.68rem;color:#c9a96e;letter-spacing:0.15em;">satellites are orbiting Earth</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#2a2a2a;letter-spacing:0.15em;margin-top:4rem;">scroll down. this isn't the full picture.</p>
</div>

<!-- ── Section 2: The Dead ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#6b6560;line-height:1.8;max-width:800px;margin-bottom:3rem;">but not all of them are alive.<br>A lot of them are just drifting.</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:9.8rem;color:#c94a4a;line-height:1;margin-bottom:1rem;">{dead}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">are dead, still orbiting with no purpose.</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">space junk that circles our planet.</p>
</div>

</div>
""", unsafe_allow_html=True)

    # ── Section 3: The Counter (self-contained with live JS) ──
    counter_height = 700
    counter_html = f"""
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400&family=Merriweather:wght@300&display=swap" rel="stylesheet">
<style>
html, body {{
    margin: 0; padding: 0;
    background: transparent !important;
    overflow: hidden;
}}
</style>
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;height:{counter_height}px;box-sizing:border-box;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;color:#6b6560;line-height:1.8;max-width:750px;margin-bottom:2.5rem;">Every 90 minutes, they circle the planet. Uncontrolled. Untracked.</p>
<div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;letter-spacing:0.1em;margin-bottom:2rem;">since you opened this page</p>
<p id="elapsed-time" style="font-family:'DM Mono',monospace;font-weight:400;font-size:5.6rem;color:#e8e2d9;letter-spacing:0.05em;margin:0;">00:00:00</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;letter-spacing:0.1em;margin-bottom:2rem;">dead satellites have completed</p>
<p id="orbit-count" style="font-family:'DM Mono',monospace;font-weight:400;font-size:4.9rem;color:#c9a96e;margin:0;">0</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;max-width:600px;line-height:1.8;margin-top:0.5rem;">uncontrolled orbits around Earth</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">a collision is bound to happen.</p>
</div>
</div>
<script>
(function() {{
    var startTime = Date.now();
    var timeEl = document.getElementById('elapsed-time');
    var orbitEl = document.getElementById('orbit-count');
    function update() {{
        var elapsed = (Date.now() - startTime) / 1000;
        var hrs = Math.floor(elapsed / 3600);
        var mins = Math.floor((elapsed % 3600) / 60);
        var secs = Math.floor(elapsed % 60);
        timeEl.textContent =
            String(hrs).padStart(2,'0') + ':' +
            String(mins).padStart(2,'0') + ':' +
            String(secs).padStart(2,'0');
        orbitEl.textContent = Math.floor(elapsed / 3.7);
    }}
    setInterval(update, 200);
    update();
}})();
</script>
"""
    import streamlit.components.v1 as components
    components.html(counter_html, height=counter_height)

    # ── Scrollytelling Sections 4 & 5 ──
    st.markdown(f"""
<div style="position:relative;z-index:2;">

<!-- ── Section 4: What We Built ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;letter-spacing:0.2em;text-transform:uppercase;color:#c9a96e;margin-bottom:1.5rem;">introducing</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:4.9rem;color:#e8e2d9;margin-bottom:1.5rem;line-height:1.2;">The <em style="font-style:italic;color:#c9a96e;">Delphi</em><br>Project</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;color:#6b6560;line-height:1.8;max-width:800px;margin-bottom:3rem;">An orbital intelligence platform that tracks every satellite, scores every operator, and predicts failures before they happen.</p>
<div style="display:flex;gap:4rem;justify-content:center;flex-wrap:wrap;">
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{active}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">active satellites</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{dead}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">dead in orbit</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{operators}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">operators tracked</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#c9a96e;">{high_risk}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">high-risk operators</p>
</div>
</div>
</div>

<!-- ── Section 5: Product Preview Header ── -->
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem 2rem 2rem;">
<p style="font-family:'Lora',serif;font-weight:500;font-size:3.4rem;color:#e8e2d9;margin-bottom:1rem;line-height:1.2;">Product Preview</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.1rem;color:#6b6560;line-height:1.8;max-width:600px;margin-bottom:2rem;">Watch how Delphi tracks, scores, and predicts satellite failures in real time.</p>
</div>

</div>
""", unsafe_allow_html=True)

    # ── YouTube Video (Streamlit native – avoids iframe nesting issue) ──
    col_left, col_video, col_right = st.columns([2, 2, 2])
    with col_video:
        st.video("https://www.youtube.com/watch?v=Ij42ss911BQ")

    st.markdown("<div style='height:6rem;position:relative;z-index:2;'></div>", unsafe_allow_html=True)

