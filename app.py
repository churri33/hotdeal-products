import re
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 1. 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="B tv 핫딜 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. 디자인 CSS
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --sidebar-bg: #FFFFFF;
        --sidebar-text: #253449;
        --sidebar-muted: #6F7E90;
        --sidebar-line: #E5E9EF;
        --purple: #3518C9;
        --purple-soft: #EEEAFE;
        --card-bg: #F1F3F7;
        --card-border: #E3E7ED;
        --body-text: #253449;
    }

    /* 밝은 로고에 맞춰 사이드바 전체를 화이트 톤으로 변경 */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: var(--sidebar-bg) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }

    .sidebar-logo-wrap {
        padding: 20px 12px 25px 12px;
        margin-bottom: 14px;
        border-bottom: 1px solid var(--sidebar-line);
    }
    .sidebar-logo-wrap img {
        display: block;
        width: 100%;
        max-width: 258px;
        height: auto;
    }

    /* 메뉴: 아이콘 제거, 2배 크기, 볼드, 왼쪽 정렬 */
    section[data-testid="stSidebar"] div.stButton {
        width: 100%;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        min-height: 62px !important;
        border: 0 !important;
        border-radius: 5px !important;
        background: transparent !important;
        color: var(--sidebar-text) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0 18px !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: var(--purple-soft) !important;
        color: var(--purple) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:focus:not(:active) {
        border: 0 !important;
        box-shadow: none !important;
    }

    /* 하단 DATA SOURCE 고정 */
    .data-source-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 300px;
        box-sizing: border-box;
        padding: 20px 22px 24px 22px;
        background: #F7F8FB;
        border-top: 1px solid var(--sidebar-line);
        z-index: 999;
        color: var(--sidebar-muted);
        font-size: 18px;
        line-height: 1.65;
    }
    .data-source-fixed strong {
        color: #26364A;
        font-size: 18px;
        font-weight: 850;
        letter-spacing: 0.8px;
    }
    .data-source-fixed a {
        color: var(--purple) !important;
        text-decoration: underline;
        font-weight: 750;
    }

    /* 메인 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .section-caption {
        color: #8291A0;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 18px;
    }

    /* KPI 카드: 블랙/네이비가 아닌 연한 회색 계열 */
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 19px 20px 17px 20px;
        min-height: 137px;
        box-sizing: border-box;
    }
    .kpi-label {
        color: #536276;
        font-size: 16px;
        font-weight: 750;
        margin-bottom: 14px;
        text-align: left;
    }
    .kpi-value {
        color: #202D40;
        font-size: clamp(23px, 2.1vw, 31px);
        font-weight: 850;
        letter-spacing: -0.8px;
        line-height: 1.15;
        white-space: nowrap;
        text-align: right;
    }
    .kpi-sub {
        color: #8994A3;
        font-size: 12px;
        margin-top: 9px;
        text-align: right;
    }

    /* 랭킹 제목 */
    .ranking-heading {
        font-size: 20px;
        font-weight: 850;
        margin: 12px 0 10px 0;
        color: #27364A;
    }
    .ranking-accent-sales {
        color: #3518C9;
    }
    .ranking-accent-count {
        color: #0A9470;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 3. 데이터 연결
# =========================================================
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vR6evDMSAeNeklEPyRNzfN9X9Gw02Ub8pzieBWmX_WFtL4h3gmBX_pjKt4Hekysgd7D1zSl4JBq14Cu/"
    "pub?output=csv"
)
GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1UqzVBDl3sTgKSZYty61BKqbvgrmTAIO0M4FaAulpwUo/"
    "edit?gid=686867409#gid=686867409"
)

COLUMN_MAPPING = {
    "총 판매금액": "총매출액",
    "총 판매건수": "판매건수",
    "상품명 (최종)": "상품명",
    "상품명(최종)": "상품명",
    "운영 주차": "주차",
}

@st.cache_data(ttl=300)
def load_data():
    try:
        data = pd.read_csv(SHEET_CSV_URL)
        data.columns = data.columns.astype(str).str.strip()
        data = data.rename(columns=COLUMN_MAPPING)

        # CSV에 함께 들어온 불필요한 엑셀 인덱스/첫 번째 빈 열 제거
        unnamed_cols = [
            col for col in data.columns
            if str(col).strip().lower().startswith("unnamed")
            or str(col).strip() in ("", "index", "인덱스")
        ]
        if unnamed_cols:
            data = data.drop(columns=unnamed_cols)

        # 숫자형 컬럼 정리
        for col in ["총매출액", "판매건수", "할인가", "정가", "할인율"]:
            if col in data.columns:
                cleaned = (
                    data[col]
                    .astype(str)
                    .str.replace(r"[^\d.\-]", "", regex=True)
                )
                data[col] = pd.to_numeric(cleaned, errors="coerce").fillna(0)

        # 문자열 컬럼 공백 정리
        for col in ["주차", "홈쇼핑사", "카테고리", "상품명"]:
            if col in data.columns:
                data[col] = data[col].fillna("").astype(str).str.strip()

        return data
    except Exception as exc:
        st.error(f"구글 시트 데이터를 불러오지 못했습니다: {exc}")
        return pd.DataFrame()

df = load_data()
# =========================================================
# 4. 공통 함수
# =========================================================
def week_number(value):
    """'45주차', 'W45', 45 등에서 주차 숫자를 추출."""
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else -1


def format_won(value):
    return f"{int(round(value)):,}원"


def format_count(value):
    return f"{int(round(value)):,}건"


def format_eok(value, digits=2):
    return f"{value / 100000000:,.{digits}f}억"


def format_man(value):
    return f"{value / 10000:,.1f}만건"


def make_styled_table(frame, highlight_column):
    """TOP50 데이터를 약 10행 높이의 스크롤 표로 표시."""
    if frame.empty:
        st.info("표시할 데이터가 없습니다.")
        return

    styler = frame.style
    styler = styler.set_properties(
        subset=[highlight_column],
        **{
            "background-color": "#EEEAFE" if highlight_column in ["총 매출", "총매출"] else "#E2F5EF",
            "color": "#3518C9" if highlight_column in ["총 매출", "총매출"] else "#087A52",
            "font-weight": "800",
        },
    )

    styler = styler.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", "#E7E9EE"),
                    ("color", "#3D4858"),
                    ("font-weight", "800"),
                    ("text-align", "center"),
                    ("padding", "10px 7px"),
                    ("border-bottom", "1px solid #D4D9E1"),
                    ("white-space", "nowrap"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("text-align", "center"),
                    ("padding", "8px 7px"),
                    ("border-bottom", "1px solid #E8EDF1"),
                    ("font-size", "13px"),
                    ("white-space", "normal"),
                    ("word-break", "keep-all"),
                ],
            },
            {
                "selector": "table",
                "props": [
                    ("width", "100%"),
                    ("border-collapse", "collapse"),
                    ("table-layout", "fixed"),
                ],
            },
        ]
    )

    # 인덱스 숨김 + 약 10행 높이로 제한
    column_config = {
        "운영 주차": st.column_config.TextColumn("운영 주차", width="small"),
        "홈쇼핑사": st.column_config.TextColumn("홈쇼핑사", width="small"),
        "상품명": st.column_config.TextColumn("상품명", width="medium"),
        "총 매출": st.column_config.TextColumn("총 매출", width="medium"),
        "총매출": st.column_config.TextColumn("총매출", width="medium"),
        "판매건수": st.column_config.TextColumn("판매건수", width="small"),
        "할인가": st.column_config.TextColumn("할인가", width="small"),
    }

    st.dataframe(
        styler,
        use_container_width=True,
        hide_index=True,
        height=430,
        column_config=column_config,
    )


def safe_column(frame, column, default=""):
    if column in frame.columns:
        return frame[column]
    return pd.Series([default] * len(frame), index=frame.index)


# =========================================================
# 5. 사이드바
# =========================================================
if "menu" not in st.session_state:
    st.session_state.menu = "종합 실적"

# 로고 PNG는 app.py와 같은 GitHub 저장소 경로에 함께 업로드
logo_path = Path(__file__).parent / "btv_hotdeal_logo.png"

if logo_path.exists():
    st.sidebar.markdown(
        '<div class="sidebar-logo-wrap">',
        unsafe_allow_html=True,
    )
    st.sidebar.image(
        str(logo_path),
        use_container_width=True,
    )
    st.sidebar.markdown(
        '</div>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.warning(
        "로고 파일 btv_hotdeal_logo.png를 저장소에 추가해 주세요."
    )


menu_items = [
    "종합 실적",
    "상품 검색 / 비교",
    "홈쇼핑사별 분석",
]

for label in menu_items:
    if st.sidebar.button(
        label,
        key=f"nav_{label}",
        use_container_width=True,
    ):
        st.session_state.menu = label


st.sidebar.markdown(
    f"""
    <div class="data-source-fixed">
        <strong>DATA SOURCE</strong><br>
        ↗ <a href="{GOOGLE_SHEET_URL}" target="_blank">RAW 구글시트 바로가기</a><br>
        최종 집계일: 26.10.26(월)
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 6. 메뉴 1 - 종합 실적
# =========================================================
if st.session_state.menu == "종합 실적":
    st.title("📊 종합 실적")

    st.markdown(
        '<div class="section-caption">B tv 핫딜 전체 입점 상품의 주요 실적과 랭킹을 한눈에 확인합니다.</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("데이터를 불러오지 못했습니다. 구글 시트를 확인해 주세요.")

    elif "주차" not in df.columns:
        st.error("구글 시트에 '주차' 컬럼이 없습니다.")

    else:
        # 주차 목록 정렬
        week_values = [
            w for w in df["주차"].dropna().unique().tolist()
            if str(w).strip()
        ]
        week_values = sorted(week_values, key=week_number)

        if not week_values:
            st.warning("선택할 수 있는 주차 데이터가 없습니다.")

        else:
            # 시작/끝 주차 필터
            # 오른쪽 두 칸은 공백으로 유지
            filter_cols = st.columns([1, 1, 1, 1])

            with filter_cols[0]:
                start_week = st.selectbox(
                    "시작 주차",
                    options=week_values,
                    index=0,
                    key="start_week",
                )

            with filter_cols[1]:
                end_week = st.selectbox(
                    "끝 주차",
                    options=week_values,
                    index=len(week_values) - 1,
                    key="end_week",
                )

            start_idx = week_values.index(start_week)
            end_idx = week_values.index(end_week)

            if start_idx > end_idx:
                st.warning(
                    "시작 주차가 끝 주차보다 늦습니다. 기간을 다시 선택해 주세요."
                )
                filtered_df = df.iloc[0:0].copy()

            else:
                selected_weeks = week_values[start_idx:end_idx + 1]
                filtered_df = df[df["주차"].isin(selected_weeks)].copy()

            # KPI 계산
            total_sales = (
                filtered_df["총매출액"].sum()
                if "총매출액" in filtered_df.columns else 0
            )

            total_count = (
                filtered_df["판매건수"].sum()
                if "판매건수" in filtered_df.columns else 0
            )

            product_count = (
                filtered_df.loc[
                    filtered_df["상품명"].astype(str).str.strip() != "",
                    "상품명",
                ].nunique()
                if "상품명" in filtered_df.columns else len(filtered_df)
            )

            latest_week = (
                max(
                    filtered_df["주차"].dropna().tolist(),
                    key=week_number,
                )
                if not filtered_df.empty else "-"
            )
                        st.markdown(
                "<div style='height:12px'></div>",
                unsafe_allow_html=True,
            )

            k1, k2, k3, k4 = st.columns(4)

            with k1:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-label">운영 주차</div>
                        <div class="kpi-value">{latest_week}</div>
                        <div class="kpi-sub">선택 기간 내 최신 실적 주차</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k2:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-label">총 매출</div>
                        <div class="kpi-value">{format_eok(total_sales, 2)}</div>
                        <div class="kpi-sub">{format_won(total_sales)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k3:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-label">총 판매 건수</div>
                        <div class="kpi-value">{format_man(total_count)}</div>
                        <div class="kpi-sub">{format_count(total_count)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k4:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-label">판매 상품 종류</div>
                        <div class="kpi-value">{product_count:,}종</div>
                        <div class="kpi-sub">선택 기간 내 상품명 기준</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # -------------------------------------------------
            # 주차별 매출 추이
            # -------------------------------------------------
            st.markdown("---")
            st.subheader("📈 주차별 매출 추이")

            if not filtered_df.empty and "총매출액" in filtered_df.columns:

                trend = (
                    filtered_df.groupby("주차", as_index=False)["총매출액"]
                    .sum()
                )

                trend["_sort"] = trend["주차"].map(week_number)
                trend = trend.sort_values("_sort")
                trend["매출(억)"] = trend["총매출액"] / 100000000

                fig = px.line(
                    trend,
                    x="주차",
                    y="매출(억)",
                    markers=True,
                    custom_data=["주차", "매출(억)"],
                )

                fig.update_traces(
                    line=dict(color="#10B981", width=3),
                    marker=dict(size=8, color="#10B981"),
                    hovertemplate=(
                        "%{customdata[0]}<br>"
                        "%{customdata[1]:,.1f}억"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    height=340,
                    margin=dict(l=10, r=20, t=20, b=10),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    hoverlabel=dict(
                        bgcolor="#102B40",
                        font=dict(color="#FFFFFF", size=13),
                    ),
                    xaxis=dict(
                        title=None,
                        type="category",
                        categoryorder="array",
                        categoryarray=trend["주차"].tolist(),
                        tickangle=0,
                        showgrid=False,
                    ),
                    yaxis=dict(
                        title="매출액 (억 원)",
                        tickformat=",.1f",
                        gridcolor="rgba(130,145,160,0.18)",
                        zeroline=False,
                    ),
                    showlegend=False,
                )

                # 차트 툴바 숨김 + 마우스 휠 확대/축소 비활성화
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": False,
                        "displayModeBar": False,
                        "doubleClick": False,
                    },
                )

            else:
                st.info("선택한 기간에 표시할 매출 데이터가 없습니다.")

            # -------------------------------------------------
            # 상품 랭킹
            # -------------------------------------------------
            st.markdown("---")
            st.subheader("상품 랭킹")

            ranking_df = filtered_df.copy()

            if not ranking_df.empty:

                for col in [
                    "주차",
                    "홈쇼핑사",
                    "상품명",
                    "총매출액",
                    "할인가",
                    "판매건수",
                ]:
                    if col not in ranking_df.columns:
                        ranking_df[col] = (
                            ""
                            if col in ["주차", "홈쇼핑사", "상품명"]
                            else 0
                        )

                # 매출액 TOP 50
                st.markdown(
                    '<div class="ranking-heading">'
                    '<span class="ranking-accent-sales">매출액</span> TOP 50'
                    '</div>',
                    unsafe_allow_html=True,
                )

                sales_top = (
                    ranking_df.sort_values(
                        "총매출액",
                        ascending=False,
                    )
                    .head(50)
                    .copy()
                )

                sales_table = pd.DataFrame({
                    "운영 주차": sales_top["주차"],
                    "홈쇼핑사": sales_top["홈쇼핑사"],
                    "상품명": sales_top["상품명"],
                    "총 매출": sales_top["총매출액"].map(format_won),
                    "할인가": sales_top["할인가"].map(format_won),
                    "판매건수": sales_top["판매건수"].map(format_count),
                })

                make_styled_table(sales_table, "총 매출")

                st.markdown(
                    "<div style='height:20px'></div>",
                    unsafe_allow_html=True,
                )

                # 판매량 TOP 50
                st.markdown(
                    '<div class="ranking-heading">'
                    '<span class="ranking-accent-count">판매량</span> TOP 50'
                    '</div>',
                    unsafe_allow_html=True,
                )

                count_top = (
                    ranking_df.sort_values(
                        "판매건수",
                        ascending=False,
                    )
                    .head(50)
                    .copy()
                )

                count_table = pd.DataFrame({
                    "운영 주차": count_top["주차"],
                    "홈쇼핑사": count_top["홈쇼핑사"],
                    "상품명": count_top["상품명"],
                    "판매건수": count_top["판매건수"].map(format_count),
                    "할인가": count_top["할인가"].map(format_won),
                    "총매출": count_top["총매출액"].map(format_won),
                })

                make_styled_table(count_table, "판매건수")

            else:
                st.info(
                    "선택한 기간에 표시할 상품 랭킹 데이터가 없습니다."
                )
