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

# 💡 엑셀 한글 깨짐 완벽 해결: .encode('utf-8-sig')로 바이트 강제 변환
csv_template = template_df.to_csv(index=False).encode('utf-8-sig')

st.sidebar.download_button(
    label="📄 CSV 입력 양식 다운로드", 
    data=csv_template, 
    file_name="PAPS_입력양식.csv", 
    mime="text/csv"
)

st.sidebar.divider()
st.sidebar.write("### 📂 데이터 업로드")
st.sidebar.caption("※ 다운받은 양식에 맞춰 '이름'과 '성별'을 꼭 적어줘.")
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

# CSV 읽기 헬퍼 함수
def load_csv(file):
    try: 
        df = pd.read_csv(file, encoding='utf-8-sig')
    except: 
        file.seek(0)
        df = pd.read_csv(file, encoding='cp949')
    df.columns = [c.strip() for c in df.columns]
    return df

# 점수 계산 헬퍼 함수
def calculate_scores(row_data, current_grade, current_gender):
    base = get_base(current_grade, current_gender)
    v_raw = float(row_data.get("심폐지구력", 0))
    if current_grade == "6학년":
        cardio = int(v_raw)*60 + int(round((v_raw-int(v_raw))*100))
    else: 
        cardio = v_raw
        
    d_map = {
        "실천의지": float(row_data.get("실천의지", 5)),
        "심폐지구력": cardio,
        "순발력": float(row_data.get("순발력", 15)),
        "유연성": float(row_data.get("유연성", 0)),
        "근력": float(row_data.get("근력", 0))
    }
    
    sc = []
    for k, b in base.items():
        val = next((v for key, v in d_map.items() if key in k), 5.0)
        s = 5+(b[0]-val)/(b[0]-b[1])*5 if b[2] else 5+(val-b[0])/(b[1]-b[0])*5
        sc.append(min(10.0, max(0.0, float(s))))
    return sc

# 4. 데이터 처리 및 차트 그리기
if up_file1 or up_file2:
    try:
        df1 = load_csv(up_file1) if up_file1 else None
        df2 = load_
