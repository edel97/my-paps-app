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
def load_csv(file):
    try: 
        df = pd.read_csv(file, encoding='utf-8-sig')
    except: 
        file.seek(0)
        df = pd.read_csv(file, encoding='cp949')
    df.columns = [c.strip() for c in df.columns]
    return df

# 점수 계산 헬퍼 함수
def calculate_scores(row_data):
    v_raw = float(row_data.get("심폐지구력", 0))
    if grade == "6학년":
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
        df2 = load_csv(up_file2) if up_file2 else None
        
        # 1차, 2차 데이터에 있는 모든 학생 이름 모으기 (중복 제거)
        names = []
        if df1 is not None and "이름" in df1.columns: names.extend(df1["이름"].dropna().tolist())
        if df2 is not None and "이름" in df2.columns: names.extend(df2["이름"].dropna().tolist())
        unique_names = sorted(list(set(names)))
        
        if not unique_names:
            st.warning("⚠️ 업로드된 파일에서 '이름' 컬럼을 찾을 수 없거나 데이터가 없습니다.")
        else:
            st.success(f"✅ {grade} {gender}학생 총 {len(unique_names)}명 분석 완료")
            cols = st.columns(3)
            
            for i, name in enumerate(unique_names):
                with cols[i%3]:
                    fig = go.Figure()
                    
                    # 기준선(평균)
                    fig.add_trace(go.Scatterpolar(r=[5]*6, theta=display_items+[display_items[0]], 
                                                  line=dict(color='#BDC3C7', dash='dot'), name='평균'))
                    
                    # 1차 기록 그리기 (투명도 30% 파란색 면 추가)
                    if df1 is not None and name in df1["이름"].values:
                        row1 = df1[df1["이름"] == name].iloc[0]
                        scores1 = calculate_scores(row1)
                        fig.add_trace(go.Scatterpolar(r=scores1+[scores1[0]], theta=display_items+[display_items[0]], 
                                                      fill='toself', fillcolor='rgba(52, 152, 219, 0.3)', 
                                                      name='1차 기록', line=dict(color='#3498DB', width=3)))
                        
                    # 2차 기록 그리기 (투명도 30% 빨간색 면 추가)
                    if df2 is not None and name in df2["이름"].values:
                        row2 = df2[df2["이름"] == name].iloc[0]
                        scores2 = calculate_scores(row2)
                        fig.add_trace(go.Scatterpolar(r=scores2+[scores2[0]], theta=display_items+[display_items[0]], 
                                                      fill='toself', fillcolor='rgba(231, 76, 60, 0.3)', 
                                                      name='2차 기록', line=dict(color='#E74C3C', width=3)))
                        
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
                            angularaxis=dict(tickfont=dict(size=10), rotation=90, direction="clockwise")
                        ),
                        showlegend=True, 
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                        height=480, margin=dict(l=60, r=60, t=50, b=50),
                        title=dict(text=f"👤 {name}", x=0.5, font=dict(size=17))
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.write("---")
                    
    except Exception as e: 
        st.error(f"⚠️ 파일 처리 중 오류가 발생했습니다: {e}")
