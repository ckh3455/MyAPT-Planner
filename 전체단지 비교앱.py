import streamlit as st
import pandas as pd
import datetime
import math

# 파일 로드
@st.cache_data
def load_data():
    df = pd.read_excel("앱만들기 단지데이터 250606(압구정포함).xlsx")
    df = df.set_index("단지_평형")
    return df

# CAGR 계산
def calculate_dynamic_cagr(row):
    years = [col for col in row.index if isinstance(col, int)]
    valid = row[years].dropna()
    if len(valid) < 2:
        return None
    start_year = valid.index[0]
    periods = 2025 - start_year
    start_price = valid[start_year]
    end_price = valid[2025] if 2025 in valid else None
    if pd.isna(start_price) or start_price <= 0 or pd.isna(end_price):
        return None
    return (end_price / start_price) ** (1 / periods) - 1

# 미래가격 예측
def predict_price(current_price, cagr, years_passed):
    if pd.isna(current_price) or pd.isna(cagr):
        return None
    return round(current_price * ((1 + cagr) ** years_passed) / 10000, 1)  # 억 단위

# 목표가 도달 시점 계산
def calculate_target_date(current_price, target_price, cagr):
    if pd.isna(current_price) or pd.isna(target_price) or pd.isna(cagr) or cagr <= 0:
        return None
    return math.log(target_price / current_price) / math.log(1 + cagr)

# Streamlit 앱 구성
st.set_page_config(page_title="단지 가격 비교기", layout="wide")
st.title("단지별 미래 시점 가격 비교기")

# 앱 사용 안내 및 홍보 정보
with st.expander("ℹ️ 사용 안내 및 개발자 정보", expanded=True):
    st.markdown("""
    **📘 사용법**
    - '내집'과 '갈집'에서 원하는 아파트 단지_평형을 선택하고, 신고가와 목표가를 입력하세요.
    - '결과 확인' 버튼을 누르면 1, 2, 3, 5, 10년 후 예상 가격과 목표가 도달 시점을 확인할 수 있습니다.
    - 두 단지 간의 향후 가격 차이도 함께 확인할 수 있습니다.
    - 데이터값은 해당 연도 최대값을 사용하였으며 상승률은 연복리 상승률 기준임.
    - 세금 계산은 새무사와 상의하세요.
    - 부담할 세금 보다 미래 가액 차이가 크면 갈아타세요.
    - 해당 단지 선정은 24년 거래건수 100건 이상의 단지만 선정하였습니다(단지이름이 중복일 경우 제외되었음).


    **👨‍💼 개발자 및 중개업소 정보**
    **압구정 최고의 부동산 전문가!**  
    - **업소명**: 압구정 원 부동산중개  
    - **대표자**: 최규호 이사  
    - **문의전화**: [📞 010-3065-1780]
    - **상담 **: 예약 필수
    """)

# 데이터 로드 및 전처리
df = load_data()
df["CAGR"] = df.apply(calculate_dynamic_cagr, axis=1)
단지_목록 = [""] + df.index.tolist()

if "제출1" not in st.session_state:
    st.session_state["제출1"] = False
if "제출2" not in st.session_state:
    st.session_state["제출2"] = False

col1, col2 = st.columns(2)

with col1:
    st.subheader("내집")
    with st.form("내집_form"):
        단지1 = st.selectbox("단지_평형 선택", 단지_목록, index=0, key="단지1")
        신고가1 = st.number_input("신고가 (억)", min_value=0.0, step=0.1, key="신고가1")
        목표가1 = st.number_input("목표가 (억)", min_value=0.0, step=0.1, key="목표가1")
        제출1 = st.form_submit_button("📊 내집 결과 확인")
        if 제출1:
            st.session_state["제출1"] = True

with col2:
    st.subheader("갈집")
    with st.form("갈집_form"):
        단지2 = st.selectbox("단지_평형 선택", 단지_목록, index=0, key="단지2")
        신고가2 = st.number_input("신고가 (억)", min_value=0.0, step=0.1, key="신고가2")
        목표가2 = st.number_input("목표가 (억)", min_value=0.0, step=0.1, key="목표가2")
        제출2 = st.form_submit_button("📈 갈집 결과 확인")
        if 제출2:
            st.session_state["제출2"] = True

# 내집 결과 표시
if st.session_state.get("제출1") and st.session_state.get("단지1"):
    단지1 = st.session_state["단지1"]
    신고가1 = st.session_state["신고가1"]
    목표가1 = st.session_state["목표가1"]
    row1 = df.loc[단지1]
    기준연도1 = row1.dropna().index[0]
    cagr1 = row1["CAGR"]
    current_price1 = 신고가1 * 10000
    st.markdown("### 내집 결과")
    st.markdown(f"- 기준 연도: {기준연도1} ~ 2025 ({2025 - 기준연도1}년)")
    st.markdown(f"- 신고가 기준: {신고가1}억")

    st.markdown("#### 예상 가격")
    for y in [1, 2, 3, 5, 10]:
        pred = predict_price(current_price1, cagr1, y)
        st.write(f"{y}년 후: {pred}억")

    도달년수 = calculate_target_date(current_price1, 목표가1 * 10000, cagr1)
    if 도달년수:
        도달시점 = datetime.datetime(2025, 1, 1) + datetime.timedelta(days=도달년수 * 365)
        st.success(f"목표가에 도달 예상 시점: {도달시점.strftime('%Y년 %m월 %d일')} (약 {int(도달년수)}년 후)")

# 갈집 결과 표시
if st.session_state.get("제출2") and st.session_state.get("단지2"):
    단지2 = st.session_state["단지2"]
    신고가2 = st.session_state["신고가2"]
    목표가2 = st.session_state["목표가2"]
    row2 = df.loc[단지2]
    기준연도2 = row2.dropna().index[0]
    cagr2 = row2["CAGR"]
    current_price2 = 신고가2 * 10000
    st.markdown("### 갈집 결과")
    st.markdown(f"- 기준 연도: {기준연도2} ~ 2025 ({2025 - 기준연도2}년)")
    st.markdown(f"- 신고가 기준: {신고가2}억")

    st.markdown("#### 예상 가격")
    for y in [1, 2, 3, 5, 10]:
        pred = predict_price(current_price2, cagr2, y)
        st.write(f"{y}년 후: {pred}억")

    도달년수2 = calculate_target_date(current_price2, 목표가2 * 10000, cagr2)
    if 도달년수2:
        도달시점2 = datetime.datetime(2025, 1, 1) + datetime.timedelta(days=도달년수2 * 365)
        st.success(f"목표가에 도달 예상 시점: {도달시점2.strftime('%Y년 %m월 %d일')} (약 {int(도달년수2)}년 후)")

# 두 단지 비교
if st.session_state.get("제출1") and st.session_state.get("제출2"):
    row1 = df.loc[st.session_state["단지1"]]
    row2 = df.loc[st.session_state["단지2"]]
    cagr1 = row1["CAGR"]
    cagr2 = row2["CAGR"]
    price1 = st.session_state["신고가1"] * 10000
    price2 = st.session_state["신고가2"] * 10000

    st.markdown("## 내집 vs 갈집 예상 가격 차이")
    st.markdown(f"2025 신고가 기준 차이 (갈집 - 내집): {round((price2 - price1) / 10000, 1)}억")

    st.markdown("#### 향후 가격 차이")
    for y in [1, 2, 3, 5, 10]:
        p1 = predict_price(price1, cagr1, y)
        p2 = predict_price(price2, cagr2, y)
        if p1 is not None and p2 is not None:
            st.write(f"{y}년 후 가격 차이 (갈집 - 내집): {round(p2 - p1, 1)}억")

    # 각 단지별 2025년까지 최고가 출력
    max1 = row1[[col for col in row1.index if isinstance(col, int)]].dropna().max()
    max2 = row2[[col for col in row2.index if isinstance(col, int)]].dropna().max()
    start1 = row1.dropna().index[0]
    start2 = row2.dropna().index[0]
    st.markdown("### 연도별 최고가 요약")
    st.markdown(f"- 내집 기준연도: {start1}~2025 / 최고가: {round(max1 / 10000, 1)}억")
    st.markdown(f"- 갈집 기준연도: {start2}~2025 / 최고가: {round(max2 / 10000, 1)}억")
