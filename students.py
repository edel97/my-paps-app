import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")
st.markdown("<h2 style='text-align: center; font-size: 1.5rem;'>🌱 우리 반 PAPS 성장 기록</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 학생 데이터 (보내주신 명단 17명 기록)
# 6학년 기준, 심폐지구력은 '초' 단위로 변환하여 입력했습니다.
students_data = {
    "권0나": [62, 10.30, 12.0, 14.9], "김0재": [79, 9.24, 7.0, 18.8],
    "김0윤": [22, 11.33, 5.2, 11.8], "김0언": [79, 9.34, 17.2, 17.6],
    "김0준": [53, 9.97, 9.0, 18.9], "박0서": [39, 10.60, 10.0, 13.6],
    "박0정": [70, 9.29, 10.0, 16.3], "박0진": [68, 9.29, 8.5, 14.4],
    "박0균": [72, 10.21, 16.0, 12.7], "백0유": [100, 8.63, 11.4, 12.7],
    "송0준": [24, 15.00, -20.0, 7.1], "안0솜": [30, 10.92, 16.5, 15.8],
    "여0철": [100, 9.04, 10.3, 16.6], "오0민": [28, 10.61, 10.5, 13.4],
    "이0현": [72, 9.41, 19.0, 13.2], "이0섭": [25, 10.06, -6.0, 17.4],
    "조0서": [13, 13.64, 13.0, 10.2]
}

# 3. 사이드바 설정
st.sidebar.header("👤 학생 선택")
selected_student = st.sidebar.selectbox("이름을 선택하세요", list(students_data.keys()))
gender = st.sidebar.radio("성별", ["남", "여"])
st.sidebar.divider()

# 선택된 학생 데이터 가져오기
s_rec = students_data[selected_student]

# 4. 기준치 설정 (6학년 고정)
base = {
    "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
    "오래달리기-걷기(심폐지구력)": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
    "50m 달리기(순발력)": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
    "앉아윗몸앞으로굽히기(유연성)": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
    "악력(근력)": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
}

# 5. 데이터 가공 (1차 기록에 학생 데이터 매칭)
v1 = {
    "실천의지": 5.0, # 실천의지는 기본 5점 설정
    "오래달리기-걷기(심폐지구력)": float(s_rec[0]),
    "50m 달리기(순발력)": float(s_rec[1]),
    "앉아윗몸앞으로굽히기(유연성)": float(s_rec[2]),
    "악력(근력)": float(s_rec[3])
}

# 2차 기록은 입력받을 수 있게 유지
st.sidebar.write(f"### 📝 {selected_student} 학생 2차 기록")
v2 = {}
for k, v in base.items():
    v2[k] = st.sidebar.number_input(f"{k} (2차)", value=float(v['avg']), key=f"2_{k}")

# 6. 점수 계산 및 차트 그리기
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k], v['avg'], v['max']
        score = 5 + (avg - val) / (avg - mx) * 5 if v['rev'] else 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

lbls = list(base.keys()); p_lbls = lbls + [lbls[0]]
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot'), name='평균'))
fig.add_trace(go.Scatterpolar(r=calc_score(v1), theta=p_lbls, fill='toself', name='1차(3월)', line=dict(color='#3498DB')))
fig.add_trace(go.Scatterpolar(r=calc_score(v2), theta=p_lbls, fill='toself', name='2차(5월)', line=dict(color='#E74C3C')))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균'])),
    margin=dict(l=80, r=80, t=50, b=50), dragmode=False
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

st.info(f"**{selected_student}** 학생, 기록은 숫자일 뿐! 너의 노력이 진짜야! ✨")
