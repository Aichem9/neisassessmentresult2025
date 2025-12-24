import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="고등학교 성취평가 과목별 성취도 분포 결과 시각화 인창고 aichem9제작", layout="wide")

st.title("📊 과목별 성적 분포 성취도 시각화")
st.write("나이스(NEIS)에서 다운로드한 성적 분포 파일(CSV 또는 XLSX)을 업로드하세요.")

# 1. 파일 업로드 (csv와 xlsx 모두 허용)
uploaded_file = st.file_uploader("파일을 선택하세요 (CSV, XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 파일 확장자에 따라 읽는 방식 결정
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=4)
        else:
            # 엑셀 파일 읽기 (엔진으로 openpyxl 사용)
            df = pd.read_excel(uploaded_file, skiprows=4)
        
        # 필요한 컬럼만 추출 (과목, A, B, C, D, E)
        # 인덱스 기준으로 추출하여 컬럼명 오차 방지
        df_cleaned = df.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_cleaned.columns = ['과목', 'A', 'B', 'C', 'D', 'E']
        
        # 결측치 제거 (과목명이 비어있는 행 제외)
        df_cleaned = df_cleaned.dropna(subset=['과목'])
        
        # 숫자 데이터로 변환
        for col in ['A', 'B', 'C', 'D', 'E']:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce').fillna(0)

        # 2. 데이터 재구조화 (비율 계산용)
        df_total = df_cleaned.set_index('과목')
        df_percent = df_total.div(df_total.sum(axis=1), axis=0) * 100
        
        # Plotly 시각화를 위한 Melt 작업
        df_plot = df_percent.reset_index().melt(id_vars=['과목'], var_name='성취도', value_name='비율')

        # 3. 그래프 생성 (Plotly)
        fig = px.bar(
            df_plot,
            y="과목",
            x="비율",
            color="성취도",
            orientation='h',
            text=df_plot['비율'].apply(lambda x: f'{x:.1f}%' if x > 0 else ''),
            color_discrete_map={
                'A': '#4C78A8', 'B': '#72B7B2', 'C': '#F58518', 'D': '#E45756', 'E': '#54A24B'
            },
            category_orders={"성취도": ["A", "B", "C", "D", "E"], "과목": df_cleaned['과목'].tolist()}
        )

        fig.update_layout(
            xaxis_title="비율 (%)",
            yaxis_title="과목명",
            legend_title="성취도",
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            height=600,
            xaxis=dict(range=[0, 100]) # X축을 0~100%로 고정
        )

        # 4. 화면 출력
        st.subheader("✅ 성취도별 인원수 비율 분포")
        st.plotly_chart(fig, use_container_width=True)

        # 데이터 표 보기
        with st.expander("원본 데이터 확인"):
            st.dataframe(df_cleaned)

    except Exception as e:
        st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("CSV 또는 XLSX 파일을 업로드하면 그래프가 나타납니다.")
