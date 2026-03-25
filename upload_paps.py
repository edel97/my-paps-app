import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io

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

# 3. 데이터 기준 설정 (4/6학년 통합)
if grade == "4학년":
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 35.0 if gender == "남" else 30.0, "max": 80.0 if gender == "남" else 70.0, "rev": False},
        "순발력": {"avg": 10.5 if gender == "남" else 11.2, "max": 8.0 if gender == "남" else 8.5, "rev": True},
        "유연성": {"avg": 5.0 if gender == "남" else 8.0, "max": 18.0 if gender == "남" else 21.0, "rev": False},
        "근력": {"avg": 14.0 if gender == "남" else 13.0, "max": 24.0 if gender == "남" else 22.0, "rev": False}
    }
else: # 6학년
    base = {
        "실천의지": {"avg": 5.0, "max": 10.0, "rev": False},
        "심폐지구력": {"avg": 400.0 if gender == "남" else 500.0, "max": 240.0 if gender == "남" else 300.0, "rev": True},
        "순발력": {"avg": 9.5 if gender == "남" else 10.2, "max": 7.5 if gender == "남" else 8.0, "rev": True},
        "유연성": {"avg": 8.0 if gender == "남" else 11.0, "max": 20.0 if gender == "남" else 23.0, "rev": False},
        "근력": {"avg": 22.0 if gender == "남" else 20.0, "max": 35.0 if gender == "남" else 32.0, "rev": False}
    }

lbls = list(base.keys())
p_lbls = lbls + [lbls[0]]

# 4. 점수 계산 함수
def calc_score(row):
    scores = []
    try:
        raw_v = float(row.get("심폐지구력", 0))
        if grade == "6학년":
            m = int(raw_v)
            s = int(round((raw_v - m) * 100))
            cardio_val = float(m * 60 + s)
        else:
            cardio_val = raw_v
    except:
        cardio_val = 0.0

    data_map = {
        "실천의지": float(row.get("실천의지", 5.0)),
        "심폐지구력": cardio_val,
        "순발력": float(row.get("순발력", 15.0)),
        "유연성": float(row.get("유연성", 0.0)),
        "근력": float(row.get("근력", 0.0))
    }
    
    for k, v in base.items():
        val = data_map.get(k, 0.0)
        avg, mx = v['avg'], v['max']
        score = 5 + (avg - val) / (avg - mx) * 5 if v['rev'] else 5 + (val - avg) / (mx - avg) * 5
        scores.append(min(10.0, max(0.0, float(score))))
    return scores + [scores[0]]

# 5. 메인 로직 (한글 깨짐 방지 강화)
if uploaded_file is not None:
    try:
        # 1차 시도: utf-8-sig (엑셀 UTF-8 방식)
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            # 2차 시도: cp949 (일반 한국어 엑셀 방식)
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='cp949')
        
        # 컬럼명 앞뒤 공백 제거
        df.columns = [c.strip() for c in df.columns]
        
        if not df.empty:
            st.success(f"✅ {grade} {gender}학생 {len(df)}명의 데이터를 분석했습니다!")
            st.write("---")
            
            cols = st.columns(3)
            for i, row in df.iterrows():
                with cols[i % 3]:
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(r=[5]*6, theta=p_lbls, line=dict(color='gray', dash='dot', width=1), name='평균'))
                    fig.add_trace(go.Scatterpolar(r=calc_score(row), theta=p_lbls, fill='toself', name=row["이름"], line=dict(color='#3498DB', width=3)))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickvals=[5], ticktext=['평균']),
                                   angularaxis=dict(tickfont=dict(size=11), rotation=90, direction="clockwise")),
                        showlegend=False, height=400, margin=dict(l=70, r=70, t=60, b=40),
                        title=dict(text=f"👤 {row['이름']} ({grade})", x=0.5, y=0.95, xanchor='center', font=dict(size=16)),
                        dragmode=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.write("---")
        else:
            st.warning("⚠️ 파일 안에 데이터가 없습니다.")

    except Exception as e:
        st.error(f"⚠️ 파일을 읽는 중 오류가 발생했습니다. CSV 형식을 확인해주세요! (에러: {e})")
else:
    st.info("👈 사이드바에서 아까 만드신 엑셀(CSV) 파일을 다시 한번 올려주세요!")
