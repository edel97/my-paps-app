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

# 3. 데이터 기준 및 종목 이름 설정 (체력 명칭 추가)
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

# 4. 입력 섹션 (오류 방지를 위한 탭 구조 유지)
st.sidebar.divider()
st.sidebar.write("### 📝 기록 입력")
tab1, tab2 = st.sidebar.tabs(["1차 (3월)", "2차 (5월)"])

def input_val(label, v_info, key_p, tab_obj):
    with tab_obj:
        # 심폐지구력 항목이면서 6학년인 경우만 분/초 입력
        if grade == "6학년" and "심폐지구력" in label:
            st.write(f"{label}")
            m = st.number_input("분", value=int(v_info['avg'] // 60), key=f"{key_p}_{label}_m", min_value=0)
            s = st.number_input("초", value=int(v_info['avg'] % 60), key=f"{key_p}_{label}_s", min_value=0, max_value=59)
            return float(m * 60 + s)
        else:
            return st.number_input(f"{label} ({v_info['u']})", value=float(v_info['avg']), key=f"{key_p}_{label}")

v1 = {k: input_val(k, v, "1", tab1) for k, v in base.items()}
v2 = {k: input_val(k, v, "2", tab2) for k, v in base.items()}

# 5. 점수 계산 함수
def calc_score(vals):
    scores = []
    for k, v in base.items():
        val, avg, mx = vals[k],
