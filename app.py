
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math
from io import BytesIO

st.set_page_config(page_title="성취평가 모니터링", layout="wide")

st.title("성취평가 모니터링을 위한 NEIS 과목별 성취도 분석(교내) aichem9 제작")

uploaded_file = st.file_uploader("과목별 성취도 엑셀 파일 업로드", type=["xlsx"])

def parse_excel(df):
    subject_rows = {}
    current_subject = None

    for i in range(5, len(df)):
        a_val = df.iloc[i, 0]
        bf_vals = df.iloc[i, 1:6]

        # 과목명 후보: A열 문자열 & B~F 대부분 비어 있음
        if isinstance(a_val, str) and bf_vals.isna().sum() >= 4:
            current_subject = a_val.strip()
            subject_rows[current_subject] = []

        # 인원수 행: B~F 중 숫자 존재
        nums = pd.to_numeric(bf_vals, errors="coerce")
        if current_subject and nums.notna().any():
            subject_rows[current_subject].append(i)

    # 실제 데이터가 없는 과목 제거
    subject_rows = {
        k: v for k, v in subject_rows.items()
        if len(v) > 0
    }
    return subject_rows

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    subject_rows = parse_excel(df)

    if len(subject_rows) == 0:
        st.error("과목을 인식하지 못했습니다. 엑셀 형식을 확인해주세요.")
        st.stop()

    grades = ["A", "B", "C", "D", "E"]
    scores = np.array([100, 80, 60, 40, 20])
    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff66cc"]

    subjects = list(subject_rows.keys())
    n = len(subjects)
    cols = 4
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
    axes = axes.flatten()

    all_means = []

    for ax, subject in zip(axes, subjects):
        rows_idx = subject_rows[subject]
        block = df.iloc[rows_idx, 1:6].apply(pd.to_numeric, errors="coerce")
        counts = block.sum().values
        total = counts.sum()

        ax.bar(grades, counts, color=colors)

        if total > 0:
            mean = np.average(scores, weights=counts)
            std = np.sqrt(np.average((scores - mean) ** 2, weights=counts))
            all_means.append(mean)

            for i, c in enumerate(counts):
                pct = c / total * 100 if total > 0 else 0
                ax.text(i, c, f"{int(c)}명\n{pct:.1f}%", 
                        ha="center", va="bottom", fontsize=8)

            ax.set_title(f"{subject}\n평균: {mean:.1f}, 표준편차: {std:.1f}", fontsize=9)
        else:
            ax.set_title(f"{subject}\n데이터 없음", fontsize=9)

        ax.set_ylim(0, max(counts)*1.3 if total > 0 else 1)
        ax.tick_params(labelsize=8)

    overall_mean = np.mean(all_means) if all_means else None

    for ax in axes[:n]:
        if overall_mean:
            ax.axhline(y=overall_mean/20, linestyle="--", color="gray", linewidth=1)

    for ax in axes[n:]:
        ax.axis("off")

    plt.tight_layout()
    st.pyplot(fig)

    # --------- 저장 기능 ---------
    buf_png = BytesIO()
    fig.savefig(buf_png, format="png", dpi=300, bbox_inches="tight")
    buf_png.seek(0)

    buf_pdf = BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches="tight")
    buf_pdf.seek(0)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 PNG 다운로드", buf_png, "성취도_분포.png", "image/png")
    with col2:
        st.download_button("📥 PDF 다운로드(평가보고서용)", buf_pdf, "성취도_분포.pdf", "application/pdf")
