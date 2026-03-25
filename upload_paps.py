import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 PAPS 일괄 생성", layout="wide") # 넓게 보기

st.markdown("<h2 style='text-align: center; font-size: 1.8rem;'>📊 우리 반 PAPS 그래프 일괄 생성</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 - 파일 업로드 및 설정
st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader("학생 결과 파일(CSV)을 업로드하세요", type=["csv"])

st.sidebar.divider()
st.sidebar.header("⚙️ 설정")
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"], index=1)
gender = st.sidebar.radio("성별", ["남", "여"])

# 💡 팁: 샘플 파일 다운로드 기능
st.sidebar.divider()
st.sidebar.write("### 📝 파일 형식 예시")
sample_data = pd.DataFrame({
    "이름": ["김OO", "박OO"],
    "실천의지": [5, 4],
    "심폐지구력": [350, 420], # 6학년은 '초' 단위 입력
    "순발력": [9.5, 10.2],
    "유연성": [12.5, 8.0],
    "근력": [25.3, 19.8]
})
csv = sample_data.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📌 샘플 CSV 다운로드", data=csv, file_name="paps_sample.csv", mime="text/csv")


# 3. 데이터 기준 설정 (기존 앱과 동일)
if grade == "4학년":
    # (4학년 기준치는 생략, 6학년과 동일한 구조로 입력됨)
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "왕복오래달리기(심폐지구력)": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False, "u": "회"},
        # ... (나머지 4학년 기준 입력)
    }
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "오래달리기-걷기(심폐지구력)": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
    }

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 4. 점수 계산 함수 (기존 앱과 동일)
def calc_score(row):
    scores = []
    # 업로드된 파일의 컬럼명과 base의 키를 매칭
    data_map = {
        "실천의지": row["실천의지"],
        "심폐지구력": row["심폐지구력"],
        "순발력": row["순발력"],
        "유연성": row["유연성"],
        "근력": row["근력"]
    }
    
    # base의 순서대로 점수 계산
    for i, (k, v) in enumerate(base.items()):
        # 컬럼 순서대로 매핑 (0: 실천의지, 1: 심폐, 2: 순발, 3: 유연, 4: 근력)
        val = list(data_map.values())[i] 
        avg, mx = v['avg'], v['max']
        
        if v['rev']: # 낮을수록 좋은 종목
            score = 5 + (avg - val) / (avg - mx) * 5
        else: # 높을수록 좋은 종목
            score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

# 5. 그래프 그리기 함수 (한 명의 그래프를 생성)
def create_radar_chart(student_name, scores):
    fig = go.Figure()
    
    # 평균 기준선
    fig.add_trace(go.Scatterpolar(
        r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), 
        name='평균', hoverinfo='none'
    ))
    
    # 학생 그래프
    fig.add_trace(go.Scatterpolar(
        r=scores, theta=p_lbls, fill='toself', 
        name=student_name, line=dict(color='#3498DB', width=3)
    ))
    
    fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
        angularaxis=dict(tickfont=dict(size=12), rotation=90, direction="clockwise")
    ),
    showlegend=False, # 범례 숨김 (이름이 제목에 있으므로)
    margin=dict(l=80, r=80, t=60, b=40),
    height=400,
    title=dict(text=f"👤 {student_name} 학생", x=0.5, y=0.95, xanchor='center', font=dict(size=18)),
    dragmode=False
    )
    return fig

# 6. 메인 화면 - 데이터 처리 및 그래프 출력
if uploaded_file is not None:
    try:
        # 업로드된 CSV 파일 읽기
        df = pd.read_csv(uploaded_file)
        
        # 필수 컬럼 확인
        required_cols = ["이름", "실천의지", "심폐지구력", "순발력", "유연성", "근력"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ 파일에 필수 컬럼이 없습니다. ({', '.join(required_cols)})")
            st.stop()
            
        st.success(f"✅ {len(df)}명 학생의 데이터를 불러왔습니다!")
        st.write("---")
        
        # 그래프 출력 (3열 배치)
        cols = st.columns(3)
        
        for i, row in df.iterrows():
            with cols[i % 3]:
                scores = calc_score(row)
                fig = create_radar_chart(row["이름"], scores)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': False})
                st.write("---") # 구분선
                
    except Exception as e:
        st.error(f"⚠️ 파일을 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.warning("👈 왼쪽 사이드바에서 학생 결과 파일(CSV)을 업로드해주세요.")
    st.info("""
    **💡 사용 방법:**
    1. 사이드바에서 **'샘플 CSV 다운로드'** 버튼을 눌러 엑셀 파일을 받습니다.
    2. 엑셀에서 아이들의 이름과 기록을 입력합니다. (6학년 심폐지구력은 '초' 단위 입력)
    3. 파일을 CSV 형식으로 저장한 뒤, 사이드바의 **'파일 업로드'** 칸에 슥~ 끌어다 놓습니다.
    4. 우리 반 아이들 전체의 오각형 그래프가 한 번에 나타납니다! ✨
    """)
