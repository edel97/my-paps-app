import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="PAPS 정밀 진단", layout="wide")
st.markdown("<h2 style='text-align: center;'>🏆 국가공인 PAPS 기준 정밀 진단</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
up_file = st.sidebar.file_uploader("학생 결과(CSV) 업로드", type=["csv"])
grade = st.sidebar.selectbox("학년 선택", ["4학년", "5학년", "6학년"])
gender = st.sidebar.radio("성별 선택", ["남", "여"])

# 3. 등급표 기반 수치 설정 (평균=3등급 최하위, 만점=1등급 최하위)
# [3등급 커트라인(5점), 1등급 커트라인(10점), 역산여부]
if grade == "4학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "심폐지구력": [18.0 if gender=="남" else 12.0, 40.0 if gender=="남" else 29.0, 0], 
        "순발력": [11.0 if gender=="남" else 11.6, 8.8 if gender=="남" else 9.3, 1],
        "유연성": [1.4 if gender=="남" else 4.2, 14.3 if gender=="남" else 17.3, 0],
        "근력": [13.4 if gender=="남" else 12.1, 21.6 if gender=="남" else 19.3, 0]
    }
elif grade == "5학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "심폐지구력": [23.0 if gender=="남" else 15.0, 51.0 if gender=="남" else 36.0, 0], 
        "순발력": [10.2 if gender=="남" else 10.9, 8.3 if gender=="남" else 8.8, 1],
        "유연성": [2.3 if gender=="남" else 5.8, 16.5 if gender=="남" else 19.6, 0],
        "근력": [15.9 if gender=="남" else 14.1, 26.2 if gender=="남" else 23.3, 0]
    }
else: # 6학년
    base = {
        "실천의지": [5.0, 10.0, 0],
        # 6학년 심폐(시간): 남 3등급(8분40초=520초), 1등급(6분10초=370초) / 여 3등급(9분50초=590초), 1등급(7분20초=440초)
        "심폐지구력": [520.0 if gender=="남" else 590.0, 370.0 if gender=="남" else 440.0, 1],
        "순발력": [9.6 if gender=="남" else 10.4, 7.8 if gender=="남" else 8.3, 1],
        "유연성": [3.6 if gender=="남" else 7.5, 18.9 if gender=="남" else 22.3, 0],
        "근력": [18.7 if gender=="남" else 16.7, 31.7 if gender=="남" else 28.1, 0]
    }

display_items = ["실천의지", "심폐지구력\n(오래달리기)", "순발력\n(50m달리기)", "유연성\n(앉아윗몸굽히기)", "근력\n(악력)"]

# 4. 데이터 처리
if up_file:
    try:
        try: df = pd.read_csv(up_file, encoding='utf-8-sig')
        except: up_file.seek(0); df = pd.read_csv(up_file, encoding='cp949')
        df.columns = [c.strip() for c in df.columns]
        
        st.success(f"✅ {grade} {gender}학생 분석 완료 (평균선: 3등급 최하위 기준)")
        cols = st.columns(3)
        
        for i, row in df.iterrows():
            v_raw = float(row.get("심폐지구력", 0))
            if grade == "6학년":
                cardio = int(v_raw)*60 + int(round((v_raw-int(v_raw))*100))
            else: cardio = v_raw
            
            d_map = {"실천의지":float(row.get("실천의지",5)), "심폐지구력":cardio, "순발력":float(row.get("순발력",15)),
                     "유연성":float(row.get("유연성",0)), "근력":float(row.get("근력",0))}
            
            scores = []
            for k, b in base.items():
                v = d_map[k]
                # 선형 변환: 3등급 커트라인(5점) ~ 1등급 커트라인(10점)
                s = 5+(b[0]-v)/(b[0]-b[1])*5 if b[2] else 5+(v-b[0])/(b[1]-b[0])*5
                scores.append(min(10.0, max(0.0, float(s))))
            
            with cols[i%3]:
                fig = go.Figure()
                # 3등급 라인을 '평균'으로 표시
                fig.add_trace(go.Scatterpolar(r=[5]*6, theta=display_items+[display_items[0]], 
                                              line=dict(color='#BDC3C7', dash='dot'), name='평균(3등급)'))
                fig.add_trace(go.Scatterpolar(r=scores+[scores[0]], theta=display_items+[display_items[0]], 
                                              fill='toself', name=row["이름"], line=dict(color='#2980B9', width=3)))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균'])),
                                  showlegend=False, height=430, margin=dict(l=80, r=80, t=50, b=50),
                                  title=dict(text=f"👤 {row['이름']}", x=0.5, font=dict(size=17)))
                st.plotly_chart(fig, use_container_width=True)
                st.write("---")
    except Exception as e: st.error(f"⚠️ 오류: {e}")
