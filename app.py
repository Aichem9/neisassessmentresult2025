
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

    start_row = 5
    current_subject = None
    subject_rows = {}

    for i in range(start_row, len(df)):
        val = df.iloc[i, 0]
        if pd.notna(val):
            current_subject = str(val)
            subject_rows[current_subject] = []
        elif current_subject is not None:
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
        block = block[block.sum(axis=1) > 0]

        counts = block.sum().values
        total = np.sum(counts)

        ax.bar(grades, counts, color=colors)
        mean = np.average(np.arange(1, 6), weights=counts) if total > 0 else 0
        std = np.sqrt(np.average((np.arange(1, 6)-mean)**2, weights=counts)) if total > 0 else 0

        ax.set_title(f"{subject}\n평균: {mean*20:.1f}, 표준편차: {std*20:.1f}", fontsize=9)
        ax.set_ylim(0, max(counts)*1.2 if total > 0 else 1)
        ax.tick_params(labelsize=8)

    for ax in axes[n:]:
        ax.axis("off")

    plt.tight_layout()
    st.pyplot(fig)
