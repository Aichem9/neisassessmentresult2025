import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(
    page_title="성취도 분포 시각화 - 인창고 aichem9",
    layout="wide"
)

# --- 인쇄를 위한 CSS 설정 (인쇄 시 버튼 등 UI 숨기기) ---
st.markdown("""
    <style>
    @media print {
        .stButton, .stFileUploader, .stSelectbox, .stInfo, header, footer, .css-1dp56ee, .css-12oz5g7 {
            display: none !important;
        }
        .main .block-container {
            padding-top: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 입력 섹션
st.title("📊 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")

input_col1, input_col2, input_col3 = st.columns([1, 1, 1])
with input_col1:
    selected_year = st.selectbox("📅 학년도", [2024, 2025, 2026, 2027], index=1)
with input_col2:
    selected_semester = st.selectbox("🏫 학기", ["1학기", "2학기"], index=1)
with input_col3:
    st.write("") # 간격 맞춤
    if st.button("🖨️ 결과 전체 출력/PDF 저장"):
        components.html("<script>window.print();</script>", height=0)

st.divider()

# 3. 파일 업로드
uploaded_file = st.file_uploader("나이스 성적 분포 파일(XLSX, CSV)을 업로드하세요.", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
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
            
            # 빈칸이 나오면 읽기 중단
            if not subject_name or subject_name == 'nan' or subject_name == 'None' or subject_name == "":
                break
            
            if any(keyword in subject_name for keyword in ['합계', '소계', '평균']):
                continue
                
            extracted_rows.append(row.iloc[:8]) 

        df = pd.DataFrame(extracted_rows)
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']

        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 4. 그래프 출력 (4열 배치)
        st.header(f"✨ {selected_year}학년도 {selected_semester} 성적 분석 결과")
        
        categories = ['A', 'B', 'C', 'D', 'E']
        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494']

        for i in range(0, len(df), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(df):
                    row = df.iloc[i + j]
                    with cols[j]:
                        total = sum([row[c] for c in categories])
                        if total == 0: continue
                        
                        percents = [(row[cat] / total) * 100 for cat in categories]

                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=categories,
                            y=percents,
                            text=[f"{p:.1f}%" for p in percents],
                            textposition='auto',
                            marker_color=colors,
                        ))

                        # A 비율 32.8% 보조선
                        fig.add_shape(
                            type="line", x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                            line=dict(color="Red", width=2, dash="dash")
                        )

                        # 그래프 제목에 학년도/학기 포함
                        fig.update_layout(
                            title=dict(
                                text=f"<b>{row['과목']}</b><br><span style='font-size:11px;'>{selected_year}년 {selected_semester} | 평균:{row['평균']} / 표편:{row['표준편차']}</span>",
                                x=0.5, xanchor='center'
                            ),
                            yaxis=dict(range=[0, max(max(percents)+20, 50)], title="비율(%)"),
                            height=330,
                            margin=dict(l=10, r=10, t=80, b=20),
                            template="plotly_white",
                            showlegend=False,
                            # 인쇄 시 배경을 하얗게 유지
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with st.expander("📝 데이터 테이블"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 분석 오류: {e}")
else:
    st.info("💡 나이스 파일을 업로드하면 분석이 시작됩니다.")
