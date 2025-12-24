import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# 1. 페이지 설정
st.set_page_config(
    page_title="성취도 분포 시각화 마스터 - 인창고 aichem9",
    layout="wide"
)

# 2. 상단 입력 섹션
st.title("📊 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")

col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("📅 학년도", [2024, 2025, 2026, 2027], index=1)
with col2:
    selected_semester = st.selectbox("🏫 학기", ["1학기", "2학기"], index=1)

st.info("💡 아래 마스터 차트 우측 상단의 **카메라 아이콘**을 클릭하면 모든 과목이 포함된 한 장의 이미지로 저장됩니다.")
st.divider()

# 3. 파일 업로드
uploaded_file = st.file_uploader("나이스 성적 분포 파일(XLSX, CSV)을 업로드하세요.", type=["xlsx", "csv"])

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
            st.error("⚠️ 데이터 헤더를 찾을 수 없습니다.")
            st.stop()

        # 데이터 추출 (빈칸 발생 시 즉시 중단)
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

        # 서브플롯 제목 생성
        subplot_titles = []
        for _, row in df.iterrows():
            subplot_titles.append(f"<b>{row['과목']}</b> (평균:{row['평균']})")

        # 마스터 피규어 생성
        fig = make_subplots(
            rows=num_rows, cols=num_cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.05,  # 상하 간격
            horizontal_spacing=0.05 # 좌우 간격
        )

        categories = ['A', 'B', 'C', 'D', 'E']
        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494']

        # 각 과목 데이터를 서브플롯에 추가
        for idx, (_, row) in enumerate(df.iterrows()):
            curr_row = (idx // num_cols) + 1
            curr_col = (idx % num_cols) + 1
            
            total = sum([row[c] for c in categories])
            percents = [(row[cat] / total * 100) if total > 0 else 0 for cat in categories]

            # 막대 그래프 추가
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=percents,
                    text=[f"{p:.1f}%" for p in percents],
                    textposition='auto',
                    marker_color=colors,
                    showlegend=False
                ),
                row=curr_row, col=curr_col
            )

            # 32.8% 보조선 추가
            fig.add_shape(
                type="line", x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=1.5, dash="dash"),
                row=curr_row, col=curr_col
            )

        # 5. 마스터 차트 전체 레이아웃 설정
        fig.update_layout(
            title=dict(
                text=f"✨ {selected_year}학년도 {selected_semester} 성취도 분포 마스터 리포트",
                x=0.5, font=dict(size=24)
            ),
            height=350 * num_rows, # 과목 수에 따라 높이 자동 조절
            width=1200,            # 전체 너비 고정
            template="plotly_white",
            margin=dict(t=100, b=50, l=50, r=50)
        )
        fig.update_yaxes(range=[0, 100], title="비율(%)")

        # 6. 화면 출력 및 다운로드 설정
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            config={
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f"{selected_year}_{selected_semester}_성취도분포_전체",
                    'scale': 2 # 고해상도 저장
                }
            }
        )

        with st.expander("📝 원본 데이터 확인"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 분석 오류: {e}")
else:
    st.warning("나이스 파일을 업로드하면 분석 마스터 리포트가 생성됩니다.")
