import os
import random
from pathlib import Path

import streamlit as st
from PIL import Image

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
    # 기존 코드의 특수 처리(유지)
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
# 2) UI 헬퍼 (첨부 이미지 스타일에 맞춘 HTML/CSS)
# ------------------------------------------------------------
def build_css():
    return """
    <style>
      /* 페이지 배경 (첨부 이미지 느낌의 다크 블루 그라데이션) */
      .stApp {
        background: radial-gradient(1200px 800px at 25% 20%, rgba(55, 70, 180, 0.35), rgba(0,0,0,0) 55%),
                    radial-gradient(900px 650px at 85% 70%, rgba(30, 150, 255, 0.18), rgba(0,0,0,0) 60%),
                    linear-gradient(135deg, #07112a 0%, #040a1d 55%, #030817 100%);
      }

      /* 상단 타이틀 영역 */
      .title-wrap {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 22px;
      }
      .title-line {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #e9eefc;
        display: inline-flex;
        gap: 14px;
        align-items: baseline;
      }
      .slash-left {
        color: #ff3aa8;
        font-weight: 900;
      }
      .slash-right {
        color: #2ecbff;
        font-weight: 900;
      }
      .subtitle {
        margin-top: 10px;
        font-size: 18px;
        color: rgba(233,238,252,0.82);
      }

      /* 카드(박스) */
      .card {
        background: rgba(0, 0, 0, 0.30);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px;
        padding: 22px 22px 18px 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin: 14px auto;
        max-width: 880px;
      }
      .card-title {
        text-align: center;
        font-size: 26px;
        font-weight: 800;
        color: #e9eefc;
        margin-bottom: 18px;
      }
      .row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        flex-wrap: wrap;
      }
      .stat-label {
        font-size: 20px;
        font-weight: 700;
        color: rgba(233,238,252,0.92);
        min-width: 220px;
      }
      .stat-value {
        font-size: 26px;
        font-weight: 900;
        color: #e9eefc;
        min-width: 120px;
        text-align: right;
      }
      .stat-value span {
        font-size: 18px;
        opacity: 0.9;
        font-weight: 800;
      }

      /* 바(15칸) */
      .bar {
        flex: 1;
        display: flex;
        gap: 6px;
        min-width: 320px;
        justify-content: flex-start;
      }
      .seg {
        height: 16px;
        width: 22px;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.20);
      }
      .blue { background: #1d5cff; }
      .purple { background: #b434ff; }
      .gold { background: #ffd34a; }
      .empty { background: rgba(255,255,255,0.10); }

      /* 구분선 */
      .divider {
        height: 1px;
        max-width: 880px;
        margin: 22px auto;
        background: rgba(255,255,255,0.16);
      }

      /* 버튼(첨부 이미지처럼 보라색) */
      div.stButton > button {
        width: 100%;
        max-width: 880px;
        margin: 0 auto;
        display: block;
        background: linear-gradient(180deg, #7d3cff 0%, #6a2cff 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 12px;
        padding: 14px 18px;
        font-size: 20px;
        font-weight: 900;
        box-shadow: 0 12px 28px rgba(0,0,0,0.25);
      }
      div.stButton > button:hover {
        filter: brightness(1.05);
      }

      /* 이미지 중앙 정렬 */
      .img-wrap {
        display: flex;
        justify-content: center;
        margin: 8px 0 8px 0;
      }
    </style>
    """

def render_bar_html(additional: int, total_slots: int = 15) -> str:
    # 파랑 4, 보라 4, 금색 additional, 나머지 empty
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

def render_card(title: str, stat_name: str, stat_value: int, additional: int) -> str:
    denom = 8 + additional  # 최대치(파랑4+보라4+금색additional)
    bar_html = render_bar_html(additional=additional, total_slots=15)
    return f"""
      <div class="card">
        <div class="card-title">{title}</div>
        <div class="row">
          <div class="stat-label">{stat_name}</div>
          <div class="stat-value">{stat_value}<span>/{denom}</span></div>
          {bar_html}
        </div>
      </div>
    """

# ------------------------------------------------------------
# 3) Streamlit App
# ------------------------------------------------------------
st.set_page_config(page_title="각성 잠재 시뮬레이터", layout="centered")

st.markdown(build_css(), unsafe_allow_html=True)

# 세션 상태: 기존/변경을 함께 보여주기 위해 prev/current 분리
if "prev_additional" not in st.session_state:
    st.session_state.prev_additional = None

if "current_additional" not in st.session_state:
    st.session_state.current_additional = choose_slots(initial_probs)

# 로컬 이미지(ponce.PNG) 로드
player_img = None
try:
    # potential_app.py와 같은 폴더에 ponce.PNG가 있다고 가정
    base_dir = Path(__file__).resolve().parent
    img_path = base_dir / "ponce.PNG"
    if img_path.exists():
        player_img = Image.open(img_path)
except Exception:
    player_img = None

# 상단 타이틀 (첨부 이미지 느낌)
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

# 선수 이미지 표시(중앙)
if player_img is not None:
    st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
    st.image(player_img, width=210)
    st.markdown('</div>', unsafe_allow_html=True)

STAT_NAME = "장타 억제력"
STAT_VALUE = 10

# prev가 없으면(첫 화면) prev=current로 보여주고,
# 재설정 이후에는 prev는 고정, current가 새 값
prev_add = st.session_state.prev_additional
cur_add = st.session_state.current_additional

if prev_add is None:
    prev_add = cur_add

# 카드 2개: 기존/변경 (상하 배치)
st.markdown(render_card("기존 잠재력", STAT_NAME, STAT_VALUE, prev_add), unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(render_card("변경 잠재력", STAT_NAME, STAT_VALUE, cur_add), unsafe_allow_html=True)

# SR+ 축하 멘트 (15칸 완성 시)
if cur_add == 7:
    st.markdown(
        """
        <div style="text-align:center; margin-top:12px;
                    font-size:20px; font-weight:900;
                    color:#FFD34A; text-shadow:0 0 12px rgba(255,211,74,0.6);">
            🎉 SR+ ! 축하드립니다.
        </div>
        """,
        unsafe_allow_html=True
    )


# 버튼: 재설정(=변경 잠재력 다시 뽑기)
if st.button("변경"):
    # 첨부 이미지가 '확인' 버튼이라 동일하게 맞춤
    # 실제 기능은 재설정으로 구현(원하시면 버튼 2개로도 분리 가능)
    new_probs = adjust_probs(st.session_state.current_additional)
    st.session_state.prev_additional = st.session_state.current_additional
    st.session_state.current_additional = choose_slots(new_probs)

    # ✅ Streamlit 최신 방식 rerun
    st.rerun()
