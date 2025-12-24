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
        # 데이터 읽기 시도
        if uploaded_file.name.endswith('.csv'):
            # 한글 깨짐 방지를 위해 cp949 인코딩 사용
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='cp949')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='utf-8')
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # 3. 실제 데이터 시작 위치 찾기 (과목명이 '공통' 등으로 시작하거나 A가 있는 행 찾기)
        # 데이터가 있는 행을 찾기 위해 'A', 'B', 'C' 성취도가 제목으로 쓰인 행의 인덱스를 찾습니다.
        data_start_idx = 0
        for i, row in df_raw.iterrows():
            if 'A' in row.values and 'B' in row.values:
                data_start_idx = i + 1
                break
        
        # 데이터 슬라이싱 및 컬럼명 설정
        df = df_raw.iloc[data_start_idx:].copy()
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]] # 과목, A, B, C, D, E, 평균, 표준편차
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        
        # 과목명이 비어있거나 소계 등의 행 제외
        df = df.dropna(subset=['과목'])
        df = df[df['과목'].str.contains(r'[가-힣]+')] # 한글이 포함된 과목명만 유지
        
        # 숫자 변환
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 데이터가 비어있는지 확인
        if df.empty:
            st.error("파일에서 과목 데이터를 찾을 수 없습니다. 나이스 양식이 맞는지 확인해 주세요.")
            st.stop()

        subjects = df['과목'].tolist()
        n_subs = len(subjects)

        # 4. Subplots 생성
        fig = make_subplots(
            rows=n_subs, cols=1,
            subplot_titles=[f"<b>{row['과목']}</b> (평균: {row['평균']}, 표준편차: {row['표준편차']})" for _, row in df.iterrows()],
            vertical_spacing=max(0.02, 0.5 / n_subs) # 과목 수에 따른 간격 조정
        )

        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494'] # A~E 색상
        categories = ['A', 'B', 'C', 'D', 'E']

        # 5. 과목별로 그래프 추가
        for idx, (_, row) in enumerate(df.iterrows()):
            total = sum([row[c] for c in categories])
            if total == 0: continue
            
            for i, cat in enumerate(categories):
                pct = (row[cat] / total) * 100
                fig.add_trace(
                    go.Bar(
                        x=[pct], y=[row['과목']],
                        name=cat, orientation='h',
                        marker=dict(color=colors[i]),
                        text=f"{pct:.1f}%" if pct > 3 else "", # 비율이 너무 낮으면 텍스트 생략
                        textposition='inside',
                        showlegend=(idx == 0)
                    ),
                    row=idx + 1, col=1
                )
            
            # A 비율 32.8% 보조선
            fig.add_vline(
                x=32.8, line_dash="dash", line_color="#FF4B4B", line_width=2,
                annotation_text="A 상한선 (32.8%)", annotation_position="top right",
                row=idx + 1, col=1
            )

        # 6. 레이아웃 업데이트
        fig.update_layout(
            barmode='stack',
            height=250 * n_subs,
            margin=dict(t=100, b=50, l=150, r=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(range=[0, 100], title_text="비율 (%)")
        fig.update_yaxes(showticklabels=False)

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("추출된 데이터 요약표 보기"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ 앱 실행 중 오류 발생: {e}")
        st.info("나이스에서 내려받은 파일의 형식이 평소와 다른지 확인이 필요합니다.")
