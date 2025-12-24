import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(
    page_title="성취평가 과목별 성취도 분포 시각화",
    layout="wide"
)

# --- 상단 입력 섹션 ---
st.title("📊 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")

# 학년도 및 학기 선택 영역 (2컬럼 배치)
input_col1, input_col2 = st.columns(2)
with input_col1:
    year_list = [2024, 2025, 2026, 2027]
    # 기본값으로 2025학년도 선택
    selected_year = st.selectbox("📅 학년도를 선택하세요", year_list, index=1)
with input_col2:
    # 기본값으로 2학기 선택
    selected_semester = st.selectbox("🏫 학기를 선택하세요", ["1학기", "2학기"], index=1)

st.divider()

# 선택된 정보를 큰 제목으로 출력
st.header(f"✨ {selected_year}학년도 {selected_semester} 성적 분석 결과")

# 2. 파일 업로드
uploaded_file = st.file_uploader("나이스 성적 분포 파일(XLSX, CSV)을 업로드해 주세요.", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # 데이터 로드
        if uploaded_file.name.endswith('.csv'):
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='cp949')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, encoding='utf-8')
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # 3. 데이터 시작 위치 찾기
        data_start_idx = -1
        for i, row in df_raw.iterrows():
            row_vals = [str(v).strip() for v in row.values]
            if 'A' in row_vals and 'B' in row_vals:
                data_start_idx = i + 1
                break
        
        if data_start_idx == -1:
            st.error("⚠️ 데이터 헤더(A, B 등)를 찾을 수 없습니다. 파일 양식을 확인하세요.")
            st.stop()

        # 4. 데이터 추출 및 빈칸 발생 시 중단 로직
        extracted_rows = []
        for i in range(data_start_idx, len(df_raw)):
            row = df_raw.iloc[i]
            subject_name = str(row[0]).strip()
            
            # 과목명이 비어있거나 'nan'이면 즉시 읽기 중단 (사용자 요청 반영)
            if not subject_name or subject_name == 'nan' or subject_name == 'None':
                break
            
            # 불필요한 행 제외
            if any(keyword in subject_name for keyword in ['합계', '소계', '평균']):
                continue
                
            extracted_rows.append(row.iloc[:8]) 

        df = pd.DataFrame(extracted_rows)
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']

        # 숫자 데이터 변환
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. 그래프 4열 배치 출력
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
                        
                        percents = [(row[c] / total) * 100 for c in categories]

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

                        fig.update_layout(
                            title=dict(
                                text=f"<b>{row['과목']}</b><br><span style='font-size:12px;'>평균:{row['평균']} / 표편:{row['표준편차']}</span>",
                                x=0.5, xanchor='center'
                            ),
                            yaxis=dict(range=[0, max(max(percents)+20, 50)], title="비율(%)"),
                            height=330,
                            margin=dict(l=10, r=10, t=80, b=20),
                            template="plotly_white",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📝 추출된 데이터 확인"):
            st.write(f"총 {len(df)}개의 유효 과목이 분석되었습니다.")
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 분석 중 에러가 발생했습니다: {e}")
else:
    st.info("💡 파일을 업로드하면 분석이 시작됩니다.")
