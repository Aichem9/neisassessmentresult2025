import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(
    page_title="고등학교 성취평가 과목별 성취도 분포 결과 시각화 인창고 aichem9제작",
    layout="wide"
)

st.title("📊 고등학교 성취평가 과목별 성취도 분포 결과 시각화")
st.markdown("#### 인창고 aichem9 제작")
st.info("💡 나이스에서 **xls data** 형식으로 다운받으세요.")

# 2. 파일 업로드
uploaded_file = st.file_uploader("나이스에서 받은 파일을 선택하세요 (XLSX, CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # 데이터 로드 (나이스 파일 특성상 앞부분 5줄은 제목/설명이므로 건너뜀)
        if uploaded_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, skiprows=5, header=None, encoding='cp949')
            except:
                df = pd.read_csv(uploaded_file, skiprows=5, header=None, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file, skiprows=5, header=None)

        # 필요한 컬럼만 추출 및 이름 지정
        # 0:과목, 1:A, 2:B, 3:C, 4:D, 5:E, 6:평균, 7:표준편차
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]]
        df.columns = ['과목', 'A', 'B', 'C', 'D', 'E', '평균', '표준편차']

        # 데이터 정제: 과목명이 없는 행이나 소계/합계 행 제거
        df = df.dropna(subset=['과목'])
        df = df[df['과목'].astype(str).str.contains(r'[가-힣]')] # 한글 포함된 행만
        df = df[~df['과목'].astype(str).str.contains('합계|소계|평균')]

        # 숫자 데이터로 변환 (문자열 등이 섞여있을 경우 대비)
        for col in ['A', 'B', 'C', 'D', 'E', '평균', '표준편차']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 3. 과목별로 그래프 그리기 (반복문 사용)
        st.subheader("✅ 과목별 성취도 히스토그램")
        
        # 성취도 카테고리와 색상
        categories = ['A', 'B', 'C', 'D', 'E']
        colors = ['#4C78A8', '#72B7B2', '#F58518', '#E45756', '#949494']

        for _, row in df.iterrows():
            subject_name = row['과목']
            total_students = row['A'] + row['B'] + row['C'] + row['D'] + row['E']
            
            if total_students == 0: continue # 학생수 0이면 건너뜀

            # 비율 계산
            percents = [(row[cat] / total_students) * 100 for cat in categories]

            # Plotly 차트 생성
            fig = go.Figure()

            # 막대 그래프 추가
            fig.add_trace(go.Bar(
                x=categories,
                y=percents,
                text=[f"{p:.1f}%" for p in percents],
                textposition='auto',
                marker_color=colors,
                name=subject_name
            ))

            # A 비율 32.8% 보조선 추가
            fig.add_shape(
                type="line",
                x0=-0.5, x1=4.5, y0=32.8, y1=32.8,
                line=dict(color="Red", width=3, dash="dash")
            )

            # 보조선 텍스트 추가
            fig.add_annotation(
                x=4, y=34,
                text="<b>A 상한선 (32.8%)</b>",
                font=dict(color="red"),
                showarrow=False
            )

            # 레이아웃 설정 (과목명, 평균, 표준편차 포함)
            fig.update_layout(
                title=f"📖 {subject_name} (평균: {row['평균']}, 표준편차: {row['표준편차']})",
                yaxis=dict(title="비율 (%)", range=[0, max(max(percents)+10, 45)]),
                xaxis=dict(title="성취도"),
                height=400,
                template="plotly_white",
                margin=dict(l=20, r=20, t=60, b=20)
            )

            # 화면에 출력
            st.plotly_chart(fig, use_container_width=True)
            st.divider() # 과목 간 구분선

        # 상세 데이터 표
        with st.expander("원본 데이터 확인"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ 에러 발생: {e}")
        st.info("파일의 형식이 나이스에서 받은 표준 xlsx가 맞는지 확인해주세요.")
else:
    st.warning("파일을 업로드하면 시각화 결과가 나타납니다.")
