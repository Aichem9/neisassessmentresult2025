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
st.info("💡 나이스에서 **xls data** 형식으로 다운받으세요. (CSV로 변환된 파일도 지원합니다.)")

# 2. 파일 업로드
uploaded_file = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # 파일 읽기
        if uploaded_file.name.endswith('.csv'):
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='cp949')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='utf-8')
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # 3. 데이터 정제 로직 (A, B 성취도 헤더가 있는 행 찾기)
        data_start_idx = -1
        for i, row in df_raw.iterrows():
            row_list = [str(val).strip() for val in row.values]
            if 'A' in row_list and 'B' in row_list:
                data_start_idx = i + 1
                break
        
        if data_start_idx == -1:
            st.error("⚠️ 파일 내에서 'A, B, C...' 성취도 헤더를 찾을 수 없습니다. 나이스 양식이 맞는지 확인해 주세요.")
            st.stop()

        # 데이터 추출 (과목, A, B, C, D, E, 평균, 표준편차)
        df = df_raw.iloc[data_start_idx:].copy()
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]]
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        
        # 유효한 행만 필터링 (과목명이 있고 숫자가 포함된 행)
        df = df.dropna(subset=['과목'])
        df['과목'] = df['과목'].astype(str)
        df = df[df['과목'].str.contains(r'[가-힣a-zA-Z]')] # 한글이나 영문이 포함된 행만
        df = df[~df['과목'].str.contains("소계|합계|평균")] # 합계 행 제외

        # 숫자 강제 변환
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 데이터가 없는 경우
        if len(df) == 0:
            st.warning("분석할 수 있는 과목 데이터가 없습니다.")
            st.stop()

        # 4. 히스토그램 스타일 그래프 생성
        subjects = df['과목'].tolist()
        n_subs = len(subjects)
        
        # 각 서브플롯 제목 구성 (숫자 포맷 에러 방지)
        titles = []
        for _, row in df.iterrows():
            title = f"<b>{row['과목']}</b> (평균: {row['평균']:.1f}, 표준편차: {row['표준편차']:.1f})"
            titles.append(title)

        fig = make_subplots(
            rows=n_subs, cols=1,
            subplot_titles=titles,
            vertical_spacing=max(0.05, 0.4 / n_subs)
        )

        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494'] # A~E
        cats = ['A', 'B', 'C', 'D', 'E']

        for idx, (_, row) in enumerate(df.iterrows()):
            total = sum([row[c] for c in cats])
            percentages = [(row[c] / total * 100) if total > 0 else 0 for c in cats]
            
            # 히스토그램(세로 막대) 추가
            fig.add_trace(
                go.Bar(
                    x=cats,
                    y=percentages,
                    marker=dict(color=colors),
                    text=[f"{p:.1f}%" if p > 0 else "" for p in percentages],
                    textposition='auto',
                    showlegend=False
                ),
                row=idx + 1, col=1
            )
            
            # A 비율 32.8% 보조선
            fig.add_shape(
                type="line", x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=2, dash="dash"),
                row=idx + 1, col=1
            )
            
            # 보조선 라벨
            if idx == 0: # 맨 위 그래프에만 라벨 표시
                fig.add_annotation(
                    x=0, y=32.8, text="A 상한선 (32.8%)",
                    showarrow=False, yshift=15, font=dict(color="red"),
                    row=idx + 1, col=1
                )

        # 레이아웃 조정
        fig.update_layout(
            height=350 * n_subs,
            margin=dict(t=100, b=50, l=50, r=50),
            template="plotly_white"
        )
        fig.update_yaxes(title_text="비율 (%)", range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)

        # 원본 데이터 확인
        with st.expander("데이터 테이블 보기"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 앱 실행 중 에러가 발생했습니다.")
        st.exception(e) # 구체적인 에러 내용을 출력하여 디버깅을 돕습니다.
