import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 정밀 진단", layout="wide")
st.markdown("<h2 style='text-align: center;'>🏆 국가공인 PAPS 기준 정밀 진단 (1·2차 비교)</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.write("### 📝 학급 설정")
grade = st.sidebar.selectbox("학년 선택", ["4학년", "6학년"])

st.sidebar.divider()
st.sidebar.write("### 📥 업로드용 양식 다운로드")
st.sidebar.caption("아래 양식을 다운받아 학생들의 기록을 입력한 뒤 업로드해 줘!")

# 다운로드용 템플릿(양식) 데이터 만들기
template_df = pd.DataFrame({
    "이름": ["홍길동", "유관순"],
    "성별": ["남", "여"],
    "실천의지": [5.0, 5.0],
    "심폐지구력": [429.0, 429.0] if grade == "6학년" else [45.0, 40.0],
    "순발력": [10.0, 10.7] if grade == "6학년" else [10.5, 11.0],
    "유연성": [1.0, 6.2] if grade == "6학년" else [1.0, 5.0],
    "근력": [19.0, 19.0] if grade == "6학년" else [15.0, 13.5]
})

# 엑셀 한글 깨짐 완벽 해결
csv_template = template_df.to_csv(index=False).encode('utf-8-sig')

st.sidebar.download_button(
    label="📄 CSV 입력 양식 다운로드", 
    data=csv_template, 
    file_name="PAPS_입력양식.csv", 
    mime="text/csv"
)

st.sidebar.divider()
st.sidebar.write("### 📂 데이터 업로드")
up_file1 = st.sidebar.file_uploader("1차 기록(CSV) 업로드", type=["csv"])
up_file2 = st.sidebar.file_uploader("2차 기록(CSV) 업로드 (선택)", type=["csv"])

# 3. 등급표 기반 수치 반환 함수
def get_base(student_grade, student_gender):
    if student_grade == "4학년":
        return {
            "실천의지": [5.0, 10.0, 0],
            "왕복오래달리기(심폐지구력)": [45.0 if student_gender=="남" else 40.0, 103.0 if student_gender=="남" else 100.0, 0], 
            "50m 달리기(순발력)": [10.5 if student_gender=="남" else 11.0, 8.7 if student_gender=="남" else 9.3, 1],
            "앉아윗몸앞으로굽히기(유연성)": [1.0 if student_gender=="남" else 5.0, 18.0 if student_gender=="남" else 22.0, 0],
            "악력(근력)": [15.0 if student_gender=="남" else 13.5, 36.0 if student_gender=="남" else 33.6, 0]
        }
    else: # 6학년
        return {
            "실천의지": [5.0, 10.0, 0],
            "오래달리기-걷기(심폐지구력)": [379.0 if student_gender=="남" else 429.0, 243.0 if student_gender=="남" else 243.0, 1],
            "50m 달리기(순발력)": [10.0 if student_gender=="남" else 10.7, 7.77 if student_gender=="남" else 8.66, 1],
            "앉아윗몸앞으로굽히기(유연성)": [1.0 if student_gender=="남" else 6.2, 18.0 if student_gender=="남" else 26.0, 0],
            "악력(근력)": [19.0 if student_gender=="남" else 19.0, 39.4 if student_gender=="남" else 39.0, 0]
        }

def load_csv(file):
    try: 
        df = pd.read_csv(file, encoding='utf-8-sig')
    except: 
        file.seek(0)
        df = pd.read_csv(file, encoding='cp949')
    df.columns = [c.strip() for c in df.columns]
    return df

def get_val_robust(row_data, keywords, default_val):
    for col, val in row_data.items():
        clean_col = str(col).replace(" ", "").replace("_", "")
        for kw in keywords:
            if kw in clean_col:
                try:
                    return float(val)
                except:
                    pass
    return default_val

def calculate_scores(row_data, current_grade, current_gender):
    base = get_base(current_grade, current_gender)
    
    v_raw_cardio = get_val_robust(row_data, ["심폐", "오래달리기", "왕복"], 0.0)
    if current_grade == "6학년":
        cardio = int(v_raw_cardio)*60 + int(round((v_raw_cardio-int(v_raw_cardio))*100))
    else: 
        cardio = v_
