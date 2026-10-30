import pandas as pd
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(page_title="B tv 핫딜 대시보드", layout="wide")

# 샘플 데이터 로드 (추후 구글 시트 IMPORTRANGE/API 연동 가능)
@st.cache_data
def load_data():
    data = [
        {
            "주차": "42주차",
            "홈쇼핑사": "CJ온스타일",
            "카테고리": "주방가전",
            "상품명": "[B tv 단독] 에어프라이어 듀얼바스켓 10L",
            "정가": 159000,
            "할인가": 129000,
            "할인율": 18,
            "총매출액": 45800000,
            "판매건수": 355,
            "입점일": "2025-01-10",
        },
        {
            "주차": "42주차",
            "홈쇼핑사": "GS샵",
            "카테고리": "식품",
            "상품명": "LA양념갈비 800g x 5팩 세트",
            "정가": 89000,
            "할인가": 79000,
            "할인율": 11,
            "총매출액": 62400000,
            "판매건수": 789,
            "입점일": "2024-11-15",
        },
        {
            "주차": "41주차",
            "홈쇼핑사": "현대홈쇼핑",
            "카테고리": "패션/의류",
            "상품명": "24FW 프리미엄 울 100% 핸드메이드 코트",
            "정가": 299000,
            "할인가": 239000,
            "할인율": 20,
            "총매출액": 88300000,
            "판매건수": 369,
            "입점일": "2025-02-01",
        },
        {
            "주차": "41주차",
            "홈쇼핑사": "롯데홈쇼핑",
            "카테고리": "생활/건강",
            "상품명": "호텔식 고밀도 순면 침구세트 Q",
            "정가": 119000,
            "할인가": 89000,
            "할인율": 25,
            "총매출액": 31100000,
            "판매건수": 349,
            "입점일": "2024-09-01",
        },
        {
            "주차": "40주차",
            "홈쇼핑사": "NS홈쇼핑",
            "카테고리": "식품",
            "상품명": "국내산 나주배 5kg 선물세트",
            "정가": 59000,
            "할인가": 49000,
            "할인율": 17,
            "총매출액": 28500000,
            "판매건수": 581,
            "입점일": "2024-12-20",
        },
        {
            "주차": "40주차",
            "홈쇼핑사": "GS샵",
            "카테고리": "식품",
            "상품명": "수제 돼지양념구이 1kg x 3팩",
            "정가": 49000,
            "할인가": 39000,
            "할인율": 20,
            "총매출액": 41200000,
            "판매건수": 1056,
            "입점일": "2024-11-15",
        },
    ]
    df = pd.DataFrame(data)
    df["객단가"] = (df["총매출액"] / df["판매건수"]).fillna(0).astype(int)
    return df

df = load_data()

# 구글 시트 원본 주소 적용
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1UqzVBDl3sTgKSZYty61BKqbvgrmTAIO0M4FaAulpwUo/edit?gid=686867409#gid=686867409"

# ==========================================
# 사이드바 (메뉴 및 RAW 데이터 관리)
# ==========================================
st.sidebar.title("📺 B tv 핫딜 대시보드")
st.sidebar.markdown("---")

# 1. 메인 메뉴 선택
selected_menu = st.sidebar.radio(
    "📌 메뉴 선택",
    ["🏆 역대 랭킹 & 실적 종합", "🔍 통합 상품 검색", "🏢 홈쇼핑사별 분석"]
)

st.sidebar.markdown("---")

# 2. 하단 RAW 데이터 관리 영역
st.sidebar.subheader("📂 RAW 데이터 관리")
st.sidebar.markdown(f"🔗 **[RAW 구글시트 바로가기]({GOOGLE_SHEET_URL})**")
st.sidebar.caption("📅 현재 **26.10.30 (42주차)** 실적까지 포함")


# ==========================================
# [메뉴 1] 역대 랭킹 & 실적 종합
# ==========================================
if selected_menu == "🏆 역대 랭킹 & 실적 종합":
    st.title("🏆 역대 랭킹 & 실적 종합")
    st.caption("B tv 핫딜 전체 입점 상품의 주요 실적과 랭킹을 한눈에 확인합니다.")
    
    # 주차 필터
    weeks = ["전체 주차"] + sorted(list(df["주차"].unique()), reverse=True)
    selected_week = st.selectbox("📅 주차 선택", weeks)
    
    filtered_df = df.copy()
    if selected_week != "전체 주차":
        filtered_df = filtered_df[filtered_df["주차"] == selected_week]
        
    # KPI 카드
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 매출 합계", f"{filtered_df['총매출액'].sum():,} 원")
    col2.metric("총 판매 건수", f"{filtered_df['판매건수'].sum():,} 건")
    col3.metric("입점 상품 종 수", f"{len(filtered_df)} 종")
    avg_price = int(filtered_df['총매출액'].sum() / filtered_df['판매건수'].sum()) if filtered_df['판매건수'].sum() > 0 else 0
    col4.metric("평균 객단가", f"{avg_price:,} 원")
    
    st.markdown("---")
    
    # 주차별 매출 추이 차트
    st.subheader("📈 주차별 매출 추이")
    week_summary = df.groupby("주차")["총매출액"].sum().reset_index()
    st.bar_chart(data=week_summary, x="주차", y="총매출액", use_container_width=True)
    
    # Top 10 탭
    st.subheader("🥇 Top 실적 상품")
    tab1, tab2 = st.tabs(["💰 매출액 Top 10", "📦 판매량 Top 10"])
    
    with tab1:
        top_sales = filtered_df.sort_values(by="총매출액", ascending=False).head(10)
        st.dataframe(top_sales[["주차", "홈쇼핑사", "카테고리", "상품명", "할인가", "총매출액", "판매건수"]], use_container_width=True)
        
    with tab2:
        top_count = filtered_df.sort_values(by="판매건수", ascending=False).head(10)
        st.dataframe(top_count[["주차", "홈쇼핑사", "카테고리", "상품명", "할인가", "판매건수", "총매출액"]], use_container_width=True)

    st.markdown("---")
    st.subheader("📋 전체 상품 목록 (최신순)")
    sorted_all = filtered_df.sort_values(by="주차", ascending=False)
    st.dataframe(sorted_all, use_container_width=True)


# ==========================================
# [메뉴 2] 통합 상품 검색
# ==========================================
elif selected_menu == "🔍 통합 상품 검색":
    st.title("🔍 통합 상품 상세 검색 & 필터")
    st.caption("키워드, 가격대, 할인율, 카테고리 등 조건별로 상품을 밀착 검색합니다.")
    
    # 검색 조건 레이아웃
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        search_kw = st.text_input("🔎 상품명 키워드 검색", "", placeholder="예: 갈비, 코트, 에어프라이어")
        categories = ["전체"] + list(df["카테고리"].unique())
        selected_cat = st.selectbox("📂 카테고리 선택", categories)
        
    with col_filter2:
        channels = ["전체"] + list(df["홈쇼핑사"].unique())
        selected_chan = st.selectbox("📺 홈쇼핑사 선택", channels)
        min_discount = st.slider("🏷️ 최소 할인율 (%)", 0, 50, 0, step=5)
        
    with col_filter3:
        max_price_limit = int(df["할인가"].max())
        price_range = st.slider("💵 할인가 범위 (원)", 0, max_price_limit, (0, max_price_limit), step=5000)

    # 필터 적용
    search_df = df.copy()
    if search_kw:
        search_df = search_df[search_df["상품명"].str.contains(search_kw, case=False)]
    if selected_cat != "전체":
        search_df = search_df[search_df["카테고리"] == selected_cat]
    if selected_chan != "전체":
        search_df = search_df[search_df["홈쇼핑사"] == selected_chan]
    search_df = search_df[search_df["할인율"] >= min_discount]
    search_df = search_df[(search_df["할인가"] >= price_range[0]) & (search_df["할인가"] <= price_range[1])]

    # 요약 정보
    st.markdown("---")
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("검색된 상품 수", f"{len(search_df)} 건")
    res_col2.metric("검색 상품 총 매출액", f"{search_df['총매출액'].sum():,} 원")
    avg_price_search = int(search_df['할인가'].mean()) if len(search_df) > 0 else 0
    res_col3.metric("검색 상품 평균 할인가", f"{avg_price_search:,} 원")
    
    # 검색 결과 표
    st.dataframe(
        search_df[["주차", "홈쇼핑사", "카테고리", "상품명", "정가", "할인가", "할인율", "총매출액", "판매건수"]],
        use_container_width=True
    )


# ==========================================
# [메뉴 3] 홈쇼핑사별 분석
# ==========================================
elif selected_menu == "🏢 홈쇼핑사별 분석":
    st.title("🏢 홈쇼핑사별 파트너십 분석")
    st.caption("제휴 홈쇼핑사별 입점 성과, 히스토리 및 효자 상품을 분석합니다.")
    
    selected_partner = st.selectbox("🏢 분석할 홈쇼핑사를 선택하세요", list(df["홈쇼핑사"].unique()))
    
    partner_df = df[df["홈쇼핑사"] == selected_partner]
    
    # 홈쇼핑사 프로필 지표
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    first_date = partner_df["입점일"].min() if not partner_df.empty else "-"
    col_p1.metric("최초 입점일", first_date)
    col_p2.metric("누적 진행 상품 수", f"{len(partner_df)} 건")
    col_p3.metric("누적 총 매출액", f"{partner_df['총매출액'].sum():,} 원")
    top_cat = partner_df["카테고리"].mode()[0] if not partner_df.empty else "-"
    col_p4.metric("주력 카테고리", top_cat)
    
    st.markdown("---")
    
    # 홈쇼핑사 효자 상품 Top 5 & 히스토리
    left_p, right_p = st.columns([1, 1])
    
    with left_p:
        st.subheader(f"🏆 {selected_partner} 역대 효자 상품 Top 5")
        partner_top5 = partner_df.sort_values(by="총매출액", ascending=False).head(5)
        st.dataframe(partner_top5[["주차", "상품명", "할인가", "총매출액", "판매건수"]], use_container_width=True)
        
    with right_p:
        st.subheader(f"📊 {selected_partner} 주차별 매출 흐름")
        partner_trend = partner_df.groupby("주차")["총매출액"].sum().reset_index()
        st.line_chart(data=partner_trend, x="주차", y="총매출액", use_container_width=True)

    st.markdown("---")
    st.subheader(f"📋 {selected_partner} 전체 딜 진행 히스토리")
    st.dataframe(partner_df.sort_values(by="주차", ascending=False), use_container_width=True)
