import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 성장 기록")
st.write("---")
st.info("💡 모든 종목이 '평균'일 때 예쁜 정오각형이 그려집니다. 나의 성장을 확인해 보세요!")

# 2. 설정
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 기준 데이터 (이 수치를 입력하면 정오각형 '5점' 위치에 찍힙니다)
if grade == "4학년":
    base = {
        "실천의지": {"ref": 10.0, "rev": False, "u": "점"}, # 실천의지는 10점을 기준으로 설계
        "왕복오래달리기(심폐지구력)": {"ref": 40.0 if gender == "남" else 35.0, "rev": False, "u": "회"},
        "50m 달리기(순발력)": {"ref": 10.0 if gender == "남" else 11.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"ref": 10.0 if gender == "남" else 12.0, "rev": False, "u": "cm"},
        "악력(근력)": {"ref": 18.0 if gender == "남" else 16.0, "rev": False, "u": "kg"}
    }
else:
    base = {
        "실천의지": {"ref": 10.0, "rev": False, "u": "점"},
        "오래달리기-걷기(심폐지구력)": {"ref": 350.0 if gender == "남" else 450.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"ref": 9.0 if gender == "남" else 10.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"ref": 12.0 if gender == "남" else 15.0, "rev": False, "u": "cm"},
        "악력(근력)": {"ref": 25.0 if gender == "남" else 23.0, "rev": False, "u": "kg"}
    }

# 4. 입력
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("### 1차 (3월)")
    v1 = {k: st.number_input(f"{k}", value=float(v['ref']), key=f"1_{k}") for k, v in base.items()}
with col2:
    st.write("### 2차 (5월)")
    v2 = {k: st.number_input(f"{k}", value=float(v['ref']), key=f"2_{k}") for k, v in base.items()}

# 5. 표준화 점수 계산 (기준값 입력 시 무조건 5점이 나오도록)
def scale_score(vals):
    s = []
    for k, v in base.items():
        val, ref = vals[k], v['ref']
        if v['rev']: # 낮을수록 좋은 종목 (초)
            score = (ref / val) * 5 if val > 0 else 0
        else: # 높을수록 좋은 종목
            # 유연성 마이너스 고려: (값 + 10) / (기준 + 10) 방식으로 보정 가능하나 직관성을 위해 기본비율 적용
            score = (val / ref) * 5 if ref > 0 else 0
        s.append(min(10.0, max(0.0, float(score))))
    return s + [s[0]]

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트
fig = go.Figure()
# 가이드라인 (정오각형 기준선)
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='lightgray', dash='dot'), name='기준(평균)', hoverinfo='none'))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=scale_score(v1), theta=p_lbls, fill='toself', name='1차(3월)', line=dict(color='#3498DB')))
if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=scale_score(v2), theta=p_lbls, fill='toself', name='2차(5월)', line=dict(color='#E74C3C')))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['기준'])),
    dragmode=False, showlegend=True
)
st.plotly_chart(fig, use_container_width=True)

# 7. 표
st.write("### 📝 기록 데이터 확인")
st.table(pd.DataFrame({
    "종목": lbls, 
    "1차(3월)": [f"{v1[k]} {base[k]['u']}" for k in lbls],
    "2차(5월)": [f"{v2[k]} {base[k]['u']}" for k in lbls]
}))
