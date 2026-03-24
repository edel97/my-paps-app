import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 성장 기록")
st.write("---")
st.info("💡 평균 기록은 5점(중간), 1등급 만점은 10점(끝)으로 설계되었습니다.")

# 2. 설정
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. PAPS 정밀 기준 데이터 (avg: 평균/5점 위치, max: 1등급/10점 위치)
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

# 4. 입력
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("### 1차 (3월)")
    v1 = {k: st.number_input(f"{k}", value=float(v['avg']), key=f"1_{k}") for k, v in base.items()}
with col2:
    st.write("### 2차 (5월)")
    v2 = {k: st.number_input(f"{k}", value=float(v['avg']), key=f"2_{k}") for k, v in base.items()}

# 5. 점수 계산 (평균=5, 만점=10 선형 변환)
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k], v['avg'], v['max']
        if v['rev']: # 낮을수록 좋은 종목 (초)
            # 평균보다 빠르면 5~10점 사이, 느리면 0~5점 사이
            score = 5 + (avg - val) / (avg - mx) * 5
        else: # 높을수록 좋은 종목 (회, cm, kg)
            score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트 그리기
fig = go.Figure()
# 가이드라인 (평균 정오각형 선)
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), name='평균 기록', hoverinfo='none'))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v1), theta=p_lbls, fill='toself', name='1차(3월)', line=dict(color='#3498DB', width=3)))
if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v2), theta=p_lbls, fill='toself', name='2차(5월)', line=dict(color='#E74C3C', width=3)))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['', '평균', '1등급']),
        angularaxis=dict(tickfont=dict(size=10))
    ),
    dragmode=False, showlegend=True, height=550
)
st.plotly_chart(fig, use_container_width=True)

# 7. 표 데이터
st.write("### 📝 기록 데이터 확인")
df = pd.DataFrame({
    "종목": lbls,
    "1차(3월)": [f"{v1[k]} {base[k]['u']}" for k in lbls],
    "2차(5월)": [f"{v2[k]} {base[k]['u']}" for k in lbls],
    "1등급 기준": [f"{base[k]['max']} {base[k]['u']}" for k in lbls]
})
st.table(df)
