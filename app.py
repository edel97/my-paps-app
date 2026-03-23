import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="PAPS 성장 기록기", layout="centered")

st.title("🌱 나의 체력 성장 기록하기")
st.write("---")
st.subheader("평균 기준선과 나의 기록 비교")
st.info("💡 오른쪽 위 카메라 아이콘(📷)을 누르면 내 차트를 그림으로 저장할 수 있어요!")

# 2. 학생 정보 입력 (사이드바)
st.sidebar.header("🏫 학생 정보 입력")
grade = st.sidebar.selectbox("학년을 선택하세요", ["4학년", "6학년"])
gender = st.sidebar.radio("성별을 선택하세요", ["남", "여"])

# 3. 기준 데이터 설정 (선생님 제공 표 반영)
if grade == "4학년":
    items = {
        "실천의지": {"ref": 5.0, "rev": False, "u": "점"},
        "왕복오래달리기": {"ref": 45.0 if gender == "남" else 40.0, "rev": False, "u": "회"},
        "50m 달리기": {"ref": 9.71 if gender == "남" else 10.41, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기": {"ref": 1.0 if gender == "남" else 5.0, "rev": False, "u": "cm"},
        "악력": {"ref": 15.0 if gender == "남" else 13.5, "rev": False, "u": "kg"}
    }
else:
    items = {
        "실천의지": {"ref": 5.0, "rev": False, "u": "점"},
        "오래달리기-걷기": {"ref": 315.0 if gender == "남" else 458.0, "rev": True, "u": "초"},
        "50m 달리기": {"ref": 9.11 if gender == "남" else 9.81, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기": {"ref": 1.0 if gender == "남" else 5.0, "rev": False, "u": "cm"},
        "악력": {"ref": 19.0 if gender == "남" else 19.0, "rev": False, "u": "kg"}
    }

# 4. 기록 입력 섹션
st.sidebar.divider()
st.sidebar.write(f"### 📊 기록 입력")
vals = {}
for k, v in items.items():
    if k == "실천의지":
        vals[k] = st.sidebar.slider(f"{k} (1~10점)", 1, 10, 5)
    else:
        vals[k] = st.sidebar.number_input(f"{k} ({v['u']})", value=float(v['ref']))

# 5. 점수 계산 (5점=평균, 10점=최상위권 지향)
scores = []
for k, v in items.items():
    val, ref = vals[k], v['ref']
    if v['rev']: # 낮을수록 좋음 (시간)
        s = (ref / val * 5.0) if val > 0 else 0
    else: # 높을수록 좋음 (횟수/거리)
        r = ref if ref > 0 else 1.0
        s = (val / r * 5.0)
    scores.append(min(10.0, max(0.0, float(s))))

# 차트 데이터 준비
lbls = list(items.keys())
p_lbls = lbls + [lbls[0]]
p_scrs = scores + [scores[0]]

# 6. 차트 그리기
fig = go.Figure()

# 가이드라인 (평균 5점)
fig.add_trace(go.Scatterpolar(
    r=[5]*6, theta=p_lbls, 
    line=dict(color='rgba(150,150,150,0.5)', dash='dash'), 
    name='전국 평균', hoverinfo='none'
))

# 학생 기록
fig.add_trace(go.Scatterpolar(
    r=p_scrs, theta=p_lbls, fill='toself', 
    line=dict(color='#2ECC71', width=3), 
    fillcolor='rgba(46, 204, 113, 0.3)',
    name='나의 기록'
))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['0', '평균', '10'])),
    showlegend=True,
    height=500
)

# 차트 출력
st.plotly_chart(fig, use_container_width=True)

# 7. 기록 요약 표
st.write("### 📝 나의 측정 결과 요약")
df_data = {
    "종목": lbls,
    "나의 기록": [f"{vals[k]} {items[k]['u']}" for k in lbls],
    "평균(참고)": [f"{items[k]['ref']} {items[k]['u']}" for k in lbls]
}
st.table(pd.DataFrame(df_data))

st.success("✨ 이 화면을 캡처하거나 차트 위의 카메라 아이콘을 눌러 저장하세요!")