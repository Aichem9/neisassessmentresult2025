import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="과목별 성적 상세 분석", layout="wide")

st.title("📊 과목별 성취도 상세 분석 도구")
st.info("각 과목별 성취도 분포와 평균, 표준편차를 확인하고 A비율 상한선(32.8%)을 점검합니다.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("파일을 선택하세요 (CSV, XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 데이터 읽기
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=4)
        else:
            df = pd.read_excel(uploaded_file, skiprows=4)
        
        # 필요한 컬럼 추출 및 정리 (과목, A, B, C, D, E, 평균, 표준편차)
        # 인덱스: 0(과목), 1~5(A~E), 6(평균), 7(표준편차)
        df_cleaned = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]]
        df_cleaned.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        df_cleaned = df_cleaned.dropna(subset=['과목'])
        
        # 숫자 데이터 변환
        cols_to_fix = ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        for col in cols_to_fix:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce').fillna(0)

        # 과목 리스트
        subjects = df_cleaned['과목'].tolist()
        num_subjects = len(subjects)

        # 2. Subplots 생성 (과목 수만큼 행 생성)
        fig = make_subplots(
            rows=num_subjects, cols=1,
            subplot_titles=[f"<b>{sub}</b> (평균: {avg}, 표준편차: {std})" 
                            for sub, avg, std in zip(subjects, df_cleaned['평균'], df_cleaned['표준편차'])],
            vertical_spacing=0.05
        )

        # 성취도별 색상 설정
        colors = {'A': '#4C78A8', 'B': '#72B7B2', 'C': '#F58518', 'D': '#E45756', 'E': '#BAB0AC'}

        # 3. 각 과목별로 막대 그래프 추가
        for i, row in df_cleaned.iterrows():
            total = row['A'] + row['B'] + row['C'] + row['D'] + row['E']
            if total == 0: continue
            
            # 비율 계산
            probs = {cat: (row[cat] / total) * 100 for cat in ['A', 'B', 'C', 'D', 'E']}
            
            # 성취도별로 누적 막대 추가
            cumulative_x = 0
            for cat in ['A', 'B', 'C', 'D', 'E']:
                val = probs[cat]
                fig.add_trace(
                    go.Bar(
                        name=cat,
                        x=[val],
                        y=[row['과목']],
                        orientation='h',
                        marker=dict(color=colors[cat]),
                        text=f"{val:.1;f}%" if val > 0 else "",
                        textposition='inside',
                        showlegend=(i == 0), # 범례는 첫 번째 과목에서만 표시
                    ),
                    row=i+1, col=1
                )
            
            # A 비율 32.8% 보조선 추가 (각 서브플롯 기준)
            fig.add_vline(
                x=32.8, 
                line_dash="dash", 
                line_color="red", 
                annotation_text="32.8% 제한", 
                annotation_position="top",
                row=i+1, col=1
            )

        # 그래프 레이아웃 업데이트
        fig.update_layout(
            barmode='stack',
            height=300 * num_subjects, # 과목 수에 따라 높이 조절
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=100, b=20)
        )
        
        # X축 범위 100%로 고정
        fig.update_xaxes(range=[0, 100], title_text="비율 (%)")

        # 4. 결과 출력
        st.plotly_chart(fig, use_container_width=True)

        # 통계 요약표
        st.subheader("📊 과목별 통계 요약")
        st.dataframe(df_cleaned.set_index('과목'))

    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다. 파일 형식을 확인해주세요. \n 에러 내용: {e}")
else:
    st.info("CSV 또는 XLSX 파일을 업로드해 주세요.")
