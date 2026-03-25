import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 PAPS 일괄 생성", layout="wide")
st.markdown("<h2 style='text-align: center;'>📊 우리 반 PAPS 그래프 일괄 생성</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader("학생 결과 파일(CSV)을 업로드하세요", type=["csv"])

st.sidebar.divider()
st.sidebar.header("⚙️ 기준 설정")
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 3. 학년별 데이터 기준 및 항목 명칭
if grade == "4학년":
    items = ["실천의지", "심폐지구력\n(왕복오래달리기)", "순발력\n(50m 달리기)", "유연성\n(앉아윗몸굽히기)", "근력·근지구력\n(악력)"]
    base_vals = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False},
        "순발력": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True},
        "유연성": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False},
        "근력": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False}
    }
else: # 6학년
    items = ["실천의지", "심폐지구력\n(오래달리기-걷기)", "순발력\n(50m 달리기)", "유연성\n(앉아윗몸굽히기)", "근력·근지구력\n(악력)"]
    base_vals = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True},
        "순발력": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True},
        "유연성": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False},
        "근력": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False}
    }

p_items = items + [items[0]]

# 4. 메인 처리 로직
if uploaded_file is not None:
    try:
        # 인코딩 처리
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='cp949')
        
        df.columns = [c.strip() for c in df.columns]
        st.success(f"✅ {grade} {gender}학생 데이터를 분석했습니다!")
        
        cols = st.columns(3)
        for idx, row in df.iterrows():
            scores = []
            try:
                raw_cardio = float(row.get("심폐지구력", 0))
                if grade == "6학년":
                    m = int(raw_cardio)
                    s = int(round((raw_cardio - m) * 100))
                    cardio_final = float(m * 60 + s)
                else:
                    cardio_final = raw_cardio
            except:
                cardio_final = 0.0

            data_map = {
                "실천의지": float(row.get("실천의지", 5.0)),
                "심폐지구력": cardio_final,
                "순발력": float(row.get("순발력", 15.0)),
                "유연성": float(row.get("유연성", 0.0)),
                "근력": float(row.get("근력", 0.0))
            }

            for k, v in base_vals.items():
                val = data_map.get(k, 0.0)
                avg, mx = v['avg'], v['max']
                if v['rev']:
                    score = 5 + (avg - val) / (avg - mx) * 5
                else:
                    score = 5 + (val - avg) / (mx - avg) * 5
                scores.append(min(10.0, max(0.0, float(score))))
