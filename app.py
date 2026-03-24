import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 성장 기록") # 제목 수정
st.write("---")
st.info("💡 기록을 입력하고 '1, 2차 함께 비교하기'를 선택해 나의 성장을 확인해 보세요!")

# 2. 설정 메뉴
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("보고 싶은 기록을 선택하세요", ["1차 기록 보기", "2차 기록 보기", "1, 2차 함께 비교하기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 항목 정보 (단위 및 역전 여부만 설정)
items = {
    "실천의지": {"u": "점", "rev": False},
    "왕복오래달리기(심폐지구력)": {"u": "회", "rev": False},
    "50m 달리기(순발력)": {"u": "초", "rev": True},
    "앉아윗몸앞으로굽히기(유연성)": {"u": "cm", "rev": False},
    "악력(근력)": {"u": "kg", "rev": False}
}

# 4. 데이터 입력
st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)

with col1:
    st.write("### 1차 (3월)")
    vals1 = {k: st.number_input(f"{k}", value=0.0, key=f"1st_{k}") for k in items.keys()}

with col2:
    st.write("### 2차 (5월)")
    vals2 = {k: st.number_input(f"{k}", value=0.0, key=f"2nd_{k}") for k in items.keys()}

# 5. 점수 계산 (입력값 중 최대값에 맞춰 그래프 크기를 자동 조절)
def get_scores(vals_dict):
    scores = []
    for k, v in items.items():
        val = vals_dict[k]
        if v['rev']: # 달리기처럼 낮을수록 좋은 경우 (보정)
            # 기준값보다 빠를수록 높은 점수 (간단한 비례식 적용)
            s = max(0.1, 15.0 - val) 
        else:
            s = val
        scores.append(float(s))
    return scores + [scores[0]]

lbls = list(items.keys())
p_lbls = lbls + [lbls[0]]
s1, s2 = get_scores(vals1), get_scores(vals2)
max_range = max(max(s1), max(s2), 10.0) * 1.1 # 입력값 중 가장 큰 값에 맞춰 눈금 자동 조절

# 6. 차트 그리기
fig = go.Figure()

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=s1, theta=p_lbls, fill='toself', name='1차 기록(3월)',
        line=dict(color='#3498DB'), fillcolor='rgba(52, 152, 219, 0.3)'
    ))

if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(
        r=s2, theta=p_lbls, fill='toself', name='2차 기록(5월)',
        line=dict(color='#E74C3C'), fillcolor='rgba(231, 76, 60, 0.3)'
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, max_range], showticklabels=False)),
    showlegend=True, dragmode=False
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

# 7. 데이터 표
st.write("### 📝 기록 데이터 확인")
df_compare = pd.DataFrame({
    "종목": lbls,
    "1차 기록(3월)": [f"{vals1[k]} {items[k]['u']}" for k in lbls],
    "2차 기록(5월)": [f"{vals2[k]} {items[k]['u']}" for k in lbls]
})
st.table(df_compare)
