import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 성장 기록기", layout="centered")

st.title("🌱 나의 성장 기록: 어제의 나를 넘어서")
st.write("---")
st.info("💡 기록을 입력하고 '1, 2차 함께 보기'를 눌러 나의 성장을 확인해 보세요!")

# 2. 학생 정보 및 보기 설정
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록을 선택하세요", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 항목 및 기준 설정 (비교를 위한 고정 범위 설정)
if grade == "4학년":
    items = {
        "실천의지": {"max": 10.0, "rev": False, "u": "점", "min": 0.0},
        "왕복오래달리기(심폐지구력)": {"max": 60.0, "rev": False, "u": "회", "min": 0.0},
        "50m 달리기(순발력)": {"max": 8.0, "rev": True, "u": "초", "min": 12.0},
        "앉아윗몸앞으로굽히기(유연성)": {"max": 25.0, "rev": False, "u": "cm", "min": -10.0},
        "악력(근력)": {"max": 25.0, "rev": False, "u": "kg", "min": 0.0}
    }
else:
    items = {
        "실천의지": {"max": 10.0, "rev": False, "u": "점", "min": 0.0},
        "오래달리기-걷기(심폐지구력)": {"max": 200.0, "rev": True, "u": "초", "min": 500.0},
        "50m 달리기(순발력)": {"max": 7.0, "rev": True, "u": "초", "min": 11.0},
        "앉아윗몸앞으로굽히기(유연성)": {"max": 28.0, "rev": False, "u": "cm", "min": -10.0},
        "악력(근력)": {"max": 35.0, "rev": False, "u": "kg", "min": 0.0}
    }

# 4. 1차 & 2차 기록 입력
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)

with col1:
    st.write("### 1차 (3월)")
    vals1 = {}
    for k, v in items.items():
        vals1[k] = st.number_input(f"{k}", value=float(v['min']), key=f"1st_{k}")

with col2:
    st.write("### 2차 (5월)")
    vals2 = {}
    for k, v in items.items():
        vals2[k] = st.number_input(f"{k}", value=float(v['min']), key=f"2nd_{k}")

# 5. 점수 계산 함수 (최저~최대 범위를 0~10점으로 환산)
def get_scores(vals_dict):
    scores = []
    for k, v in items.items():
        val = vals_dict[k]
        if v['rev']: # 낮을수록 좋은 종목
            s = (v['min'] - val) / (v['min'] - v['max']) * 10
        else: # 높을수록 좋은 종목
            s = (val - v['min']) / (v['max'] - v['min']) * 10
        scores.append(min(10.0, max(0.0, float(s))))
    return scores + [scores[0]]

lbls = list(items.keys())
p_lbls = lbls + [lbls[0]]

# 6. 차트 그리기
fig = go.Figure()

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=get_scores(vals1), theta=p_lbls, fill='toself',
        name='1차 기록 (3월)', line=dict(color='#3498DB'), fillcolor='rgba(52, 152, 219, 0.3)'
    ))

if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=get_scores(vals2), theta=p_lbls, fill='toself',
        name='2차 기록 (5월)', line=dict(color='#E74C3C'), fillcolor='rgba(231, 76, 60, 0.3)'
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['', '', ''])),
    showlegend=True, dragmode=False
)

st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': True})

# 7. 성장 메시지
if "함께" in view_option:
    s1, s2 = sum(get_scores(vals1)[:-1]), sum(get_scores(vals2)[:-1])
    if s2 > s1:
        st.balloons()
        st.success(f"🎊 대단해요! 3월보다 총점이 {((s2-s1)/s1*100):.1f}% 성장했어요!")
    elif s2 == s1 and s1 > 0:
        st.info("실력을 잘 유지하고 있네요! 꾸준함이 가장 큰 재능이에요.")

# 8. 데이터 표
st.write("### 📝 기록 데이터 확인")
df_compare = pd.DataFrame({
    "종목": lbls,
    "1차 기록(3월)": [f"{vals1[k]} {items[k]['u']}" for k in lbls],
    "2차 기록(5월)": [f"{vals2[k]} {items[k]['u']}" for k in lbls]
})
st.table(df_compare)
