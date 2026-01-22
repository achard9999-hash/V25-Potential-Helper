import random
from pathlib import Path

import streamlit as st
from PIL import Image
import streamlit.components.v1 as components

# ------------------------------------------------------------
# 1) 확률/로직 (기존 메커니즘 유지)
# ------------------------------------------------------------
initial_probs = {
    1: 0.20,
    2: 0.27,
    3: 0.31,
    4: 0.12,
    5: 0.05,
    6: 0.03,
    7: 0.02
}

def adjust_probs(current):
    new_probs = initial_probs.copy()
    if current in new_probs:
        del new_probs[current]
    if current == 3:
        total = sum(new_probs.values())
        scale = 1 / total
        for k in new_probs:
            new_probs[k] *= scale
    return new_probs

def choose_slots(prob_dict):
    slots = list(prob_dict.keys())
    probs = list(prob_dict.values())
    return random.choices(slots, weights=probs, k=1)[0]

# ------------------------------------------------------------
# 2) CSS / HTML 렌더링
# ------------------------------------------------------------
def build_css():
    return """
    <style>
      html, body { font-size: 15px; }
      .stApp {
        background: radial-gradient(1200px 800px at 25% 20%, rgba(55, 70, 180, 0.35), rgba(0,0,0,0) 55%),
                    radial-gradient(900px 650px at 85% 70%, rgba(30, 150, 255, 0.18), rgba(0,0,0,0) 60%),
                    linear-gradient(135deg, #07112a 0%, #040a1d 55%, #030817 100%);
      }

      .title-wrap {
        text-align: center;
        margin-top: 8px;
        margin-bottom: 14px;
      }
      .title-line {
        font-size: 34px;
        font-weight: 850;
        letter-spacing: -0.5px;
        color: #e9eefc;
        display: inline-flex;
        gap: 12px;
        align-items: baseline;
      }
      .slash-left { color: #ff3aa8; font-weight: 900; }
      .slash-right { color: #2ecbff; font-weight: 900; }
      .subtitle {
        margin-top: 8px;
        font-size: 15px;
        color: rgba(233,238,252,0.82);
      }

      .card {
        background: rgba(0, 0, 0, 0.30);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        margin: 10px auto;
        max-width: 820px;
      }
      .card-title {
        text-align: center;
        font-size: 20px;
        font-weight: 850;
        color: #e9eefc;
        margin-bottom: 12px;
      }
      .row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        flex-wrap: wrap;
      }
      .stat-label {
        font-size: 16px;
        font-weight: 800;
        color: rgba(233,238,252,0.92);
        min-width: 160px;
      }
      .stat-value {
        font-size: 20px;
        font-weight: 950;
        color: #e9eefc;
        min-width: 92px;
        text-align: right;
      }
      .stat-value span {
        font-size: 14px;
        opacity: 0.9;
        font-weight: 850;
      }

      .bar-wrap{
        display:flex;
        align-items:center;
        gap:10px;
        flex: 1;
        min-width: 300px;
      }
      .bar {
        display: flex;
        gap: 5px;
        justify-content: flex-start;
      }
      .seg {
        height: 14px;
        width: 20px;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.20);
      }
      .blue { background: #1d5cff; }
      .purple { background: #b434ff; }
      .gold { background: #ffd34a; }
      .empty { background: rgba(255,255,255,0.10); }

      .srplus {
        font-size: 18px;
        font-weight: 950;
        color: #ffd34a;
        text-shadow: 0 2px 10px rgba(255, 211, 74, 0.35);
        letter-spacing: -0.3px;
        margin-left: 2px;
        white-space: nowrap;
      }

      .divider {
        height: 1px;
        max-width: 820px;
        margin: 16px auto;
        background: rgba(255,255,255,0.16);
      }

      div.stButton > button {
        width: 100%;
        max-width: 820px;
        margin: 0 auto;
        display: block;
        background: linear-gradient(180deg, #7d3cff 0%, #6a2cff 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 18px;
        font-weight: 950;
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
      }
      div.stButton > button:hover { filter: brightness(1.05); }
    </style>
    """

def render_bar_html(additional: int, total_slots: int = 15) -> str:
    segs = []
    for _ in range(4):
        segs.append('<div class="seg blue"></div>')
    for _ in range(4):
        segs.append('<div class="seg purple"></div>')
    for _ in range(additional):
        segs.append('<div class="seg gold"></div>')
    for _ in range(total_slots - (8 + additional)):
        segs.append('<div class="seg empty"></div>')
    return f'<div class="bar">{"".join(segs)}</div>'

def render_card_html(title: str, stat_name: str, stat_value: int, additional: int) -> str:
    denom = 8 + additional
    bar_html = render_bar_html(additional=additional, total_slots=15)
    sr_badge = '<div class="srplus">SR+</div>' if additional == 7 else ""
    return f"""
      <div class="card">
        <div class="card-title">{title}</div>
        <div class="row">
          <div class="stat-label">{stat_name}</div>
          <div class="stat-value">{stat_value}<span>/{denom}</span></div>
          <div class="bar-wrap">
            {bar_html}
            {sr_badge}
          </div>
        </div>
      </div>
    """

def render_block(*html_parts, height=220):
    # components.html은 독립 DOM이라 body 배경은 Streamlit 쪽을 따라가고,
    # 카드 내부만 렌더되면 되므로 wrapper만 최소로 둠.
    html = "".join(html_parts)
    components.html(html, height=height, scrolling=False)

# ------------------------------------------------------------
# 3) Streamlit App
# ------------------------------------------------------------
st.set_page_config(page_title="각성 잠재 시뮬레이터", layout="centered")
st.markdown(build_css(), unsafe_allow_html=True)

if "prev_additional" not in st.session_state:
    st.session_state.prev_additional = None
if "current_additional" not in st.session_state:
    st.session_state.current_additional = choose_slots(initial_probs)

# 로컬 이미지(ponce.PNG)
player_img = None
try:
    base_dir = Path(__file__).resolve().parent
    img_path = base_dir / "ponce.PNG"
    if img_path.exists():
        player_img = Image.open(img_path)
except Exception:
    player_img = None

# 타이틀 (이건 markdown+html로도 잘 먹음)
st.markdown(
    """
    <div class="title-wrap">
      <div class="title-line">
        <span class="slash-left">/</span>
        <span>잠재력 재설정</span>
        <span class="slash-right">/</span>
      </div>
      <div class="subtitle">잠재력이 변경되었습니다.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# 이미지 가운데 정렬 (streamlit native)
if player_img is not None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(player_img, width=210)

STAT_NAME = "장타 억제력"
STAT_VALUE = 10

prev_add = st.session_state.prev_additional
cur_add = st.session_state.current_additional
if prev_add is None:
    prev_add = cur_add

# ✅ 카드 렌더: st.markdown 대신 components.html로 강제 렌더
render_block(render_card_html("기존 잠재력", STAT_NAME, STAT_VALUE, prev_add), height=190)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
render_block(render_card_html("변경 잠재력", STAT_NAME, STAT_VALUE, cur_add), height=190)

if st.button("확인"):
    new_probs = adjust_probs(st.session_state.current_additional)
    st.session_state.prev_additional = st.session_state.current_additional
    st.session_state.current_additional = choose_slots(new_probs)
    st.rerun()
