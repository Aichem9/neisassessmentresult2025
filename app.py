import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정
st.set_page_config(
    page_title="고등학교 성취평가 과목별 성취도 분포 결과 시각화 인창고 aichem9제작",
    layout="wide"
)

# 제목 및 안내 메시지
st.title("📊 고등학교 성취평가 과목별 성취도 분포 결과 시각화")
st.markdown("### 인창고 aichem9 제작")
st.info("💡 나이스에서 **xls data** 형식으로 다운받으세요.")

# 2. 파일 업로드
uploaded_file = st.file_uploader("성적 분포 파일 업로드 (CSV 또는 XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 데이터 읽기
        if uploaded_file.name.endswith('.csv'):
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='cp949')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='utf-8')
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # 3. 데이터 시작 위치 자동 찾기
        data_start_idx = 0
        for i, row in df_raw.iterrows():
            if 'A' in row.values and 'B' in row.values:
                data_start_idx = i + 1
                break
        
        # 데이터 정제
        df = df_raw.iloc[data_start_idx:].copy()
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]] # 과목, A, B, C, D, E, 평균, 표준편차
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        df = df.dropna(subset=['과목'])
        df = df[df['과목'].str.contains(r'[가-힣]+')]
        
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        subjects = df['과목'].tolist()
        n_subs = len(subjects)

        # 4. 히스토그램 스타일 Subplots 생성 (세로형 막대)
        # 과목당 행 하나씩 배정
        fig = make_subplots(
            rows=n_subs, cols=1,
            subplot_titles=[f"<b>{row['과목']}</b> (평균: {row['평균']:.1f}, 표준편차: {row['표준편차']:.1f})" for _, row in df.iterrows()],
            vertical_spacing=0.08
        )

        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494'] # A~E
        categories = ['A', 'B', 'C', 'D', 'E']

        # 5. 과목별로 히스토그램 추가
        for idx, (_, row) in enumerate(df.iterrows()):
            total = sum([row[c] for c in categories])
            if total == 0: continue
            
            # 비율 계산
            percentages = [(row[c] / total) * 100 for c in categories]
            
            # 세로 막대 추가
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=percentages,
                    marker=dict(color=colors),
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition='auto',
                    name=row['과목'],
                    showlegend=False
                ),
                row=idx + 1, col=1
            )
            
            # A 비율 32.8% 가로 보조선 추가 (성취도 A 위치 근처에 강조)
            fig.add_shape(
                type="line",
                x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=2, dash="dash"),
                row=idx + 1, col=1
            )
            
            # 보조선 라벨 추가
            fig.add_annotation(
                x=0, y=32.8,
                text="A 상한선 (32.8%)",
                showarrow=False,
                yshift=10,
                font=dict(color="red", size=12),
                row=idx + 1, col=1
            )

        # 6. 레이아웃 업데이트
        fig.update_layout(
            height=400 * n_subs, # 세로형이므로 높이를 넉넉히 설정
            margin=dict(t=100, b=50, l=50, r=50),
            template="plotly_white"
        )
        
        fig.update_yaxes(title_text="비율 (%)", range=[0, max(df[['A','B','C','D','E']].max(axis=1))+20]) # Y축 여유공간

        # 7. 앱 화면 출력
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("추출된 데이터 요약표 보기"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다: {e}")
else:
    st.warning("나이스에서 받은 파일을 업로드해 주세요.")
