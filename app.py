import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="과목별 성취도 분포 시각화", layout="wide")

st.title("📊 과목별 성적 분포 성취도 시각화")
st.write("나이스(NEIS)에서 다운로드한 성적 분포 엑셀(CSV 변환본)을 업로드하세요.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # 데이터 읽기 (파일 구조상 5번째 줄부터 데이터가 시작됨)
        # skiprows를 통해 불필요한 헤더 정리
        df = pd.read_csv(uploaded_file, skiprows=4)
        
        # 필요한 컬럼만 추출 (과목, A, B, C, D, E)
        # CSV 구조에 따라 컬럼명이 달라질 수 있으므로 인덱스로 접근하거나 정제합니다.
        df_cleaned = df.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_cleaned.columns = ['과목', 'A', 'B', 'C', 'D', 'E']
        
        # 결측치 제거 및 과목명이 없는 행 제거
        df_cleaned = df_cleaned.dropna(subset=['과목'])
        
        # 숫자 데이터로 변환 (문자열 등이 섞여있을 수 있음)
        for col in ['A', 'B', 'C', 'D', 'E']:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce').fillna(0)

        # 2. 데이터 재구조화 (Plotly 시각화를 위해 Wide to Long format 변환)
        df_melted = df_cleaned.melt(id_vars=['과목'], value_vars=['A', 'B', 'C', 'D', 'E'],
                                   var_name='성취도', value_name='인원수')

        # 3. 백분율 계산
        df_total = df_cleaned[['과목', 'A', 'B', 'C', 'D', 'E']].set_index('과목')
        df_percent = df_total.div(df_total.sum(axis=1), axis=0) * 100
        df_percent = df_percent.reset_index().melt(id_vars=['과목'], var_name='성취도', value_name='비율')

        # 4. 그래프 생성 (Plotly)
        fig = px.bar(
            df_percent,
            y="과목",
            x="비율",
            color="성취도",
            orientation='h',
            text=df_percent['비율'].apply(lambda x: f'{x:.1f}%'),
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
            height=600
        )

        # 5. 화면 출력
        st.subheader("✅ 성취도별 인원수 비율 그래프")
        st.plotly_chart(fig, use_container_width=True)

        # 데이터 표 보기
        with st.expander("데이터 상세 보기"):
            st.dataframe(df_cleaned)

    except Exception as e:
        st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("파일을 업로드하면 그래프가 나타납니다.")
