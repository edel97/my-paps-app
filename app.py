import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 성장 기록")
st.write("---")

# 🌟 선생님 요청 멘트
st.info("기록은 숫자일 뿐, 어제보다 나아지려고 애쓴 너의 노력이 진짜!")

# 2. 설정 메뉴
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 데이터 기준 설정
if grade == "4학년":
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "왕복오래달리기(심폐지구력)": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False, "u": "회"},
        "50m 달리기(순발력)": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False, "u": "kg"}
    }
else:
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "오래달리기-걷기(심폐지구력)": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
    }

# 4. 입력 섹션 (탭 구조)
st.sidebar.divider()
st.sidebar.write("### 📝 기록 입력")
tab1, tab2 = st.sidebar.tabs(["1차 (3월)", "2차 (5월)"])

v1, v2 = {}, {}

# 1차 기록 입력
with tab1:
    for k, v in base.items():
        if grade == "6학년" and "심폐지구력" in k:
            st.write(f"**{k}**")
            m1 = st.number_input("분", value=int(v['avg'] // 60), key=f"1_{k}_m", min_value=0)
            s1 = st.number_input("초", value=int(v['avg'] % 60), key=f"1_{k}_s", min_value=0, max_value=59)
            v1[k] = float(m1 * 60 + s1)
        else:
            v1[k] = st.number_input(f"{k} ({v['u']})", value=float(v['avg']), key=f"1_{k}")

# 2차 기록 입력
with tab2:
    for k, v in base.items():
        if grade == "6학년" and "심폐지구력" in k:
            st.write(f"**{k}**")
            m2 = st.number_input("분", value=int(v['avg'] // 60), key=f"2_{k}_m", min_value=0)
            s2 = st.number_input("초", value=int(v['avg'] % 60), key=f"2_{k}_s", min_value=0, max_value=59)
            v2[k] = float(m2 * 60 + s2)
        else:
            v2[k] = st.number_input(f"{k} ({v['u']})", value=float(v['avg']), key=f"2_{k}")

# 5. 점수 계산 함수
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k], v['avg'], v['max']
        if v['rev']:
            score = 5 + (avg - val) / (avg - mx) * 5
        else:
            score = 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트 그리기
fig = go.Figure()

# 평균 기준선
fig.add_trace(go.Scatterpolar(
    r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), 
    name='평균 기록', hoverinfo='none'
))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=calc_score(v1), theta=p_lbls, fill='toself', 
        name='1차(3월)', line=dict(color='#3498DB', width=3)
    ))

if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=calc_score(v2), theta=p_lbls, fill='toself', 
        name='2차(5월)', line=dict(color='#E74C3C', width=3)
    ))

# 🛠️ 가장 안전한 레이아웃 설정
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
        angularaxis=dict(tickfont=dict(size=11))
    ),
    showlegend=True,
    margin=dict(l=80, r=80, t=50, b=50),
    height=500
)

# 카메라 아이콘 포함 렌더링
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

# 7. 데이터 표 출력
def format_val(val, label, unit):
    if grade == "6학년" and "심폐지구력" in label:
        return f"{int(val // 60)}분 {int(val % 60)}초"
    return f"{val} {unit}"

st.write("### 📝 기록 데이터 확인")
df_data = {
    "종목": lbls,
    "1차 기록(3월)": [format_val(v1[k], k, base[k]['u']) for k in lbls],
    "2차 기록(5월)": [format_val(v2[k], k, base[k]['u']) for k in lbls]
}
st.table(pd.DataFrame(df_data))
