
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="과목별 성취도 분포", layout="wide")
st.title("과목별 성취도 분포 히스토그램")

uploaded_file = st.file_uploader("과목별 성취도 엑셀 파일 업로드", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)

    start_row = 5
    current_subject = None
    subject_rows = {}

    for i in range(start_row, len(df)):
        val = df.iloc[i, 0]
        if pd.notna(val):
            current_subject = val
            subject_rows[val] = []
        elif current_subject is not None:
            subject_rows[current_subject].append(i)

    grades = ["A", "B", "C", "D", "E"]
    colors = ["#4CAF50", "#2196F3", "#FFC107", "#FF9800", "#F44336"]

    for subject, rows in subject_rows.items():
        counts = df.iloc[rows, 1:6].sum().values
        total = counts.sum()
        ratios = counts / total if total != 0 else counts

        fig, ax = plt.subplots()
        bars = ax.bar(grades, ratios)

        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_ylim(0, 1)
        ax.set_ylabel("비율")
        ax.set_title(subject)

        st.pyplot(fig)
