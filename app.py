
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math
from io import BytesIO
import matplotlib.font_manager as fm
import os

# --------------------
# 한글 폰트 설정 (Streamlit Cloud 대응)
# --------------------
def set_korean_font():
    possible_fonts = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    ]
    for font_path in possible_fonts:
        if os.path.exists(font_path):
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams["font.family"] = font_name
            plt.rcParams["axes.unicode_minus"] = False
            return
    # fallback
    plt.rcParams["axes.unicode_minus"] = False

set_korean_font()

st.set_page_config(page_title="성취평가 모니터링", layout="wide")

st.title("성취평가 모니터링을 위한 NEIS 과목별 성취도 분석(교내) aichem9 제작")

uploaded_file = st.file_uploader("과목별 성취도 엑셀 파일 업로드", type=["xlsx"])

# --------------------
# NEIS 엑셀 파싱 (강화 버전)
# --------------------
def parse_neis_excel(df):
    subject_rows = {}
    current_subject = None

    for i in range(5, len(df)):
        a = df.iloc[i, 0]
        btof = df.iloc[i, 1:6]

        # 문자열 정리
        a_str = str(a).strip() if isinstance(a, str) else None

        # B~F 숫자 판별
        nums = pd.to_numeric(btof, errors="coerce")
        has_number = nums.notna().any()

        # 과목명 판단 규칙 (NEIS 실제 구조 반영)
        if a_str and (
            "과목" not in a_str
            and not a_str.endswith("등급")
            and not a_str.endswith("수준")
            and not has_number
        ):
            current_subject = a_str
            subject_rows[current_subject] = []
            continue

        # 인원수 행
        if current_subject and has_number:
            subject_rows[current_subject].append(i)

    # 실제 인원 데이터 없는 과목 제거
    cleaned = {}
    for subj, rows in subject_rows.items():
        if rows:
            cleaned[subj] = rows

    return cleaned

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    subject_rows = parse_neis_excel(df)

    if not subject_rows:
        st.error("과목을 인식하지 못했습니다. (NEIS 양식 확인 필요)")
        st.stop()

    grades = ["A", "B", "C", "D", "E"]
    scores = np.array([100, 80, 60, 40, 20])
    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff66cc"]

    subjects = list(subject_rows.keys())
    n = len(subjects)
    cols = 4
    rows = max(1, math.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.2, rows * 3.2))
    axes = axes.flatten()

    all_means = []

    for ax, subject in zip(axes, subjects):
        idx = subject_rows[subject]
        block = df.iloc[idx, 1:6].apply(pd.to_numeric, errors="coerce")
        counts = block.sum().values
        total = counts.sum()

        ax.bar(grades, counts, color=colors)

        if total > 0:
            mean = np.average(scores, weights=counts)
            std = np.sqrt(np.average((scores - mean) ** 2, weights=counts))
            all_means.append(mean)

            for i, c in enumerate(counts):
                pct = c / total * 100
                ax.text(i, c, f"{int(c)}명\n{pct:.1f}%", 
                        ha="center", va="bottom", fontsize=8)

            ax.set_title(f"{subject}\n평균 {mean:.1f}, 표준편차 {std:.1f}", fontsize=9)
        else:
            ax.set_title(f"{subject}\n데이터 없음", fontsize=9)

        ax.set_ylim(0, max(counts) * 1.35 if total > 0 else 1)
        ax.tick_params(labelsize=8)

    # 전체 과목 평균선
    if all_means:
        overall_mean = np.mean(all_means)
        overall_y = overall_mean / 20  # 점수 → 막대 스케일
        for ax in axes[:n]:
            ax.axhline(y=overall_y, linestyle="--", color="gray", linewidth=1)

    for ax in axes[n:]:
        ax.axis("off")

    plt.tight_layout()
    st.pyplot(fig)

    # --------------------
    # 저장 기능
    # --------------------
    buf_png = BytesIO()
    fig.savefig(buf_png, format="png", dpi=300, bbox_inches="tight")
    buf_png.seek(0)

    buf_pdf = BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches="tight")
    buf_pdf.seek(0)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 PNG 저장", buf_png, "NEIS_성취도_분포.png", "image/png")
    with col2:
        st.download_button("📥 PDF 저장(보고서용)", buf_pdf, "NEIS_성취도_분포.pdf", "application/pdf")
