import pandas as pd
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="B tv 핫딜 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# [클래식 차콜 & 에머랄드 어드민 테마]
st.markdown(
    """
    <style>
    /* 사이드바 배경 및 기본 색상 */
    section[data-testid="stSidebar"] {
        background-color: #1E2430 !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }

    /* 상단 대시보드 타이틀 */
    .sidebar-title {
        padding: 24px 20px;
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        border-bottom: 2px solid #272E3D;
        letter-spacing: -0.5px;
    }

    /* 템플릿 방식: 꽉 차는 네비게이션 블록 버튼 */
    div[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        height: 64px !important;
        background-color: #1E2430 !important;
        color: #E2E8F0 !important;
        border: none !important;
        border-bottom: 2px solid #272E3D !important;
        border-radius: 0px !important;
        text-align: left !important;
        padding-left: 24px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* 마우스 호버 시 에머랄드 반전 포인트 */
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #10B981 !important;
        color: #ffffff !important;
        border-bottom-color: #059669 !important;
        cursor: pointer;
    }

    /* 최하단 영구 고정 DATA SOURCE 영역 */
    .data-source-container {
        padding: 20px;
        background-color: #171C26;
        border-top: 2px solid #272E3D;
        margin-top: auto !important; /* 맨 밑으로 고정 */
    }
    .data-source-text {
        color: #8A99AD !important;
        font-size: 14px;
        line-height: 1.6;
    }
    .data-source-text a {
        color: #10B981 !important;
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

# 세션 상태 초기화 (메뉴 상태 유지)
if "menu" not in st.session_state:
    st.session_state.menu = "종합 실적"

# ==========================================
# 사이드바 (템플릿 모듈형 네비게이션)
# ==========================================

# 1. 상단 타이틀
st.sidebar.markdown(
    '<div class="sidebar-title">B tv 핫딜 대시보드</div>',
    unsafe_allow_html=True,
)

# 2. 가로 전체 클릭 메뉴 블록
if st.sidebar.button("종합 실적", use_container_width=True):
    st.session_state.menu = "종합 실적"

if st.sidebar.button("상품 검색 / 비교", use_container_width=True):
    st.session_state.menu = "상품 검색 / 비교"

if st.sidebar.button("홈쇼핑사별 분석", use_container_width=True):
    st.session_state.menu = "홈쇼핑사별 분석"

# 3. 최하단 영구 고정 DATA SOURCE
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
    st.title("🔍 상품 검색 / 비교")
    st.caption("키워드, 가격대, 할인율, 카테고리 등 조건별로 상품을 밀착 검색하고 비교합니다.")

    if df.empty:
        st.warning("데이터를 불러오지 못했습니다.")
    else:
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            search_kw = st.text_input("🔎 상품명 키워드 검색", "", placeholder="예: 갈비, 코트, 에어프라이어")
            cats = (
                ["전체"] + list(df["카테고리"].dropna().unique())
                if "카테고리" in df.columns
                else ["전체"]
            )
            selected_cat = st.selectbox("📂 카테고리 선택", cats)

        with col_filter2:
            chans = (
                ["전체"] + list(df["홈쇼핑사"].dropna().unique())
                if "홈쇼핑사" in df.columns
                else ["전체"]
            )
            selected_chan = st.selectbox("📺 홈쇼핑사 선택", chans)
            min_discount = st.slider("🏷️ 최소 할인율 (%)", 0, 50, 0, step=5)

        with col_filter3:
            max_price_limit = (
                int(df["할인가"].max())
                if ("할인가" in df.columns and df["할인가"].max() > 0)
                else 1000000
            )
            price_range = st.slider("💵 할인가 범위 (원)", 0, max_price_limit, (0, max_price_limit), step=5000)

        search_df = df.copy()
        if search_kw and "상품명" in search_df.columns:
            search_df = search_df[search_df["상품명"].str.contains(search_kw, case=False, na=False)]
        if selected_cat != "전체" and "카테고리" in search_df.columns:
            search_df = search_df[search_df["카테고리"] == selected_cat]
        if selected_chan != "전체" and "홈쇼핑사" in search_df.columns:
            search_df = search_df[search_df["홈쇼핑사"] == selected_chan]
        if "할인율" in search_df.columns:
            search_df = search_df[search_df["할인율"] >= min_discount]
        if "할인가" in search_df.columns:
            search_df = search_df[
                (search_df["할인가"] >= price_range[0]) & (search_df["할인가"] <= price_range[1])
            ]

        st.markdown("---")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("검색된 상품 수", f"{len(search_df):,} 건")

        s_sales = search_df["총매출액"].sum() if "총매출액" in search_df else 0
        res_col2.metric("검색 상품 총 매출액", f"{int(s_sales):,} 원")

        avg_p = int(search_df["할인가"].mean()) if len(search_df) > 0 else 0
        res_col3.metric("검색 상품 평균 할인가", f"{avg_p:,} 원")

        st.dataframe(search_df, use_container_width=True)


# ==========================================
# [메뉴 3] 홈쇼핑사별 분석
# ==========================================
elif selected_menu == "홈쇼핑사별 분석":
    st.title("🏢 홈쇼핑사별 분석")
    st.caption("제휴 홈쇼핑사별 입점 성과, 히스토리 및 효자 상품을 분석합니다.")

    if df.empty or "홈쇼핑사" not in df.columns:
        st.warning("홈쇼핑사 데이터가 없습니다.")
    else:
        partners = list(df["홈쇼핑사"].dropna().unique())
        selected_partner = st.selectbox("🏢 분석할 홈쇼핑사를 선택하세요", partners)

        partner_df = df[df["홈쇼핑사"] == selected_partner]

        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("누적 진행 상품 수", f"{len(partner_df):,} 건")

        p_sales = partner_df["총매출액"].sum() if "총매출액" in partner_df else 0
        col_p2.metric("누적 총 매출액", f"{int(p_sales):,} 원")

        top_cat = (
            partner_df["카테고리"].mode()[0]
            if ("카테고리" in partner_df and not partner_df.empty)
            else "-"
        )
        col_p3.metric("주력 카테고리", top_cat)

        st.markdown("---")

        left_p, right_p = st.columns([1, 1])

        with left_p:
            st.subheader(f"🏆 {selected_partner} 역대 효자 상품 Top 5")
            if "총매출액" in partner_df.columns:
                partner_top5 = partner_df.sort_values(by="총매출액", ascending=False).head(5)
                st.dataframe(partner_top5, use_container_width=True)

        with right_p:
            st.subheader(f"📊 {selected_partner} 주차별 매출 흐름")
            if "주차" in partner_df.columns and "총매출액" in partner_df.columns:
                partner_trend = partner_df.groupby("주차", as_index=False)["총매출액"].sum()
                st.line_chart(data=partner_trend, x="주차", y="총매출액", use_container_width=True)

        st.markdown("---")
        st.subheader(f"📋 {selected_partner} 전체 딜 진행 히스토리")
        st.dataframe(partner_df, use_container_width=True)
