import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정 및 제목
st.set_page_config(
    page_title="고등학교 성취평가 과목별 성취도 분포 결과 시각화 인창고 aichem9제작",
    layout="wide"
)

st.title("📊 고등학교 성취평가 과목별 성취도 분포 결과 시각화")
st.caption("인창고 aichem9 제작")

# 2. 안내 메시지 추가
st.info("💡 나이스에서 xls data 형식으로 다운받으세요.")

# 3. 파일 업로드
uploaded_file = st.file_uploader("성적 분포 파일 업로드 (CSV 또는 XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 데이터 읽기 (나이스 표준 형식에 맞춰 5행 스킵)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=5, header=None)
        else:
            df = pd.read_excel(uploaded_file, skiprows=5, header=None)
        
        # 필요한 열 선택 (0:과목, 1~5:A~E, 6:평균, 7:표준편차)
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]]
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        
        # 과목명이 비어있는 행 제거 및 데이터 정제
        df = df.dropna(subset=['과목'])
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        subjects = df['과목'].tolist()
        n_subs = len(subjects)

        # 4. 과목별 Subplots 생성
        fig = make_subplots(
            rows=n_subs, cols=1,
            subplot_titles=[f"<b>{row['과목']}</b> (평균: {row['평균']:.1f}, 표준편차: {row['표준편차']:.1f})" for _, row in df.iterrows()],
            vertical_spacing=0.04
        )

        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#A9A9A9'] # A, B, C, D, E 색상
        categories = ['A', 'B', 'C', 'D', 'E']

        # 5. 각 과목별
