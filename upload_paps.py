import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 정밀 진단", layout="wide")
st.markdown("<h2 style='text-align: center;'>🏆 국가공인 PAPS 기준 정밀 진단</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
up_file = st.sidebar.file_uploader("학생 결과(CSV) 업로드", type=["csv"])
grade = st.sidebar.selectbox("학년 선택", ["4학년", "6학년"])
gender = st.sidebar.radio("성별 선택", ["남", "여"])

# 3. 등급표 기반 수치 설정 (실천의지를 첫 번째로 배치하여 12시 방향 고정)
if grade == "4학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "왕복오래달리기(심폐지구력)": [45.0 if gender=="남" else 40.0, 96.0 if gender=="남" else 77.0, 0], 
        "50m 달리기(순발력)": [10.5 if gender=="남" else 11.0, 8.8 if gender=="남" else 9.4, 1],
        "앉아윗몸앞으로굽히기(유연성)": [1.0 if gender=="남" else 5.0, 8.0 if gender=="남" else 10.0, 0],
        "악력(근력)": [15.0 if gender=="남" else 13.5, 31.0 if gender=="남" else 29.0, 0]
    }
else: # 6학년
    base = {
        "실천의지": [5.0, 10.0, 0],
        "오래달리기-걷기(심폐지구력)": [379.0 if gender=="남" else 429.0, 250.0 if gender=="남" else 299.0, 1],
        "50m 달리기(순발력)": [10.0 if gender=="남" else 10.7, 8.1 if gender=="남" else 8.9, 1],
        "앉아윗몸앞으로굽히기(유연성)": [1.0 if gender=="남" else 5.0, 8.0 if gender=="남" else 14.0, 0],
        "악력(근력)": [19.0 if gender=="남" else 19.0, 35.0 if gender=="남" else 33.0, 0]
    }

lbls = list(base.keys())
# 차트 표시용 이름 (줄바꿈 포함)
display_items = [k.replace("(", "\n(") for k in lbls]

# 4. 데이터 처리
if up_file:
    try:
        try: df = pd.read_csv(up_file, encoding='utf-8-sig')
        except: up_file.seek(0); df = pd.read_csv(up_file, encoding='cp949')
        df.columns = [c.strip() for c in df.columns]
        
        st.success(f"✅ {grade} {gender}학생 분석 완료")
        cols = st.columns(3)
        
        for i, row in df.iterrows():
            # 심폐지구력 처리 (6학년 분.초 변환)
            v_raw = float(row.get("심폐지구력", 0))
            if grade == "6학년":
                cardio = int(v_raw)*60 + int(round((v_raw-int(v_raw))*100))
            else: cardio = v_raw
            
            # 매핑 시 실제 컬럼명과 일치시키기 위해 '심폐지구력' 키워드로 찾음
            d_map = {
                "실천의지": float(row.get("실천의지", 5)),
                "심폐지구력": cardio,
                "순발력": float(row.get("순발력", 15)),
                "유연성": float(row.get("유연성", 0)),
                "근력": float(row.get("근력", 0))
            }
            
            scores = []
            # base의 키 순서대로 점수 계산 (실천의지가 가장 먼저)
            for k, b in base.items():
                # d_map에서 해당 키워드가 포함된 값을 가져옴
                val = next((v for key, v in d_map.items() if key in k), 5.0)
                s = 5+(b[0]-val)/(b[0]-b[1])*5 if b[2] else 5+(val-b[0])/(b[1]-b[0])*5
                scores.append(min(10.0, max(0.0, float(s))))
            
            with cols[i%3]:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[5]*6, theta=display_items+[display_items[0]], 
                                              line=dict(color='#BDC3C7', dash='dot'), name='평균'))
                fig.add_trace(go.Scatterpolar(r=scores+[scores[0]], theta=display_items+[display_items[0]], 
                                              fill='toself', name=row["이름"], line=dict(color='#2980B9', width=3)))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
                        # 회전각 90도로 설정하여 첫 번째 항목(실천의지)을 12시 방향으로 배치
                        angularaxis=dict(tickfont=dict(size=10), rotation=90, direction="clockwise")
                    ),
                    showlegend=False, height=430, margin=dict(l=80, r=80, t=50, b=50),
                    title=dict(text=f"👤 {row['이름']}", x=0.5, font=dict(size=17)))
                st.plotly_chart(fig, use_container_width=True)
                st.write("---")
    except Exception as e: st.error(f"⚠️ 오류: {e}")
