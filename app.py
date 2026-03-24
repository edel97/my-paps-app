import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="나의 성장 기록", layout="centered")

st.title("🌱 나의 성장 기록")
st.write("---")

# 🌟 학생들에게 전하는 따뜻한 메시지
st.info("""
**"기록은 숫자일 뿐, 너의 노력은 반짝이는 별이야"** 남보다 잘하는 것보다 어제보다 조금 더 나아진 너의 모습이 훨씬 소중하단다.  
포기하지 않고 끝까지 달린 너의 마음을 이 그래프에 담아보렴! ✨
""")

# 2. 설정 메뉴
st.sidebar.header("⚙️ 설정")
my_class = st.sidebar.selectbox("우리 반을 선택하세요", ["1반", "2반", "3반", "4반"])
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
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "오래달리기-걷기(심폐지구력)": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
        "50m 달리기(순발력)": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
        "앉아윗몸앞으로굽히기(유연성)": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
        "악력(근력)": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
    }

# 4. 입력 함수
def input_record(label, v_info, key_prefix):
    if v_info['u'] == "초" and "심폐지구력" in label:
        st.sidebar.write(f"**{label}**")
        c_m, c_s = st.sidebar.columns(2)
        with c_m:
            m = st.number_input("분", value=int(v_info['avg'] // 60), key=f"{key_prefix}_{label}_m", min_value=0)
        with c_s:
            s = st.number_input("초", value=int(v_info['avg'] % 60), key=f"{key_prefix}_{label}_s", min_value=0, max_value=59)
        return float(m * 60 + s)
    else:
        return st.sidebar.number_input(f"{label} ({v_info['u']})", value=float(v_info['avg']), key=f"{key_prefix}_{label}")

st.sidebar.divider()
col1, col2 = st.sidebar.columns(2)
with col1:
    st.write("### 1차 (3월)")
    v1 = {k: input_record(k, v, "1") for k, v in base.items()}
with col2:
    st.write("### 2차 (5월)")
    v2 = {k: input_record(k, v, "2") for k, v in base.items()}

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
fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), name='평균 기록', hoverinfo='none'))

if "1차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v1), theta=p_lbls, fill='toself', name='1차(3월)', line=dict(color='#3498DB', width=3)))
if "2차" in view_option or "함께" in view_option:
    fig.add_trace(go.Scatterpolar(r=calc_score(v2), theta=p_lbls, fill='toself', name='2차(5월)', line=dict(color='#E74C3C', width=3)))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], tickvals=[0, 5, 10], ticktext=['', '평균', '나의 잠재력'])
    ),
    dragmode=False, showlegend=True, height=550
)
st.plotly_chart(fig, use_container_width=True)

# 7. 데이터 표 출력
def format_val(val, label, unit):
    if unit == "초" and "심폐지구력" in label:
        return f"{int(val // 60)}분 {int(val % 60)}초"
    return f"{val} {unit}"

st.write("### 📝 기록 데이터 확인")
df = pd.DataFrame({
    "종목": lbls,
    "1차 기록(3월)": [format_val(v1[k], k, base[k]['u']) for k in lbls],
    "2차 기록(5월)": [format_val(v2[k], k, base[k]['u']) for k in lbls]
})
st.table(df)

st.write(f"🎈 **{my_class} 친구들에게 보내는 응원**")
st.write("너의 오각형이 조금씩 넓어지는 것은 그만큼 네 마음과 몸이 튼튼해졌다는 증거야. 정말 자랑스러워!")
