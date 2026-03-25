import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 PAPS 일괄 생성", layout="wide")

st.markdown("<h2 style='text-align: center; font-size: 1.8rem;'>📊 우리 반 PAPS 그래프 일괄 생성</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader("학생 결과 파일(CSV)을 업로드하세요", type=["csv"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 데이터 기준 설정 (선생님 엑셀의 '회수' 기준에 맞게 고정)
base = {
    "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
    "심폐지구력": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False, "u": "회"},
    "순발력": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True, "u": "초"},
    "유연성": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False, "u": "cm"},
    "근력": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False, "u": "kg"}
}

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 4. 점수 계산 함수
def calc_score(row):
    scores = []
    # 엑셀의 컬럼명에서 공백이 있을 수 있어 strip() 처리
    data_map = {
        "실천의지": row.get("실천의지", 5.0),
        "심폐지구력": row.get("심폐지구력", 0.0),
        "순발력": row.get("순발력", 15.0),
        "유연성": row.get("유연성", 0.0),
        "근력": row.get("근력", 0.0)
    }
    
    for k, v in base.items():
        val = data_map[k]
        avg, mx = v['avg'], v['max']
        if v['rev']: # 순발력(초) 등 낮을수록 좋은 종목
            score = 5 + (avg - val) / (avg - mx) * 5
        else: # 높을수록 좋은 종목
            score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

# 5. 그래프 그리기 함수
def create_radar_chart(student_name, scores):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), name='평균'))
    fig.add_trace(go.Scatterpolar(r=scores, theta=p_lbls, fill='toself', name=student_name, line=dict(color='#3498DB', width=3)))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
            angularaxis=dict(tickfont=dict(size=12), rotation=90, direction="clockwise")
        ),
        showlegend=False,
        margin=dict(l=80, r=80, t=60, b=40),
        height=400,
        title=dict(text=f"👤 {student_name} 학생", x=0.5, y=0.95, xanchor='center', font=dict(size=18)),
        dragmode=False
    )
    return fig

# 6. 메인 화면 출력
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # 엑셀 상단 제목의 공백 제거 (매우 중요!)
        df.columns = [c.strip() for c in df.columns]
        
        st.success(f"✅ {len(df)}명의 데이터를 성공적으로 불러왔습니다!")
        st.write("---")
        
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.plotly_chart(create_radar_chart(row["이름"], calc_score(row)), use_container_width=True)
                st.write("---")
    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다: {e}")
else:
    st.info("👈 왼쪽 사이드바에서 아까 만드신 엑셀(CSV) 파일을 업로드해주세요!")
