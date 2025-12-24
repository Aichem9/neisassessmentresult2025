
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math

st.set_page_config(page_title="과목별 성취도 분포", layout="wide")
st.title("과목별 성취도 분포 (히스토그램)")

uploaded_file = st.file_uploader("과목별 성취도 엑셀 파일 업로드", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)

    subject_rows = {}
    current_subject = None

    # 핵심: 과목명 / 인원수 행 정확히 구분
    for i in range(5, len(df)):
        a_val = df.iloc[i, 0]
        bf_vals = df.iloc[i, 1:6]

        # 과목명 행: A열 값 있고, B~F 모두 비어 있음
        if pd.notna(a_val) and bf_vals.isna().all():
            current_subject = str(a_val)
            subject_rows[current_subject] = []

        # 인원수 행: B~F 중 숫자 하나라도 있음
        elif current_subject is not None:
            nums = pd.to_numeric(bf_vals, errors="coerce")
            if nums.notna().any():
                subject_rows[current_subject].append(i)

    grades = ["A", "B", "C", "D", "E"]
    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff66cc"]

    subjects = list(subject_rows.keys())
    n = len(subjects)
    cols = 4
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
    axes = axes.flatten()

    for ax, subject in zip(axes, subjects):
        rows_idx = subject_rows[subject]
        block = df.iloc[rows_idx, 1:6].apply(pd.to_numeric, errors="coerce")

        counts = block.sum().values
        total = np.sum(counts)

        ax.bar(grades, counts, color=colors)

        if total > 0:
            scores = np.array([100, 80, 60, 40, 20])
            mean = np.average(scores, weights=counts)
            std = np.sqrt(np.average((scores - mean) ** 2, weights=counts))
            title = f"{subject}\n평균: {mean:.1f}, 표준편차: {std:.1f}"
        else:
            title = f"{subject}\n데이터 없음"

        ax.set_title(title, fontsize=9)
        ax.set_ylim(0, max(counts)*1.2 if total > 0 else 1)
        ax.tick_params(labelsize=8)

    for ax in axes[n:]:
        ax.axis("off")

    plt.tight_layout()
    st.pyplot(fig)
