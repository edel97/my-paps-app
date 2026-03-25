import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="PAPS 일괄 생성", layout="wide")
st.markdown("### 📊 우리 반 PAPS 그래프 일괄 생성")

# 사이드바 설정
up_file = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])
grade = st.sidebar.selectbox("학년", ["4학년", "6학년"])
gender = st.sidebar.radio("성별", ["남", "여"])

# 기준치 설정
if grade == "4학년":
    items = ["실천의지", "심폐지구력\n(왕복오래달리기)", "순발력\n(50m 달리기)", "유연성\n(앉아윗몸굽히기)", "근력\n(악력)"]
    base = {"실천의지":[5,10,0], "심폐지구력":[35 if gender=="남" else 30, 80 if gender=="남" else 70, 0], 
            "순발력":[10.5 if gender=="남" else 11.2, 8 if gender=="남" else 8.5, 1],
            "유연성":[5 if gender=="남" else 8, 18 if gender=="남" else 21, 0],
            "근력":[14 if gender=="남" else 13, 24 if gender=="남" else 22, 0]}
else:
    items = ["실천의지", "심폐지구력\n(오래달리기-걷기)", "순발력\n(50m 달리기)", "유연성\n(앉아윗몸굽히기)", "근력\n(악력)"]
    base = {"실천의지":[5,10,0], "심폐지구력":[400 if gender=="남" else 500, 240 if gender=="남" else 300, 1],
            "순발력":[9.5 if gender=="남" else 10.2, 7.5 if gender=="남" else 8, 1],
            "유연성":[8 if gender=="남" else 11, 20 if gender=="남" else 23, 0],
            "근력":[22 if gender=="남" else 20, 35 if gender=="남" else 32, 0]}

if up_file:
    try:
        try: df = pd.read_csv(up_file, encoding='utf-8-sig')
        except: up_file.seek(0); df = pd.read_csv(up_file, encoding='cp949')
        df.columns = [c.strip() for c in df.columns]
        
        cols = st.columns(3)
        for i, row in df.iterrows():
            # 데이터 처리
            v_raw = float(row.get("심폐지구력", 0))
            if grade == "6학년":
                cardio = int(v_raw)*60 + int(round((v_raw-int(v_raw))*100))
            else: cardio = v_raw
            
            d_map = {"실천의지":float(row.get("실천의지",5)), "심폐지구력":cardio, "순발력":float(row.get("순발력",15)),
                     "유연성":float(row.get("유연성",0)), "근력":float(row.get("근력",0))}
            
            scores = []
            for k, b in base.items():
                v = d_map[k]
                s = 5+(b[0]-v)/(b[0]-b[1])*5 if b[2] else 5+(v-b[0])/(b[1]-b[0])*5
                scores.append(min(10.0, max(0.0, float(s))))
            
            # 그래프 출력
            with cols[i%3]:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[5]*6, theta=items+[items[0]], line=dict(color='gray', dash='dot'), name='평균'))
                fig.add_trace(go.Scatterpolar(r=scores+[scores[0]], theta=items+[items[0]], fill='toself', name=row["이름"]))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,10])), showlegend=False, 
                                  height=400, title=dict(text=f"👤 {row['이름']}", x=0.5))
                st.plotly_chart(fig, use_container_width=True)
                st.write("---")
    except Exception as e: st.error(f"오류: {e}")
