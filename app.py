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

# 2. 설정 메뉴 (5학년 제외)
st.sidebar.header("⚙️ 설정")
view_option = st.sidebar.radio("기록 보기", ["1차 기록", "2차 기록", "1, 2차 함께 보기"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 2026 국가기준 (평균=3등급 하한, 만점=1등급 하한)
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
            v2[k] = float(m
