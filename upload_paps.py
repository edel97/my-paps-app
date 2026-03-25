import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 PAPS 일괄 생성", layout="wide")
st.markdown("<h2 style='text-align: center; font-size: 1.8rem;'>📊 우리 반 PAPS 그래프 일괄 생성</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader("학생 결과 파일(CSV)을 업로드하세요", type=["csv"])

st.sidebar.divider()
st.sidebar.header("⚙️ 기준 설정")
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 학년별 데이터 기준 설정
if grade == "4학년":
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        "심폐지구력": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False, "u": "회"},
        "순발력": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True, "u": "초"},
        "유연성": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False, "u": "cm"},
        "근력": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False, "u": "kg"}
    }
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False, "u": "점"},
        # 6학년 심폐지구력은 '초' 단위 기준 (낮을수록 좋은 rev: True)
        "심폐지구력": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True, "u": "초"},
        "순발력": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True, "u": "초"},
        "유연성": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False, "u": "cm"},
        "근력": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False, "u": "kg"}
    }

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 4. 점수 계산 함수 (6학년 분.초 변환 로직 포함)
def calc_score(row):
    scores = []
    
    # 심폐지구력 값 처리
    raw_cardio = float(row.get("심폐지구력", 0.0))
    if grade == "6학년":
        # 5.20 형태를 초로 변환 (5분 * 60 + 20초 = 320초)
        minutes = int(raw_cardio)
        seconds = int(round((raw_cardio - minutes) * 100))
        processed_cardio = float(minutes * 60 + seconds)
    else:
        processed_cardio = raw_cardio

    data_map = {
        "실천의지": row.get("실천의지", 5.0),
        "심폐지구력": processed_cardio,
        "순발력": row.get("순발력", 15.0),
        "유연성": row.get("유연성", 0.0),
        "근력": row.get("근력", 0.0)
    }
    
    for k, v in base.items():
        val = data_map[k]
        avg, mx = v['avg'], v['max']
        if
