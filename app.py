import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 체력 성장 기록")
st.write("---")

# 🌟 학생들에게 전하는 따뜻한 메시지
st.info("""
**"기록은 숫자일 뿐, 어제보다 조금 더 나아지려고 노력한 나의 진심이 진짜!  
포기하지 않고 도전하는 우리가 멋지다! ✨
""")

# 2. 설정 메뉴
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 데이터 기준 (평균=5점, 충분한 성장=10점 위치)
if grade == "4학년":
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "왕복오래달리기(심폐지구력)": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False, "u": "회"},
        "50m 달리기(순발력)": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False, "u": "kg"}
    }
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "오래달리기-걷기(심폐지구력)": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
    }

# 4. 입력 칸
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("### 1차 (3월)")
    v1 = {k: st.number_input(f"{k}", value=float(v['avg']), key=f"1_{k}") for k, v in base.items()}
with col2:
    st.write("### 2차 (5월)")
    v2 = {k: st.number_input(f"{k}", value=float(v['avg']), key=f"2_{k}") for k, v in base.items()}

# 5. 점수 계산
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k], v['avg'], v['max']
        if v['rev']: score = 5 + (avg - val) / (avg - mx) * 5
        else: score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트 그리기
fig = go.Figure()

# 평균 가이드라인
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), name='평균 기록', hoverinfo='none'))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v1), theta=p_lbls, fill='toself', name='1차(3월)', line=dict(color='#3498DB', width=3)))
if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v2), theta=p_lbls, fill='toself', name='2차(5월)', line=dict(color='#E74C3C', width=3)))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['', '평균', '나의 잠재력']),
        angularaxis=dict(tickfont=dict(size=11))
    ),
    dragmode=False, showlegend=True, height=550
)
st.plotly_chart(fig, use_container_width=True)

# 7. 기록 데이터 확인 (비교 중심)
st.write("### 📝 기록 데이터 확인")
df = pd.DataFrame({
    "종목": lbls,
    "1차 기록(3월)": [f"{v1[k]} {base[k]['u']}" for k in lbls],
    "2차 기록(5월)": [f"{v2[k]} {base[k]['u']}" for k in lbls]
})
st.table(df)

# 8. 격려의 메시지
if "함께" in view_option:
    st.write("---")
    st.write("🎈 **선생님이 너에게 보내는 응원**")
    st.write("너의 오각형이 조금씩 넓어지는 것은 그만큼 네 마음과 몸이 튼튼해졌다는 증거야. 결과보다 중요한 건 오늘 하루도 최선을 다했다는 사실이란다. 정말 자랑스러워!")
