import pandas as pd
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="B tv 핫딜 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사이드바 패딩 제거 및 꽉 차는 레이아웃 CSS
st.markdown(
    """
    <style>
    /* 사이드바 기본 패딩 제거 */
    section[data-testid="stSidebar"] {
        background-color: #1a202c !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    /* 타이틀 영역 */
    .sidebar-header {
        padding: 24px 20px 20px 20px;
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        border-bottom: 2px solid #323d4d;
        letter-spacing: -0.5px;
    }

    /* 가로 100% 전체 영역 꽉 차는 버튼 커스텀 */
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    
    [data-testid="stSidebar"] .stButton {
        width: 100% !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        height: 65px !important;
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
        border: none !important;
        border-bottom: 2px solid #323d4d !important;
        border-radius: 0px !important;
        text-align: left !important;
        padding-left: 20px !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        margin: 0px !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }

    /* 마우스 호버 시 트렌디 딥 퍼플 포인트 반전 및 꽉 채우기 */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #6366f1 !important;
        color: #ffffff !important;
        border-bottom-color: #6366f1 !important;
        cursor: pointer;
    }

    /* 최하단 DATA SOURCE 영역 */
    .data-source-container {
        padding: 20px;
        background-color: #0f172a;
        border-top: 2px solid #323d4d;
        margin-top: auto !important;
    }
    .data-source-text {
        color: #8a99ad !important;
        font-size: 14px;
        line-height: 1.6;
    }
    .data-source-text a {
        color: #818cf8 !important;
        text-decoration: underline;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 구글 시트 URL
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6evDMSAeNeklEPyRNzfN9X9Gw02Ub8pzieBWmX_WFtL4h3gmBX_pjKt4Hekysgd7D1zSl4JBq14Cu/pub?output=csv"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1UqzVBDl3sTgKSZYty61BKqbvgrmTAIO0M4FaAulpwUo/edit?gid=686867409#gid=686867409"


# 2. 데이터 로드 및 정제
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df.columns = df.columns.astype(str).str.strip()

        column_mapping = {
            "총 판매금액": "총매출액",
            "총 판매건수": "판매건수",
            "상품명 (최종)": "상품명",
            "상품명(최종)": "상품명",
        }
        df = df.rename(columns=column_mapping)

        target_num_cols = ["총매출액", "판매건수", "할인가", "정가", "할인율"]
        for col in target_num_cols:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if "총매출액" in df.columns and "판매건수" in df.columns:
            df["객단가"] = (
                (df["총매출액"] / df["판매건수"])
                .replace([float("inf"), -float("inf")], 0)
                .fillna(0)
                .astype(int)
            )

        return df
    except Exception as e:
        st.error(f"구글 시트 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()


df = load_data()

# 세션 상태 초기화
if "menu" not in st.session_state:
    st.session_state.menu = "종합 실적"

# ==========================================
# 사이드바
# ==========================================

# 1. 상단 타이틀
st.sidebar.markdown(
    '<div class="sidebar-header">B tv 핫딜 대시보드</div>',
    unsafe_allow_html=True,
)

# 2. 가로 100% 채우는 메뉴 버튼
if st.sidebar.button("종합 실적", key="btn1"):
    st.session_state.menu = "종합 실적"

if st.sidebar.button("상품 검색 / 비교", key="btn2"):
    st.session_state.menu = "상품 검색 / 비교"

if st.sidebar.button("홈쇼핑사별 분석", key="btn3"):
    st.session_state.menu = "홈쇼핑사별 분석"

# 3. 최하단 고정 DATA SOURCE
st.sidebar.markdown(
    f"""
    <div class="data-source-container">
        <div class="data-source-text">
            <strong>DATA SOURCE</strong><br>
            🔗 <a href="{GOOGLE_SHEET_URL}" target="_blank">RAW 구글시트 바로가기</a><br><br>
            최종 집계일: 26.10.26(월)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_menu = st.session_state.menu


# ==========================================
# [메뉴 1] 종합 실적
# ==========================================
if selected_menu == "종합 실적":
    st.title("📊 종합 실적")
    st.caption("B tv 핫딜 전체 입점 상품의 주요 실적과 랭킹을 한눈에 확인합니다.")

    if df.empty:
        st.warning("데이터를 불러오지 못했습니다. 구글 시트를 확인해 주세요.")
    else:
        weeks = (
            ["전체 주차"] + list(df["주차"].dropna().unique())
            if "주차" in df.columns
            else ["전체 주차"]
        )
        selected_week = st.selectbox("📅 주차 선택", weeks)

        filtered_df = df.copy()
        if selected_week != "전체 주차" and "주차" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["주차"] == selected_week]

        col1, col2, col3, col4 = st.columns(4)
        total_sales = filtered_df["총매출액"].sum() if "총매출액" in filtered_df else 0
        total_count = filtered_df["판매건수"].sum() if "판매건수" in filtered_df else 0

        col1.metric("총 매출 합계", f"{int(total_sales):,} 원")
        col2.metric("총 판매 건수", f"{int(total_count):,} 건")
        col3.metric("입점 상품 종 수", f"{len(filtered_df):,} 종")

        avg_price = int(total_sales / total_count) if total_count > 0 else 0
        col4.metric("평균 객단가", f"{avg_price:,} 원")

        st.markdown("---")

        st.subheader("📈 주차별 매출 추이")
        if "주차" in df.columns and "총매출액" in df.columns:
            week_summary = df.groupby("주차", as_index=False)["총매출액"].sum()
            st.bar_chart(data=week_summary, x="주차", y="총매출액", use_container_width=True)

        st.subheader("🥇 Top 실적 상품")
        tab1, tab2 = st.tabs(["💰 매출액 Top 10", "📦 판매량 Top 10"])

        cols_to_show = [
            col
            for col in ["주차", "홈쇼핑사", "카테고리", "상품명", "할인가", "총매출액", "판매건수", "객단가"]
            if col in filtered_df.columns
        ]

        with tab1:
            if "총매출액" in filtered_df.columns:
                top_sales = filtered_df.sort_values(by="총매출액", ascending=False).head(10)
                st.dataframe(top_sales[cols_to_show], use_container_width=True)

        with tab2:
            if "판매건수" in filtered_df.columns:
                top_count = filtered_df.sort_values(by="판매건수", ascending=False).head(10)
                st.dataframe(top_count[cols_to_show], use_container_width=True)

        st.markdown("---")
        st.subheader("📋 전체 상품 목록")
        st.dataframe(filtered_df, use_container_width=True)


# ==========================================
# [메뉴 2] 상품 검색 / 비교
# ==========================================
elif selected_menu == "상품 검색 / 비교":
    st.title
