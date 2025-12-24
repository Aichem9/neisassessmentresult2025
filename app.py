import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# 1. 페이지 설정
st.set_page_config(
    page_title="성취도 분포 시각화 - 인창고 aichem9",
    layout="wide"
)

# 2. 상단 제목 및 안내
st.title("📊 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")

col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("📅 학년도 선택", [2024, 2025, 2026, 2027], index=1)
with col2:
    selected_semester = st.selectbox("🏫 학기 선택", ["1학기", "2학기"], index=1)

st.warning("📂 **나이스 > 성적조회/통계 > 학기말 성적통계 > 과목별성적분포표 > 조회 > XLS data** 형식으로 저장한 파일을 아래에 올려주세요.")
st.divider()

# 3. 파일 업로드
uploaded_file = st.file_uploader("파일을 선택하세요 (xlsx, csv)", type=["xlsx", "csv"])

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

        # 데이터 시작 위치 찾기
        data_start_idx = -1
        for i, row in df_raw.iterrows():
            row_vals = [str(v).strip() for v in row.values]
            if 'A' in row_vals and 'B' in row_vals:
                data_start_idx = i + 1
                break
        
        if data_start_idx == -1:
            st.error("⚠️ 데이터 헤더를 찾을 수 없습니다. 나이스 원본 파일이 맞는지 확인해주세요.")
            st.stop()

        # 데이터 추출 (빈 행 발생 시 중단)
        extracted_rows = []
        for i in range(data_start_idx, len(df_raw)):
            row = df_raw.iloc[i]
            subject_name = str(row[0]).strip()
            if not subject_name or subject_name in ['nan', 'None', ""]:
                break
            if any(keyword in subject_name for keyword in ['합계', '소계', '평균']):
                continue
            extracted_rows.append(row.iloc[:8]) 

        df = pd.DataFrame(extracted_rows)
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 4. 마스터 차트 구성 (4열 그리드)
        num_subjects = len(df)
        num_cols = 4
        num_rows = math.ceil(num_subjects / num_cols)

        # 서브플롯 제목 설정 (과목명)
        subplot_titles = [f"<b>{row['과목']}</b>" for _, row in df.iterrows()]

        # 겹침 방지를 위해 vertical_spacing을 0.15 이상으로 대폭 상향
        fig = make_subplots(
            rows=num_rows, cols=num_cols,
            subplot_titles=subplot_titles,
            vertical_spacing= (0.2 / num_rows) if num_rows > 1 else 0.1, # 행 수에 따른 가변 간격
            horizontal_spacing=0.08 
        )

        categories = ['A', 'B', 'C', 'D', 'E']
        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494']

        for idx, (_, row) in enumerate(df.iterrows()):
            curr_row = (idx // num_cols) + 1
            curr_col = (idx % num_cols) + 1
            
            total = sum([row[c] for c in categories])
            percents = [(row[cat] / total * 100) if total > 0 else 0 for cat in categories]

            # 막대 그래프
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=percents,
                    text=[f"{p:.1f}%" for p in percents],
                    textposition='auto',
                    marker_color=colors,
                    showlegend=False,
                    textfont=dict(size=24, color='black', family="Arial Black") # 막대 숫자 폰트
                ),
                row=curr_row, col=curr_col
            )

            # 32.8% 보조선
            fig.add_shape(
                type="line", x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=3, dash="dash"),
                row=curr_row, col=curr_col
            )

        # 5. 전체 레이아웃 (겹침 방지 핵심 설정)
        fig.update_layout(
            title=dict(
                text=f"✨ {selected_year}학년도 {selected_semester} 성취도 분포 리포트",
                x=0.5, y=0.99, # 제목을 더 위로
                xanchor='center', yanchor='top',
                font=dict(size=70, color="black") # 제목 80은 너무 커서 겹칠 수 있어 70으로 최적화
            ),
            # 폰트가 커진만큼 한 행당 높이를 700px로 대폭 확대 (겹침 해결의 핵심)
            height=700 * num_rows, 
            width=2400,            # 전체 너비 확대
            template="plotly_white",
            margin=dict(t=300, b=150, l=150, r=150), # 상단 여백을 300으로 늘려 메인 제목 공간 확보
            font=dict(size=25, color="black") 
        )

        # 과목명(서브플롯 제목) 위치 및 크기 조정
        fig.update_annotations(font=dict(size=40, color="black"), yshift=40) # yshift로 차트와의 간격 확보

        # 축 숫자 크기 조정
        fig.update_xaxes(tickfont=dict(size=30))
        fig.update_yaxes(tickfont=dict(size=30), range=[0, 110]) # 상단 수치 겹침 방지 위해 range 110

        # 6. 화면 출력
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            config={
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f"{selected_year}_{selected_semester}_성취도분포",
                    'scale': 1.5 # 전체 사이즈가 이미 크므로 scale은 1.5로 충분
                }
            }
        )

    except Exception as e:
        st.error(f"❌ 분석 오류: {e}")
else:
    st.info("💡 나이스에서 받은 파일을 업로드해 주세요.")
