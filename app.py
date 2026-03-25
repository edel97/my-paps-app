import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

# 🛠️ 제목 설정
st.markdown("<h2 style='text-align: center; font-size: 1.5rem;'>🌱 나의 성장 기록</h2>", unsafe_allow_html=True)
st.write("---")

# 🌟 선생님 응원 멘트
st.info("🌟 기록은 숫자일 뿐, 어제보다 나아지려고 애쓴 너의 노력이 진짜!")

# 2. 설정 메뉴 (5학년 삭제)
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("기록 보기", ["1차 기록", "2차 기록", "1, 2차 함께 보기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 2026 국가기준 (선생님 파일 정밀 분석 결과: 평균=3등급 하한, 만점=1등급 하한)
if grade == "4학년":
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "왕복오래달리기(심폐지구력)": {"avg": 45.0 if gender == "남" else 40.0, "max": 96.0 if gender == "남" else 77.0, "rev": False, "u": "회"},
        "50m 달리기(순발력)": {"avg": 10.5 if gender == "남" else 11.0, "max": 8.8 if gender == "남" else 9.4, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 1.0 if gender == "남" else 5.0, "max": 8.0 if gender == "남" else 10.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 15.0 if gender == "남" else 13.5, "max": 31.0 if gender == "남" else 29.0, "rev": False, "u": "kg"}
    }
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        # 6학년 오래달리기-걷기 (남 1등급:250초/3등급:379초, 여 1등급:299초/3등급:429초)
        "오래달리기-걷기(심폐지구력)": {"avg": 379.0 if gender == "남" else 429.0, "max": 250.0 if gender == "남" else 299.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"avg": 10.0 if gender == "남" else 10.7, "max": 8.1 if gender == "남" else 8.9, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 1.0 if gender == "남" else 5.0, "max": 8.0 if gender == "남" else 14.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 19.0 if gender == "남" else 19.0, "max": 35.0 if gender == "남" else 33.0, "rev": False, "u": "kg"}
    }

# 4. 입력 섹션
st.sidebar.divider()
st.sidebar.write("### 📝 기록 입력")
tab1, tab2 = st.sidebar.tabs(["1차 기록", "2차 기록"])

v1, v2 = {}, {}

with tab1:
    for k, v in base.items():
        if grade == "6학년" and "심폐지구력" in k:
            st.write(f"**{k}**")
            m1 = st.number_input("분", value=int(v['avg'] // 60), key=f"1_{k}_m", min_value=0)
            s1 = st.number_input("초", value=int(v['avg'] % 60), key=f"1_{k}_s", min_value=0, max_value=59)
            v1[k] = float(m1 * 60 + s1)
        else:
            v1[k] = st.number_input(f"{k} ({v['u']})", value=float(v['avg']), key=f"1_{k}")

with tab2:
    for k, v in base.items():
        if grade == "6학년" and "심폐지구력" in k:
            st.write(f"**{k}**")
            m2 = st.number_input("분", value=int(v['avg'] // 60), key=f"2_{k}_m", min_value=0)
            s2 = st.number_input("초", value=int(v['avg'] % 60), key=f"2_{k}_s", min_value=0, max_value=59)
            v2[k] = float(m2 * 60 + s2)
        else:
            v2[k] = st.number_input(f"{k} ({v['u']})", value=float(v['avg']), key=f"2_{k}")

# 5. 점수 계산
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k], v['avg'], v['max']
        if v['rev']: # 낮을수록 좋은 종목 (초 등)
            score = 5 + (avg - val) / (avg - mx) * 5
        else: # 높을수록 좋은 종목 (회, cm 등)
            score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트 그리기
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='#BDC3C7', dash='dot', width=1), name='국가평균(3등급 하한)'))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v1), theta=p_lbls, fill='toself', name='1차 기록', line=dict(color='#3498DB', width=3)))

if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v2), theta=p_lbls, fill='toself', name='2차 기록', line=dict(color='#E74C3C', width=3)))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균'])),
    showlegend=True, margin=dict(l=80, r=80, t=50, b=50), height=500
)
st.plotly_chart(fig, use_container_width=True)

# 7. 데이터 표 출력
st.write("### 📝 기록 데이터 확인")
def format_val(val, label, unit):
    if grade == "6학년" and "심폐지구력" in label:
        return f"{int(val // 60)}분 {int(val % 60)}초"
    return f"{val} {unit}"

df_res = {
    "종목": lbls,
    "1차 기록": [format_val(v1[k], k, base[k]['u']) for k in lbls],
    "2차 기록": [format_val(v2[k], k, base[k]['u']) for k in lbls]
}
st.table(pd.DataFrame(df_res))
