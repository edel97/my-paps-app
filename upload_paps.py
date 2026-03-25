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

# 3. 선생님이 주신 파일 기반 정밀 기준 (3등급=5점, 1등급=10점)
# [3등급 평균, 1등급 만점, 역산여부(1:시간/초)]
if grade == "4학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "심폐지구력": [21.0 if gender=="남" else 15.0, 40.0 if gender=="남" else 29.0, 0], 
        "순발력": [10.5 if gender=="남" else 11.2, 8.8 if gender=="남" else 9.3, 1],
        "유연성": [4.1 if gender=="남" else 7.1, 14.3 if gender=="남" else 17.3, 0],
        "근력": [15.2 if gender=="남" else 13.7, 21.6 if gender=="남" else 19.3, 0]
    }
elif grade == "5학년":
    base = {
        "실천의지": [5.0, 10.0, 0],
        "심폐지구력": [28.0 if gender=="남" else 19.0, 51.0 if gender=="남" else 36.0, 0], 
        "순발력": [9.8 if gender=="남" else 10.5, 8.3 if gender=="남" else 8.8, 1],
        "유연성": [5.6 if gender=="남" else 9.0, 16.5 if gender=="남" else 19.6, 0],
        "근력": [18.3 if gender=="남" else 16.3, 26.2 if gender=="남" else 23.3, 0]
    }
else: # 6학년
    base = {
        "실천의지": [5.0, 10.0, 0],
        "심폐지구력": [486.0 if gender=="남" else 560.0, 370.0 if gender=="남" else 440.0, 1], # 시간(초) 기준
        "순발력": [9.2 if gender=="남" else 10.0, 7.8 if gender=="남" else 8.3, 1],
        "유연성": [7.3 if gender=="남" else 11.0, 18.9 if gender=="남" else 22.3, 0],
        "근력": [21.9 if gender=="남" else 19.5, 31.7 if gender=="남" else 28.1, 0]
    }

items = ["실천의지", "심폐지구력", "순발력", "유연성", "근력"]
display_items = ["실천의지", "심폐지구력\n(오래달리기)", "순발력\n(50m달리기)", "유연성\n(앉아윗몸굽히기)", "근력\n(악력)"]

# 4. 데이터 처리 및 그래프
if up_file:
    try:
        try: df = pd.read_csv(up_file, encoding='utf-8-sig')
        except: up_file.seek(0); df = pd.read_csv(up_file, encoding='cp949')
        df.columns = [c.strip() for c in df.columns]
        
        st.success(f"✅ {grade} {gender}학생 국가공인 기준 적용 완료")
        cols = st.columns(3)
        
        for i, row in df.iterrows():
            v_raw = float(row.get("심폐지구력", 0))
            if grade == "6학년": # 6학년 분.초 변환 (예: 6.10 -> 370초)
                cardio = int(v_raw)*60 + int(round((v_raw-int(v_raw))*100))
            else: cardio = v_raw
            
            d_map = {"실천의지":float(row.get("실천의지",5)), "심폐지구력":cardio, "순발력":float(row.get("순발력",15)),
                     "유연성":float(row.get("유연성",0)), "근력":float(row.get("근력",0))}
            
            scores = []
            for k, b in base.items():
                v = d_map[k]
                # 3등급(b[0])이 5점, 1등급(b[1])이 10점이 되는 선형 변환 로직
                s = 5+(b[0]-v)/(b[0]-b[1])*5 if b[2] else 5+(v-b[0])/(b[1]-b[0])*5
                scores.append(min(10.0, max(0.0, float(s))))
            
            with cols[i%3]:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[5]*6, theta=display_items+[display_items[0]], 
                                              line=dict(color='#BDC3C7', dash='dot', width=1), name='3등급(기준)'))
                fig.add_trace(go.Scatterpolar(r=scores+[scores[0]], theta=display_items+[display_items[0]], 
                                              fill='toself', name=row["이름"], line=dict(color='#2980B9', width=3)))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['3등급'])),
                                  showlegend=False, height=430, margin=dict(l=80, r=80, t=50, b=50),
                                  title=dict(text=f"👤 {row['이름']} ({grade})", x=0.5, font=dict(size=17)))
                st.plotly_chart(fig, use_container_width=True)
                st.write("---")
    except Exception as e: st.error(f"⚠️ 파일 해석 중 오류: {e}")
