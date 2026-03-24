import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 성장 기록기", layout="centered")

st.title("🌱 나의 체력 성장 기록하기")
st.write("---")
st.info("💡 오른쪽 위 카메라 아이콘(📷)을 눌러 차트를 이미지로 저장하세요.")

# 2. 학생 정보 입력
st.sidebar.header("🏫 학생 정보 입력")
grade = st.sidebar.selectbox("학년을 선택하세요", ["4학년", "6학년"])
gender = st.sidebar.radio("성별을 선택하세요", ["남", "여"])

# 3. 기준 데이터 설정 (1등급/만점 기준 적용)
# ref: 1등급 점수, rev: 낮을수록 좋은 종목(시간), min_val: 입력 최소값
if grade == "4학년":
    items = {
        "실천의지(정신력)": {"ref": 10.0, "rev": False, "u": "점", "min_val": 0.0},
        "왕복오래달리기(심폐지구력)": {"ref": 53.0 if gender == "남" else 43.0, "rev": False, "u": "회", "min_val": 0.0},
        "50m 달리기(순발력)": {"ref": 8.7 if gender == "남" else 9.4, "rev": True, "u": "초", "min_val": 5.0},
        "앉아윗몸앞으로굽히기(유연성)": {"ref": 16.0 if gender == "남" else 19.0, "rev": False, "u": "cm", "min_val": -10.0},
        "악력(근력)": {"ref": 22.1 if gender == "남" else 20.2, "rev": False, "u": "kg", "min_val": 0.0}
    }
else: # 6학년
    items = {
        "실천의지(정신력)": {"ref": 10.0, "rev": False, "u": "점", "min_val": 0.0},
        "오래달리기-걷기(심폐지구력)": {"ref": 257.0 if gender == "남" else 332.0, "rev": True, "u": "초", "min_val": 100.0},
        "50m 달리기(순발력)": {"ref": 8.1 if gender == "남" else 8.8, "rev": True, "u": "초", "min_val": 5.0},
        "앉아윗몸앞으로굽히기(유연성)": {"ref": 18.0 if gender == "남" else 21.0, "rev": False, "u": "cm", "min_val": -10.0},
        "악력(근력)": {"ref": 30.6 if gender == "남" else 28.5, "rev": False, "u": "kg", "min_val": 0.0}
    }

# 4. 기록 입력
st.sidebar.divider()
st.sidebar.write(f"### 📊 기록 입력")
vals = {}
for k, v in items.items():
    if "실천의지" in k:
        vals[k] = st.sidebar.slider(f"{k} (1~10점)", 1, 10, 5)
    else:
        vals[k] = st.sidebar.number_input(f"{k} ({v['u']})", value=float(v['ref']), min_value=float(v['min_val']))

# 5. 점수 계산 (1등급 기준 10점 만점 설계)
scores = []
for k, v in items.items():
    val, ref = vals[k], v['ref']
    
    if "유연성" in k: # 유연성은 -10부터 시작하므로 보정 계산
        # -10cm를 0점으로, 1등급(ref)을 10점으로 변환
        score = ((val + 10) / (ref + 10)) * 10
    elif v['rev']: # 낮을수록 좋은 종목 (시간)
        # 1등급 기록(ref)일 때 10점이 나오도록 계산
        score = (ref / val) * 10
    else: # 높을수록 좋은 종목 (횟수, 근력)
        score = (val / ref) * 10
    
    scores.append(min(10.0, max(0.0, float(score))))

lbls = list(items.keys())
p_lbls = lbls + [lbls[0]]
p_scrs = scores + [scores[0]]

# 6. 차트 그리기
fig = go.Figure()

# 평균기록선 (중간 등급인 5점 지점)
fig.add_trace(go.Scatterpolar(
    r=[5]*6, theta=p_lbls, 
    line=dict(color='gray', dash='dash'), 
    name='평균기록', hoverinfo='none'
))

# 나의 기록
fig.add_trace(go.Scatterpolar(
    r=p_scrs, theta=p_lbls, fill='toself', 
    line=dict(color='#2ECC71', width=3), 
    fillcolor='rgba(46, 204, 113, 0.3)',
    name='나의 기록'
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['최저', '평균', '1등급'])
    ),
    showlegend=True,
    dragmode=False
)

st.plotly_chart(fig, use_container_width=True, config={
    'staticPlot': False, 
    'scrollZoom': False,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
})

# 7. 기록 요약 표
st.write("### 📝 나의 측정 결과 요약")
df_data = {
    "종목": lbls,
    "나의 기록": [f"{vals[k]} {items[k]['u']}" for k in lbls],
    "1등급 기준": [f"{items[k]['ref']} {items[k]['u']}" for k in lbls]
}
st.table(pd.DataFrame(df_data))
