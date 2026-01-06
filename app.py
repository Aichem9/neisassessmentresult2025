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

col1, col2, col3 = st.columns(3)
with col1:
    selected_year = st.selectbox("📅 학년도 선택", [2024, 2025, 2026, 2027], index=1)
with col2:
    selected_grade = st.selectbox("🙋 학년 선택", [1, 2, 3], index=0)
with col3:
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

        # [수정] 데이터 시작 위치 및 '평균' 컬럼(G열=index 6) 찾기
        data_start_idx = -1
        for i, row in df_raw.iterrows():
            row_vals = [str(v).strip() for v in row.values]
            if 'A' in row_vals and 'B' in row_vals:
                data_start_idx = i + 1
                break
        
        if data_start_idx == -1:
            st.error("⚠️ 데이터 헤더를 찾을 수 없습니다. 나이스 원본 파일을 확인해 주세요.")
            st.stop()

        # [수정] 데이터 추출 로직: G열(index 6)을 평균으로 확실히 지정
        extracted_rows = []
        for i in range(data_start_idx, len(df_raw)):
            row = df_raw.iloc[i]
            subject_name = str(row[0]).strip()
            
            # 빈 행이거나 합계/평균 행이면 중단/건너뛰기
            if not subject_name or subject_name in ['nan', 'None', ""]:
                break
            if any(keyword in subject_name for keyword in ['합계', '소계']):
                continue
            
            # 데이터 매핑 (나이스 XLS data 표준 인덱스 기반)
            # 0:과목, 1:A, 2:B, 3:C, 4:D, 5:E, 6:평균 (G열)
            extracted_rows.append({
                '과목': subject_name,
                'A': row[1], 'B': row[2], 'C': row[3], 'D': row[4], 'E': row[5],
                '평균': row[6] # G열 데이터
            })

        df = pd.DataFrame(extracted_rows)
        # 숫자형 변환
        for col in ['A', 'B', 'C', 'D', 'E', '평균']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 4. 마스터 차트 구성
        num_subjects = len(df)
        num_cols = 4
        num_rows = math.ceil(num_subjects / num_cols)
        v_space = min(0.06, 0.9 / num_rows) if num_rows > 1 else 0.1

        fig = make_subplots(
            rows=num_rows, cols=num_cols,
            vertical_spacing=v_space,
            horizontal_spacing=0.06
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
                    x=categories, y=percents,
                    text=[f"{p:.1f}%" for p in percents],
                    textposition='auto',
                    marker_color=colors,
                    showlegend=False,
                    textfont=dict(size=22, color='black', family="Arial Black")
                ),
                row=curr_row, col=curr_col
            )

            # [핵심 수정] 과목명 및 평균값(G열 데이터) 표시
            # 폰트 크기 27px, 평균값 강조
            fig.add_annotation(
                text=f"<b>{row['과목']}</b><br><span style='color:blue;'>평균: {row['평균']:.1f}</span>",
                xref="x domain", yref="y domain",
                x=0.5, y=0.85,
                showarrow=False,
                font=dict(size=27, color="black"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="black",
                borderwidth=1,
                row=curr_row, col=curr_col
            )

            # 32.8% 보조선
            fig.add_shape(
                type="line", x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=2, dash="dash"),
                row=curr_row, col=curr_col
            )

        # 5. 전체 레이아웃
        fig.update_layout(
            title=dict(
                text=f"✨ {selected_year}학년도 {selected_grade}학년 {selected_semester} 성취도 분포 리포트",
                x=0.5, y=0.98, xanchor='center', yanchor='top',
                font=dict(size=55, color="black")
            ),
            height=580 * num_rows, 
            width=2400, 
            template="plotly_white",
            margin=dict(t=220, b=120, l=130, r=100),
        )

        fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, tickfont=dict(size=24))
        fig.update_yaxes(
            showline=True, linewidth=2, linecolor='black', mirror=True,
            title_text="인원수 비율 (%)", title_font=dict(size=20),
            tickfont=dict(size=24), range=[0, 115]
        )

        # 6. 화면 출력
        st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False})

    except Exception as e:
        st.error(f"❌ 분석 오류: {e}")
else:
    st.info("💡 파일을 업로드하시면 G열의 평균값이 반영된 리포트가 생성됩니다.")
