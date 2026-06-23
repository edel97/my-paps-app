import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 정밀 진단", layout="wide")
st.markdown("<h2 style='text-align: center;'>🏆 국가공인 PAPS 기준 정밀 진단 (1·2차 비교)</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.write("### 📝 학급 설정")
grade = st.sidebar.selectbox("학년 선택", ["4학년", "6학년"])
gender = st.sidebar.radio("성별 선택", ["남", "여"])

st.sidebar.divider()
st.sidebar.write("### 📂 데이터 업로드")
st.sidebar.caption("※ '이름' 컬럼을 기준으로 1차와 2차 기록을 비교합니다.")
up_file1 = st.sidebar.file_uploader("1차 기록(CSV) 업로드", type=["csv"])
up_file2 = st.sidebar.file_uploader("2차 기록(CSV) 업로드 (선택)", type=["csv"])

# 3. 등급표 기반 수치 설정 [평균, 만점, 반비례여부(1은 작을수록 좋음)]
if grade == "4학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "왕복오래달리기(심폐지구력)": [45.0 if gender=="남" else 40.0, 103.0 if gender=="남" else 100.0, 0], 
        "50m 달리기(순발력)": [10.5 if gender=="남" else 11.0, 8.7 if gender=="남" else 9.3, 1],
        "앉아윗몸앞으로굽히기(유연성)": [1.0 if gender=="남" else 5.0, 18.0 if gender=="남" else 22.0, 0],
        "악력(근력)": [15.0 if gender=="남" else 13.5, 36.0 if gender=="남" else 33.6, 0]
    }
else: # 6학년
    base = {
        "실천의지": [5.0, 10.0, 0],
        "오래달리기-걷기(심폐지구력)": [379.0 if gender=="남" else 429.0, 243.0 if gender=="남" else 243.0, 1],
        "50m 달리기(순발력)": [10.0 if gender=="남" else 10.7, 7.77 if gender=="남" else 8.66, 1],
        "앉아윗몸앞으로굽히기(유연성)": [1.0 if gender=="남" else 6.2, 18.0 if gender=="남" else 26.0, 0],
        "악력(근력)": [19.0 if gender=="남" else 19.0, 39.4 if gender=="남" else 39.0, 0]
    }

lbls = list(base.keys())
display_items = [k.replace("(", "\n(") for k in lbls]

# CSV 읽기 헬퍼 함수
def load
