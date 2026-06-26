import streamlit as st # type: ignore
from textblob import TextBlob # type: ignore
import re
from datetime import datetime

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Lens",
    page_icon="🧠",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,300&display=swap');

  :root {
    --bg:        #0e0f14;
    --surface:   #16181f;
    --border:    #2a2d38;
    --accent:    #7c6af7;
    --accent2:   #c792ea;
    --pos:       #4ade80;
    --neg:       #f87171;
    --neu:       #94a3b8;
    --text:      #e2e4ef;
    --muted:     #6b7280;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
  }

  [data-testid="stHeader"] { background: var(--bg) !important; }
  [data-testid="stSidebar"] { display: none; }

  /* headings */
  h1 { font-family: 'DM Mono', monospace !important; letter-spacing: -1px; }

  /* textarea */
  textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    border-radius: 8px !important;
    padding: 12px !important;
  }
  textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(124,106,247,0.2) !important; }

  /* buttons */
  .stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity 0.15s;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* metric cards */
  [data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
  }
  [data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
  [data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 1.6rem !important; }

  /* divider */
  hr { border-color: var(--border) !important; }

  /* expander */
  [data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
  }

  /* history cards */
  .hist-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
  }
  .hist-card .snippet { color: var(--muted); font-size: 0.82rem; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  /* sentiment badges */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
  }
  .badge-pos { background: rgba(74,222,128,0.12); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
  .badge-neg { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
  .badge-neu { background: rgba(148,163,184,0.12); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }

  /* big verdict */
  .verdict {
    font-family: 'DM Mono', monospace;
    font-size: 2.8rem;
    font-weight: 500;
    letter-spacing: -1px;
  }
  .verdict-pos { color: #4ade80; }
  .verdict-neg { color: #f87171; }
  .verdict-neu { color: #94a3b8; }

  /* gauge bar */
  .gauge-wrap { margin: 0.4rem 0 1rem; }
  .gauge-track { height: 8px; background: var(--border); border-radius: 99px; overflow: hidden; }
  .gauge-fill  { height: 100%; border-radius: 99px; transition: width 0.4s ease; }

  /* word chips */
  .chip-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
  .chip {
    padding: 3px 10px;
    border-radius: 99px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
  }
  .chip-pos { background: rgba(74,222,128,0.1); color: #4ade80; }
  .chip-neg { background: rgba(248,113,113,0.1); color: #f87171; }
  .chip-neu { background: rgba(148,163,184,0.08); color: #94a3b8; }

  /* label */
  .field-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────
def classify(polarity: float) -> tuple[str, str]:
    if polarity > 0.05:
        return "Positive", "pos"
    elif polarity < -0.05:
        return "Negative", "neg"
    return "Neutral", "neu"


def polarity_bar(value: float) -> str:
    """Render a colour-coded bar for polarity (–1 to +1)."""
    pct = int((value + 1) / 2 * 100)
    if value > 0.05:
        color = "#4ade80"
    elif value < -0.05:
        color = "#f87171"
    else:
        color = "#94a3b8"
    return f"""
    <div class="gauge-wrap">
      <div class="gauge-track">
        <div class="gauge-fill" style="width:{pct}%; background:{color};"></div>
      </div>
    </div>"""


def subjectivity_bar(value: float) -> str:
    pct = int(value * 100)
    return f"""
    <div class="gauge-wrap">
      <div class="gauge-track">
        <div class="gauge-fill" style="width:{pct}%; background:#7c6af7;"></div>
      </div>
    </div>"""


def word_chips(text: str) -> str:
    words = re.findall(r"[a-zA-Z']+", text)
    chips = ""
    for w in words:
        blob = TextBlob(w)
        p = blob.sentiment.polarity
        if p > 0.05:
            css = "chip-pos"
        elif p < -0.05:
            css = "chip-neg"
        else:
            css = "chip-neu"
        chips += f'<span class="chip {css}">{w}</span>'
    return f'<div class="chip-wrap">{chips}</div>'


def analyse(text: str) -> dict:
    blob = TextBlob(text)
    pol  = blob.sentiment.polarity
    sub  = blob.sentiment.subjectivity
    label, cls = classify(pol)
    sentences  = [(str(s), s.sentiment.polarity) for s in blob.sentences]
    return dict(polarity=pol, subjectivity=sub, label=label, cls=cls, sentences=sentences)


# ─── Session state ───────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 🧠 Sentiment Lens")
st.markdown('<p style="color:#6b7280;font-size:0.95rem;margin-top:-8px;">Powered by TextBlob · polarity & subjectivity analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# ─── Layout ──────────────────────────────────────────────────────────────────
left, right = st.columns([1.1, 1], gap="large")

with left:
    st.markdown('<div class="field-label">Enter text</div>', unsafe_allow_html=True)
    user_text = st.text_area("", height=180, placeholder="Type or paste anything — a review, tweet, sentence…", label_visibility="collapsed")

    col_btn, col_clear = st.columns([1, 1])
    with col_btn:
        analyse_btn = st.button("Analyse →", use_container_width=True)
    with col_clear:
        clear_btn = st.button("Clear history", use_container_width=True)

    if clear_btn:
        st.session_state.history = []
        st.rerun()

    # ── Example sentences ───────────────────────────────────────────────────
    st.markdown('<div class="field-label" style="margin-top:1rem;">Try an example</div>', unsafe_allow_html=True)
    examples = [
        "I absolutely love this product — it changed my life!",
        "The service was terrible and I'll never come back.",
        "The package arrived on Tuesday.",
        "Mixed feelings: great concept, poor execution.",
    ]
    for ex in examples:
        if st.button(ex[:55] + ("…" if len(ex) > 55 else ""), key=ex, use_container_width=True):
            user_text = ex
            analyse_btn = True

with right:
    if analyse_btn and user_text.strip():
        result = analyse(user_text.strip())

        # store in history
        st.session_state.history.insert(0, {
            "text": user_text.strip(),
            "result": result,
            "time": datetime.now().strftime("%H:%M:%S"),
        })

        cls   = result["cls"]
        label = result["label"]
        pol   = result["polarity"]
        sub   = result["subjectivity"]

        emoji = {"pos": "😊", "neg": "😟", "neu": "😐"}[cls]
        st.markdown(f'<div class="verdict verdict-{cls}">{emoji} {label}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-{cls}">{label.upper()}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.metric("Polarity", f"{pol:+.3f}", help="–1 very negative → +1 very positive")
        c2.metric("Subjectivity", f"{sub:.3f}", help="0 objective → 1 subjective")

        st.markdown('<div class="field-label" style="margin-top:1rem;">Polarity</div>', unsafe_allow_html=True)
        st.markdown(polarity_bar(pol), unsafe_allow_html=True)

        st.markdown('<div class="field-label">Subjectivity</div>', unsafe_allow_html=True)
        st.markdown(subjectivity_bar(sub), unsafe_allow_html=True)

        # ── Sentence breakdown ───────────────────────────────────────────────
        if len(result["sentences"]) > 1:
            with st.expander("Sentence breakdown"):
                for sent, sp in result["sentences"]:
                    sl, sc = classify(sp)
                    st.markdown(
                        f'<div style="margin-bottom:8px;">'
                        f'<span class="badge badge-{sc}">{sl}</span> '
                        f'<span style="font-size:0.85rem;color:#94a3b8;">{sp:+.3f}</span><br>'
                        f'<span style="font-size:0.9rem;">{sent}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        # ── Word-level heatmap ───────────────────────────────────────────────
        with st.expander("Word-level polarity"):
            st.markdown(word_chips(user_text.strip()), unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.75rem;color:#6b7280;margin-top:8px;">🟢 positive &nbsp; 🔴 negative &nbsp; ⬜ neutral</p>', unsafe_allow_html=True)

    elif analyse_btn:
        st.warning("Please enter some text first.")
    else:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.9rem;padding-top:2rem;text-align:center;">'
            'Your analysis results will appear here.'
            '</div>',
            unsafe_allow_html=True
        )

# ─── History ─────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown('<div class="field-label">Analysis history</div>', unsafe_allow_html=True)
    for item in st.session_state.history[:8]:
        r   = item["result"]
        cls = r["cls"]
        st.markdown(
            f'<div class="hist-card">'
            f'<span class="badge badge-{cls}">{r["label"].upper()}</span> '
            f'<span style="font-family:\'DM Mono\',monospace;font-size:0.8rem;color:#6b7280;margin-left:8px;">'
            f'pol {r["polarity"]:+.3f} · sub {r["subjectivity"]:.3f} · {item["time"]}</span>'
            f'<div class="snippet">{item["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )