import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정 (가장 상단에 위치)
st.set_page_config(
    page_title="고등학교 성취평가 과목별 성취도 분포 결과 시각화 인창고 aichem9제작",
    layout="wide"
)

# 제목 및 안내 메시지
st.title("📊 고등학교 성취평가 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")
st.info("💡 나이스에서 **xls data** 형식으로 다운받으세요.")

# 2. 파일 업로드
uploaded_file = st.file_uploader("파일 업로드 (XLSX, CSV)", type=["xlsx", "csv"])

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

        # 3. 데이터 시작 위치 찾기 (A, B 헤더가 있는 행 찾기)
        data_start_idx = -1
        for i, row in df_raw.iterrows():
            row_vals = [str(v).strip() for v in row.values]
            if 'A' in row_vals and 'B' in row_vals:
                data_start_idx = i + 1
                break
        
        if data_start_idx == -1:
            st.error("⚠️ 데이터 시작 지점을 찾을 수 없습니다. 파일 형식을 확인하세요.")
            st.stop()

        # 4. 빈칸이 나오면 중단하는 데이터 추출 로직
        extracted_rows = []
        for i in range(data_start_idx, len(df_raw)):
            row = df_raw.iloc[i]
            subject_name = str(row[0]).strip()
            
            # 과목명이 비어있거나 'nan'이면 읽기 중단 (유저 요청 반영)
            if not subject_name or subject_name == 'nan' or subject_name == 'None':
                break
            
            # 합계나 소계 행은 건너뜀
            if any(keyword in subject_name for keyword in ['합계', '소계', '평균']):
                continue
                
            extracted_rows.append(row.iloc[:8]) # 과목~표준편차까지만 추출

        df = pd.DataFrame(extracted_rows)
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']

        # 숫자 변환
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. 한 줄에 4개씩 그래프 배치
        st.subheader("✅ 과목별 성취도 분포 (4열 배치)")
        
        categories = ['A', 'B', 'C', 'D', 'E']
        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494']

        # 데이터를 4개씩 나누어 그리드 생성
        for i in range(0, len(df), 4):
            cols = st.columns(4) # 4개의 컬럼 생성
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

                        # 32.8% 보조선
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
                            height=350,
                            margin=dict(l=10, r=10, t=80, b=20),
                            template="plotly_white",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

        # 원본 데이터 확인용
        with st.expander("데이터 요약 보기"):
            st.write(f"총 {len(df)}개의 과목이 분석되었습니다.")
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 에러 발생: {e}")
else:
    st.warning("나이스에서 받은 파일을 업로드해 주세요.")
