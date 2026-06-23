import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="PAPS 정밀 진단", layout="wide")
st.markdown("<h2 style='text-align: center;'>🏆 국가공인 PAPS 기준 정밀 진단 (1·2차 비교)</h2>", unsafe_allow_html=True)
st.write("---")

# 2. 사이드바 설정
st.sidebar.write("### 📝 학급 설정")
grade = st.sidebar.selectbox("학년 선택", ["4학년", "6학년"])

st.sidebar.divider()
st.sidebar.write("### 📥 업로드용 양식 다운로드")
st.sidebar.caption("아래 양식을 다운받아 학생들의 기록을 입력한 뒤 업로드해 줘!")

# 양식 다운로드용 데이터 생성
template_df = pd.DataFrame({
    "이름": ["홍길동", "유관순"], "성별": ["남", "여"], "실천의지": [5.0, 5.0],
    "심폐지구력": [429.0, 429.0] if grade == "6학년" else [45.0, 40.0],
    "순발력": [10.0, 10.7] if grade == "6학년" else [10.5, 11.0],
    "유연성": [1.0, 6.2] if grade == "6학년" else [1.0, 5.0],
    "악력": [19.0, 19.0] if grade == "6학년" else [15.0, 13.5]
})
csv_template = template_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(label="📄 CSV 입력 양식 다운로드", data=csv_template, file_name="PAPS_입력양식.csv", mime="text/csv")

st.sidebar.divider()
st.sidebar.write("### 📂 데이터 업로드")
up_file1 = st.sidebar.file_uploader("1차 기록(CSV) 업로드", type=["csv"])
up_file2 = st.sidebar.file_uploader("2차 기록(CSV) 업로드 (선택)", type=["csv"])

# 3. PAPS 통합 기준 데이터
PAPS_BASE = {
    "4학년": {
        "남": {"실천의지": [5.0, 10.0, 0], "심폐지구력": [45.0, 103.0, 0], "순발력": [10.5, 8.7, 1], "유연성": [1.0, 18.0, 0], "악력": [15.0, 36.0, 0]},
        "여": {"실천의지": [5.0, 10.0, 0], "심폐지구력": [40.0, 100.0, 0], "순발력": [11.0, 9.3, 1], "유연성": [5.0, 22.0, 0], "악력": [13.5, 33.6, 0]}
    },
    "6학년": {
        "남": {"실천의지": [5.0, 10.0, 0], "심폐지구력": [379.0, 243.0, 1], "순발력": [10.0, 7.77, 1], "유연성": [1.0, 18.0, 0], "악력": [19.0, 39.4, 0]},
        "여": {"실천의지": [5.0, 10.0, 0], "심폐지구력": [429.0, 243.0, 1], "순발력": [10.7, 8.66, 1], "유연성": [6.2, 26.0, 0], "악력": [19.0, 39.0, 0]}
    }
}

def load_csv(file):
    for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: continue
    return None

def get_val_robust(row, keywords, default):
    for col, val in row.items():
        c_clean = str(col).replace(" ", "")
        if any(kw in c_clean for kw in keywords):
            try: return float(val)
            except: pass
    return default

def calc_scores(row, g, gnd):
    v_cardio = get_val_robust(row, ["심폐", "오래달리기", "왕복"], 0.0)
    if g == "6학년":
        v_cardio = int(v_cardio)*60 + int(round((v_cardio-int(v_raw_cardio if 'v_raw_cardio' in locals() else v_cardio))*100))
        
    d_map = {
        "실천의지": get_val_robust(row, ["실천의지"], 5.0), "심폐지구력": v_cardio,
        "순발력": get_val_robust(row, ["순발력", "50m", "50미터"], 15.0),
        "유연성": get_val_robust(row, ["유연성", "앉아", "윗몸"], 0.0), "악력": get_val_robust(row, ["근력", "악력"], 0.0)
    }
    
    std_base = PAPS_BASE[g][gnd]
    sc = []
    for k in ["실천의지", "심폐지구력", "순발력", "유연성", "악력"]:
        val, (avg, mx, rev) = d_map[k], std_base[k]
        s = 5 + (avg - val) / (avg - mx) * 5 if rev else 5 + (val - avg) / (mx - avg) * 5
        sc.append(min(10.0, max(0.0, float(s))))
    return sc

# 4. 데이터 처리 및 시각화
if up_file1 or up_file2:
    df1, df2 = load_csv(up_file1), load_csv(up_file2)
    ncol1 = next((c for c in df1.columns if c.replace(" ", "") in ["이름", "성명", "학생명"]), None) if df1 is not None else None
    ncol2 = next((c for c in df2.columns if c.replace(" ", "") in ["이름", "성명", "학생명"]), None) if df2 is not None else None
    
    names = []
    if df1 is not None and ncol1: names.extend(df1[ncol1].dropna().astype(str).tolist())
    if df2 is not None and ncol2: names.extend(df2[ncol2].dropna().astype(str).tolist())
    unique_names = sorted(list(set(names)))
    
    if not unique_names:
        st.error("⚠️ 파일에서 학생의 '이름'이나 '성명' 컬럼을 찾을 수 없습니다.")
    else:
        st.success(f"✅ {grade} 학생 총 {len(unique_names)}명 분석 완료 (남녀 기준 자동 적용)")
        cols = st.columns(3)
        display_items = ["실천의지", "심폐지구력", "순발력", "유연성", "악력"]
        
        for i, name in enumerate(unique_names):
            gnd = "남"
            if df1 is not None and ncol1 and name in df1[ncol1].values and "성별" in df1.columns:
                gnd = str(df1[df1[ncol1] == name].iloc[0]["성별"]).strip()
            elif df2 is not None and ncol2 and name in df2[ncol2].values and "성별" in df2.columns:
                gnd = str(df2[df2[ncol2] == name].iloc[0]["성별"]).strip()
            if gnd not in ["남", "여"]: gnd = "남"
            
            with cols[i%3]:
                fig = go.Figure()
                fig.
