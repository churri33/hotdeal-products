import re
import html
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

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

    /* 사이드바: 80% 폭으로 고정, 접기 버튼 숨김 */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        width: 240px !important;
        min-width: 240px !important;
        max-width: 240px !important;
        flex-shrink: 0 !important;
        transform: none !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: var(--sidebar-bg) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }

    /* 사이드바 접기/펼치기 컨트롤 제거 */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
    }

    /* 사이드바 텍스트형 타이틀 */
    .sidebar-title {
        color: var(--purple);
        font-size: 23px;
        font-weight: 750;
        letter-spacing: -0.8px;
        line-height: 1.3;
        text-align: left;
        padding: 22px 14px 20px 14px;
        margin-bottom: 12px;
        border-bottom: 1px solid var(--sidebar-line);
        white-space: nowrap;
    }

    /* 메뉴: 아이콘 없이 크게, 굵게, 왼쪽 정렬 */
    section[data-testid="stSidebar"] div.stButton {
        width: 100% !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        display: flex !important;
        width: 100% !important;
        min-height: 54px !important;
        border: 0 !important;
        border-radius: 6px !important;
        background: transparent !important;
        color: var(--sidebar-text) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0 16px !important;
        font-size: 19px !important;
        font-weight: 600 !important;
        letter-spacing: -0.35px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] div.stButton > button > div {
        display: flex !important;
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }
    section[data-testid="stSidebar"] div.stButton > button p {
        width: 100% !important;
        margin: 0 !important;
        text-align: left !important;
        font-size: 19px !important;
        font-weight: 600 !important;
    }
    /* 선택된 메뉴: Streamlit primary 버튼을 기준으로 강제 스타일 */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"],
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: #EEEAFE !important;
        background-color: #EEEAFE !important;
        color: #3518C9 !important;
        border: 1px solid #DDD5FF !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] *,
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * {
        color: #3518C9 !important;
        fill: #3518C9 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: #253449 !important;
        border: 1px solid transparent !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: var(--purple-soft) !important;
        color: var(--purple) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:focus:not(:active) {
        border: 0 !important;
        box-shadow: none !important;
    }

    /* 하단 DATA SOURCE */
    .data-source-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 240px;
        box-sizing: border-box;
        padding: 18px 16px 20px 16px;
        background: #F7F8FB;
        border-top: 1px solid var(--sidebar-line);
        z-index: 999;
        color: var(--sidebar-muted);
        font-size: 15px;
        line-height: 1.65;
    }
    .data-source-fixed strong {
        color: #26364A;
        font-size: 16px;
        font-weight: 850;
        letter-spacing: 0.6px;
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

    /* TOP 50 표: 실제 HTML 테이블로 열 너비와 내부 스크롤 고정 */
    .ranking-table-wrap {
        width: 100%;
        max-height: 430px;
        overflow-y: auto;
        overflow-x: hidden;
        border: 1px solid #E5E9EF;
        border-radius: 7px;
        background: #FFFFFF;
    }
    table.ranking-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 13px;
    }
    .ranking-table thead th {
        position: sticky;
        top: 0;
        z-index: 2;
        background: #E7E9EE;
        color: #3D4858;
        font-weight: 800;
        text-align: center;
        padding: 10px 7px;
        border-bottom: 1px solid #D4D9E1;
        white-space: nowrap;
    }
    .ranking-table tbody td {
        color: #253449;
        text-align: center;
        vertical-align: middle;
        padding: 8px 7px;
        border-bottom: 1px solid #E8EDF1;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: keep-all;
    }
    .ranking-table tbody tr:last-child td {
        border-bottom: 0;
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
    """TOP50 데이터를 열 너비 비율이 고정된 내부 스크롤 표로 표시."""
    if frame.empty:
        st.info("표시할 데이터가 없습니다.")
        return

    # 요청 비율: 운영주차 0.5, 홈쇼핑사 0.5, 상품명 1.3,
    # 나머지 3개 열은 각 1.0 (총 5.3 기준)
    widths = [9.43, 9.43, 24.53, 18.87, 18.87, 18.87]
    col_styles = "".join(
        f'<col style="width:{width}%;min-width:0">'
        for width in widths[:len(frame.columns)]
    )
    headers = "".join(
        f'<th style="width:{widths[i]}%;max-width:{widths[i]}%">'
        f'{html.escape(str(col))}</th>'
        for i, col in enumerate(frame.columns)
    )

    rows = []
    for _, row in frame.iterrows():
        cells = []
        for i, col in enumerate(frame.columns):
            value = html.escape(str(row[col]))
            width_style = f"width:{widths[i]}%;max-width:{widths[i]}%;"
            if col == highlight_column:
                color = "#3518C9" if highlight_column in ["총 매출", "총매출"] else "#087A52"
                bg = "#EEEAFE" if highlight_column in ["총 매출", "총매출"] else "#E2F5EF"
                cells.append(
                    f'<td style="{width_style}background:{bg};color:{color};font-weight:800">{value}</td>'
                )
            else:
                cells.append(f'<td style="{width_style}">{value}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    table_html = (
        '<div class="ranking-table-wrap"><table class="ranking-table" '
        'style="width:100%;min-width:100%;table-layout:fixed">'
        f"<colgroup>{col_styles}</colgroup>"
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

def safe_column(frame, column, default=""):
    if column in frame.columns:
        return frame[column]
    return pd.Series([default] * len(frame), index=frame.index)

# =========================================================
# 5. 사이드바
# =========================================================
if "menu" not in st.session_state:
    st.session_state.menu = "종합 실적"

# 로고 이미지 대신 텍스트 타이틀 사용
st.sidebar.markdown(
    '<div class="sidebar-title">B tv 핫딜 대시보드</div>',
    unsafe_allow_html=True,
)

def set_active_menu(label):
    st.session_state.menu = label

menu_items = ["종합 실적", "상품 검색 / 비교", "홈쇼핑사별 분석"]
for label in menu_items:
    is_active = st.session_state.menu == label
    st.sidebar.button(
        label,
        key=f"nav_{label}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
        on_click=set_active_menu,
        args=(label,),
    )

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
        week_values = [w for w in df["주차"].dropna().unique().tolist() if str(w).strip()]
        week_values = sorted(week_values, key=week_number)

        if not week_values:
            st.warning("선택할 수 있는 주차 데이터가 없습니다.")
        else:
            # 시작/끝 주차 필터는 KPI 카드의 첫 번째/두 번째 너비에 맞추고
            # 오른쪽 두 칸은 비워 둠
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
                st.warning("시작 주차가 끝 주차보다 늦습니다. 기간을 다시 선택해 주세요.")
                filtered_df = df.iloc[0:0].copy()
            else:
                selected_weeks = week_values[start_idx : end_idx + 1]
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
                    filtered_df["상품명"].astype(str).str.strip() != "", "상품명"
                ].nunique()
                if "상품명" in filtered_df.columns else len(filtered_df)
            )
            # 총 운영 주차는 선택한 주차 범위의 양 끝을 포함해 계산
            total_operating_weeks = end_idx - start_idx + 1 if start_idx <= end_idx else 0

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(
                    f"""<div class="kpi-card">
                    <div class="kpi-label">총 운영 주차</div>
                    <div class="kpi-value">{total_operating_weeks}주</div>
                    <div class="kpi-sub">선택한 조회 기간</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    f"""<div class="kpi-card">
                    <div class="kpi-label">총 매출</div>
                    <div class="kpi-value">{format_eok(total_sales, 2)}</div>
                    <div class="kpi-sub">{format_won(total_sales)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    f"""<div class="kpi-card">
                    <div class="kpi-label">총 판매 건수</div>
                    <div class="kpi-value">{format_man(total_count)}</div>
                    <div class="kpi-sub">{format_count(total_count)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with k4:
                st.markdown(
                    f"""<div class="kpi-card">
                    <div class="kpi-label">판매 상품 종류</div>
                    <div class="kpi-value">{product_count:,}종</div>
                    <div class="kpi-sub">선택 기간 내 상품명 기준</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

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
                    hovertemplate="%{customdata[0]}<br>%{customdata[1]:,.1f}억<extra></extra>",
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
                # Plotly 차트 툴바를 숨기고, 마우스 휠 확대/축소를 비활성화
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

            st.markdown("---")
            st.subheader("🏆 상품 랭킹")

            # 공통 랭킹 데이터 준비
            ranking_df = filtered_df.copy()
            if not ranking_df.empty:
                for col in ["주차", "홈쇼핑사", "상품명", "총매출액", "할인가", "판매건수"]:
                    if col not in ranking_df.columns:
                        ranking_df[col] = "" if col in ["주차", "홈쇼핑사", "상품명"] else 0

                # 매출액 TOP 50
                st.markdown('<div class="ranking-heading">① <span class="ranking-accent-sales">매출액</span> TOP 50</div>', unsafe_allow_html=True)
                sales_top = ranking_df.sort_values(
                    "총매출액", ascending=False
                ).head(50).copy()
                sales_table = pd.DataFrame({
                    "운영 주차": sales_top["주차"],
                    "홈쇼핑사": sales_top["홈쇼핑사"],
                    "상품명": sales_top["상품명"],
                    "총 매출": sales_top["총매출액"].map(format_won),
                    "할인가": sales_top["할인가"].map(format_won),
                    "판매건수": sales_top["판매건수"].map(format_count),
                })
                make_styled_table(sales_table, "총 매출")

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                # 판매건수 TOP 50
                st.markdown('<div class="ranking-heading">② <span class="ranking-accent-count">판매건수</span> TOP 50</div>', unsafe_allow_html=True)
                count_top = ranking_df.sort_values(
                    "판매건수", ascending=False
                ).head(50).copy()
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
                st.info("선택한 기간에 표시할 상품 랭킹 데이터가 없습니다.")

# =========================================================
# 7. 메뉴 2 - 상품 검색 / 비교
# =========================================================
elif st.session_state.menu == "상품 검색 / 비교":
    st.title("🔍 상품 검색 / 비교")
    st.caption("키워드, 가격대, 할인율, 카테고리 등 조건별로 상품을 검색하고 비교합니다.")

    if df.empty:
        st.warning("데이터를 불러오지 못했습니다.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            search_kw = st.text_input("상품명 키워드 검색", placeholder="예: 갈비, 코트, 에어프라이어")
            cats = ["전체"] + sorted(df["카테고리"].dropna().unique().tolist()) if "카테고리" in df else ["전체"]
            selected_cat = st.selectbox("카테고리 선택", cats)
        with f2:
            chans = ["전체"] + sorted(df["홈쇼핑사"].dropna().unique().tolist()) if "홈쇼핑사" in df else ["전체"]
            selected_chan = st.selectbox("홈쇼핑사 선택", chans)
            min_discount = st.slider("최소 할인율 (%)", 0, 100, 0, step=5)
        with f3:
            max_price = int(df["할인가"].max()) if "할인가" in df.columns and df["할인가"].max() > 0 else 1000000
            price_range = st.slider("할인가 범위 (원)", 0, max_price, (0, max_price), step=max(1, max_price // 200))

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
            search_df = search_df[search_df["할인가"].between(price_range[0], price_range[1])]

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("검색된 상품 수", f"{len(search_df):,}건")
        c2.metric("검색 상품 총 매출액", format_won(search_df["총매출액"].sum()) if "총매출액" in search_df else "0원")
        c3.metric("검색 상품 평균 할인가", format_won(search_df["할인가"].mean()) if len(search_df) and "할인가" in search_df else "0원")

        display_df = search_df.copy()
        for col in ["총매출액", "할인가", "정가", "판매건수"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].map(
                    lambda x: f"{int(round(x)):,}" if pd.notna(x) else ""
                )
        if "객단가" in display_df.columns:
            display_df = display_df.drop(columns=["객단가"])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================================================
# 8. 메뉴 3 - 홈쇼핑사별 분석
# =========================================================
elif st.session_state.menu == "홈쇼핑사별 분석":
    st.title("🏢 홈쇼핑사별 분석")
    st.caption("제휴 홈쇼핑사별 입점 성과, 히스토리 및 효자 상품을 분석합니다.")

    if df.empty or "홈쇼핑사" not in df.columns:
        st.warning("홈쇼핑사 데이터가 없습니다.")
    else:
        partners = sorted(df["홈쇼핑사"].dropna().unique().tolist())
        selected_partner = st.selectbox("분석할 홈쇼핑사", partners)
        partner_df = df[df["홈쇼핑사"] == selected_partner].copy()

        p1, p2, p3 = st.columns(3)
        p1.metric("누적 진행 상품 수", f"{len(partner_df):,}건")
        p2.metric("누적 총 매출액", format_won(partner_df["총매출액"].sum()) if "총매출액" in partner_df else "0원")
        top_cat = partner_df["카테고리"].mode().iloc[0] if "카테고리" in partner_df and not partner_df["카테고리"].mode().empty else "-"
        p3.metric("주력 카테고리", top_cat)

        st.markdown("---")
        left, right = st.columns(2)
        with left:
            st.subheader(f"{selected_partner} 역대 효자 상품 TOP 5")
            if "총매출액" in partner_df.columns:
                top5 = partner_df.sort_values("총매출액", ascending=False).head(5).copy()
                cols = [c for c in ["주차", "상품명", "총매출액", "판매건수", "할인가"] if c in top5.columns]
                st.dataframe(top5[cols], use_container_width=True, hide_index=True)
        with right:
            st.subheader(f"{selected_partner} 주차별 매출 흐름")
            if "주차" in partner_df.columns and "총매출액" in partner_df.columns:
                partner_trend = partner_df.groupby("주차", as_index=False)["총매출액"].sum()
                partner_trend["_sort"] = partner_trend["주차"].map(week_number)
                partner_trend = partner_trend.sort_values("_sort")
                partner_trend["매출(억)"] = partner_trend["총매출액"] / 100000000
                fig = px.line(partner_trend, x="주차", y="매출(억)", markers=True)
                fig.update_traces(line=dict(color="#10B981", width=3), hovertemplate="%{x}<br>%{y:,.1f}억<extra></extra>")
                fig.update_layout(height=300, margin=dict(l=5, r=5, t=15, b=5), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        st.markdown("---")
        st.subheader(f"{selected_partner} 전체 딜 진행 히스토리")
        history = partner_df.copy()
        if "객단가" in history.columns:
            history = history.drop(columns=["객단가"])
        for col in ["총매출액", "할인가", "정가", "판매건수"]:
            if col in history.columns:
                history[col] = history[col].map(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "")
        st.dataframe(history, use_container_width=True, hide_index=True)
