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

# 3. 학년별 데이터 기준 및 항목 명칭 설정 (설명 추가)
if grade == "4학년":
    items = {
        "실천의지": "실천의지",
        "심폐지구력": "심폐지구력(왕복오래달리기)",
        "순발력": "순발력(50m 달리기)",
        "유연성": "유연성(앉아윗몸굽히기)",
        "근력": "근력·근지구력(악력)"
    }
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False},
        "순발력": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True},
        "유연성": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False},
        "근력": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False}
    }
else: # 6학년
    items = {
        "실천의지": "실천의지",
        "심폐지구력": "심폐지구력(오래달리기-걷기)",
        "순발력": "순발력(50m 달리기)",
        "유연성": "유연성(앉아윗몸굽히기)",
        "근력": "근력·근지구력(악력)"
    }
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True},
        "순발력": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True},
        "유연성": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False},
        "근력": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False}
    }

# 차트에 표시될 항목 이름 리스트
display_lbls = list(items.values())
p_display_lbls = display_lbls + [display_lbls[0]]

# 4. 점수 계산 함수
def calc_score(row):
    scores = []
    try:
        raw_v = float(row.get("심폐지구력", 0))
        if grade == "6학년":
            m = int(raw_v); s = int(round((raw_v - m) * 100))
            cardio_val = float(m * 60 + s)
        else:
            cardio_val = raw_v
    except:
        cardio_val = 0.0

    # 엑셀 데이터 매핑 (사용자 파일
