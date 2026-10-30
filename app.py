import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="B tv 핫딜 대시보드", layout="wide")

st.title("📺 B tv 핫딜 대시보드")
st.caption("구글 시트 연동 통합 데이터 분석기 (Python / Streamlit)")


# 데이터 로드
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
            "할인율": "18%",
            "총매출액": 45800000,
            "판매건수": 355,
        },
        {
            "주차": "42주차",
            "홈쇼핑사": "GS샵",
            "카테고리": "식품",
            "상품명": "LA양념갈비 800g x 5팩 세트",
            "정가": 89000,
            "할인가": 79000,
            "할인율": "11%",
            "총매출액": 62400000,
            "판매건수": 789,
        },
        {
            "주차": "41주차",
            "홈쇼핑사": "현대홈쇼핑",
            "카테고리": "패션/의류",
            "상품명": "24FW 프리미엄 울 100% 핸드메이드 코트",
            "정가": 299000,
            "할인가": 239000,
            "할인율": "20%",
            "총매출액": 88300000,
            "판매건수": 369,
        },
        {
            "주차": "41주차",
            "홈쇼핑사": "롯데홈쇼핑",
            "카테고리": "생활/건강",
            "상품명": "호텔식 고밀도 순면 침구세트 Q",
            "정가": 119000,
            "할인가": 89000,
            "할인율": "25%",
            "총매출액": 31100000,
            "판매건수": 349,
        },
        {
            "주차": "40주차",
            "홈쇼핑사": "NS홈쇼핑",
            "카테고리": "식품",
            "상품명": "국내산 나주배 5kg 선물세트",
            "정가": 59000,
            "할인가": 49000,
            "할인율": "17%",
            "총매출액": 28500000,
            "판매건수": 581,
        },
    ]
    return pd.DataFrame(data)


df = load_data()

# 사이드바 필터
st.sidebar.header("🔍 검색 및 필터")
selected_channel = st.sidebar.selectbox(
    "홈쇼핑사 선택", ["전체"] + list(df["홈쇼핑사"].unique())
)
selected_category = st.sidebar.selectbox(
    "카테고리 선택", ["전체"] + list(df["카테고리"].unique())
)
search_keyword = st.sidebar.text_input("상품명 검색", "")

# 필터링 적용
filtered_df = df.copy()
if selected_channel != "전체":
    filtered_df = filtered_df[filtered_df["홈쇼핑사"] == selected_channel]
if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["카테고리"] == selected_category]
if search_keyword:
    filtered_df = filtered_df[
        filtered_df["상품명"].str.contains(search_keyword, case=False)
    ]

# 상단 요약 지표
col1, col2, col3 = st.columns(3)
col1.metric("조회된 상품 수", f"{len(filtered_df)} 건")
col2.metric(
    "총 매출 합계",
    f"{filtered_df['총매출액'].sum():,} 원" if not filtered_df.empty else "0 원",
)
col3.metric(
    "총 판매 건수",
    f"{filtered_df['판매건수'].sum():,} 건" if not filtered_df.empty else "0 건",
)

st.markdown("---")

# 매출 Top 10 / 전체 테이블
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("🏆 역대 매출 Top 10")
    top10_df = filtered_df.sort_values(by="총매출액", ascending=False).head(10)
    for idx, row in top10_df.iterrows():
        st.info(
            f"**[{row['홈쇼핑사']}] {row['상품명']}**\n\n"
            f"• 매출: **{row['총매출액']:,}원** | 판매량: {row['판매건수']:,}건"
        )

with right_col:
    st.subheader("📋 전체 상품 목록")
    st.dataframe(
        filtered_df[
            [
                "주차",
                "홈쇼핑사",
                "카테고리",
                "상품명",
                "정가",
                "할인가",
                "총매출액",
                "판매건수",
            ]
        ],
        use_container_width=True,
    )
