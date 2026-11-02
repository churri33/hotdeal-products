import html
import io
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="B tv 핫딜 대시보드", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

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
    "총 판매금액": "총매출액", "총 판매건수": "판매건수",
    "상품명 (최종)": "상품명", "상품명(최종)": "상품명", "운영 주차": "주차",
}
NUMERIC_COLUMNS = ["총매출액", "판매건수", "할인가", "정가", "할인율"]
TEXT_COLUMNS = ["주차", "홈쇼핑사", "카테고리", "상품명"]

st.markdown("""
<style>
:root {--purple:#3518C9;--purple-soft:#EEEAFE;--sidebar-line:#E5E9EF;--body-text:#253449;}
section[data-testid="stSidebar"] {background:#FFF!important;width:240px!important;min-width:240px!important;max-width:240px!important;flex-shrink:0!important;}
section[data-testid="stSidebar"] > div,section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {background:#FFF!important;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.45rem;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"],button[kind="header"] {display:none!important;}
.sidebar-title {color:var(--purple);font-size:23px;font-weight:750;letter-spacing:-.8px;line-height:1.3;text-align:left;padding:8px 14px 22px;margin-bottom:25px;border-bottom:1px solid var(--sidebar-line);white-space:nowrap;}
section[data-testid="stSidebar"] div.stButton {width:100%!important;margin:0!important;}
section[data-testid="stSidebar"] div.stButton>button {display:flex!important;width:100%!important;min-height:54px!important;border:0!important;border-radius:6px!important;background:transparent!important;color:#253449!important;text-align:left!important;justify-content:flex-start!important;padding:0 16px!important;font-size:19px!important;font-weight:600!important;letter-spacing:-.35px!important;box-shadow:none!important;white-space:nowrap!important;}
section[data-testid="stSidebar"] div.stButton>button>div {display:flex!important;width:100%!important;justify-content:flex-start!important;text-align:left!important;}
section[data-testid="stSidebar"] div.stButton>button p {width:100%!important;margin:0!important;text-align:left!important;font-size:19px!important;font-weight:600!important;}
section[data-testid="stSidebar"] div[data-testid="stButton"]>button[data-testid="stBaseButton-primary"],section[data-testid="stSidebar"] div.stButton>button[kind="primary"] {background:#EEEAFE!important;color:#3518C9!important;border:1px solid #DDD5FF!important;font-weight:700!important;opacity:1!important;}
section[data-testid="stSidebar"] div[data-testid="stButton"]>button[data-testid="stBaseButton-primary"] *,section[data-testid="stSidebar"] div.stButton>button[kind="primary"] * {color:#3518C9!important;fill:#3518C9!important;}
section[data-testid="stSidebar"] div.stButton>button:hover {background:var(--purple-soft)!important;color:var(--purple)!important;}
section[data-testid="stSidebar"] div.stButton>button:focus:not(:active) {box-shadow:none!important;}
.data-source-fixed {position:fixed;bottom:0;left:0;width:240px;box-sizing:border-box;padding:18px 16px 20px;background:#F7F8FB;border-top:1px solid var(--sidebar-line);z-index:999;color:#6F7E90;font-size:14px;line-height:1.65;}
.data-source-fixed strong {color:#26364A;font-size:16px;font-weight:850;letter-spacing:.6px;}
.data-source-fixed a {color:var(--purple)!important;text-decoration:underline;font-weight:750;}
.main .block-container {padding-top:2rem;padding-bottom:3rem;}
.section-caption {color:#8291A0;font-size:13px;margin-top:-8px;margin-bottom:18px;}
.kpi-card {background:#F1F3F7;border:1px solid #E3E7ED;border-radius:10px;padding:19px 20px 17px;min-height:137px;box-sizing:border-box;}
.kpi-label {color:#536276;font-size:16px;font-weight:750;margin-bottom:14px;text-align:left;}
.kpi-value {color:#202D40;font-size:clamp(23px,2.1vw,31px);font-weight:850;letter-spacing:-.8px;line-height:1.15;white-space:nowrap;text-align:right;}
.kpi-sub {color:#8994A3;font-size:12px;margin-top:9px;text-align:right;}
.ranking-heading {font-size:20px;font-weight:850;margin:12px 0 10px;color:#27364A;}
.ranking-accent-sales {color:#3518C9;}.ranking-accent-count {color:#0A9470;}
.ranking-table-wrap {width:100%;max-height:430px;overflow-y:auto;overflow-x:auto;border:1px solid #E5E9EF;border-radius:7px;background:#FFF;}
table.ranking-table {width:100%;table-layout:fixed;border-collapse:collapse;font-size:13px;}
.ranking-table thead th {position:sticky;top:0;z-index:2;background:#E7E9EE;color:#3D4858;font-weight:800;text-align:center;padding:10px 7px;border-bottom:1px solid #D4D9E1;white-space:nowrap;}
.ranking-table tbody td {color:#253449;text-align:center;vertical-align:middle;padding:8px 7px;border-bottom:1px solid #E8EDF1;white-space:normal;overflow-wrap:anywhere;word-break:keep-all;}
.ranking-table tbody tr:last-child td {border-bottom:0;}
.ranking-table .weekly-products {text-align:left;line-height:1.65;padding:10px 12px;}
.ranking-table .weekly-products div+div {margin-top:4px;}
/* 엑셀 아이콘과 다운로드 화살표만 표시되는 버튼 */
div[data-testid="stDownloadButton"] {display:flex!important;justify-content:flex-end!important;width:100%!important;}
div[data-testid="stDownloadButton"] button {font-size:17px!important;font-weight:750!important;min-height:38px!important;height:38px!important;width:75px!important;padding:4px 9px 4px 37px!important;margin:0!important;justify-content:center!important;background-image:url("data:image/png;base64,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")!important;background-repeat:no-repeat!important;background-size:23px 23px!important;background-position:10px center!important;border:1px solid #D8DFE6!important;border-radius:7px!important;}
/* 다운로드 버튼을 표 바로 위의 오른쪽에 정렬 */
div[data-testid="stDownloadButton"] button p {margin:0!important;}
.weekly-ranking-table tbody td:not(.weekly-products) {font-size:26px!important;font-weight:700!important;}
.weekly-ranking-table tbody td.weekly-products {font-size:13px!important;}
.weekly-ranking-table tbody td.weekly-blue {color:#3518C9!important;font-weight:800!important;}
</style>
""", unsafe_allow_html=True)


def week_sort_key(value):
    """2026년 45주차, 2026-W45, 45주차 등 지원. 연도 미기재 시 주차만 정렬."""
    s = str(value).strip()
    year_match = re.search(r"(?<!\d)(20\d{2})(?!\d)", s)
    year = int(year_match.group(1)) if year_match else 0
    rest = s[:year_match.start()] + s[year_match.end():] if year_match else s
    week_match = re.search(r"(?:W|w|제\s*)?\s*(\d{1,2})\s*(?:주차|주)?", rest)
    week = int(week_match.group(1)) if week_match else -1
    return (year, week, s)


def format_won(value):
    return f"{int(round(value)):,}원"


def format_count(value):
    return f"{int(round(value)):,}건"


def format_eok(value, digits=2):
    return f"{value / 100_000_000:,.{digits}f}억"


def format_man(value):
    return f"{value / 10_000:,.1f}만건"


def dataframe_to_excel(frame, sheet_name="데이터"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        worksheet = writer.sheets[sheet_name[:31]]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        for cells in worksheet.columns:
            max_length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in cells)
            worksheet.column_dimensions[cells[0].column_letter].width = min(max(max_length + 2, 10), 65)
    return output.getvalue()


def excel_button(frame, filename, sheet_name, key):
    st.download_button(
        label="↓",
        data=dataframe_to_excel(frame, sheet_name), file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key, help="엑셀(.xlsx) 다운로드", use_container_width=False,
    )


def make_styled_table(frame, highlight_column=None, widths=None, weekly=False):
    if frame.empty:
        st.info("표시할 데이터가 없습니다.")
        return
    if widths is None:
        widths = [6.0, 9.43, 36.79, 13.0, 13.0, 8.5, 13.28]
    if len(widths) != len(frame.columns):
        widths = [100 / len(frame.columns)] * len(frame.columns)
    col_styles = "".join(f'<col style="width:{w}%">' for w in widths)
    headers = "".join(f"<th>{html.escape(str(c))}</th>" for c in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = []
        for col in frame.columns:
            value = html.escape(str(row[col]))
            style = ""
            if col == highlight_column:
                sales = col in ("총 매출", "총매출", "총 매출액")
                style = f'background:{"#EEEAFE" if sales else "#E2F5EF"};color:{"#3518C9" if sales else "#087A52"};font-weight:800;'
            if weekly and col in ("운영주차", "총 매출액"):
                style += "color:#3518C9;font-weight:800;"
            if weekly and col == "TOP 5 상품":
                value = "".join(f"<div>{html.escape(part)}</div>" for part in str(row[col]).split("\n") if part)
                style += "text-align:left;"
                cells.append(f'<td class="weekly-products" style="{style}">{value}</td>')
            else:
                cells.append(f'<td class="{"weekly-blue" if weekly and col in ("운영주차", "총 매출액") else ""}" style="{style}">{value}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(
        f'<div class="ranking-table-wrap"><table class="ranking-table {"weekly-ranking-table" if weekly else ""}">'
        f'<colgroup>{col_styles}</colgroup><thead><tr>{headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300, show_spinner="구글 시트 데이터 불러오는 중...")
def load_data():
    data = pd.read_csv(SHEET_CSV_URL)
    data.columns = data.columns.astype(str).str.strip()
    data = data.rename(columns=COLUMN_MAPPING)
    if data.columns.duplicated().any():
        data = data.T.groupby(level=0, sort=False).first().T
    for col in NUMERIC_COLUMNS:
        if col in data.columns:
            cleaned = data[col].astype(str).str.replace(r"[^\d.\-]", "", regex=True)
            data[col] = pd.to_numeric(cleaned, errors="coerce").fillna(0)
    for col in TEXT_COLUMNS:
        if col in data.columns:
            data[col] = data[col].fillna("").astype(str).str.strip()
    return data


def aggregate_products(frame, sort_col="총매출액", top_n=50):
    """같은 상품명을 한 상품으로 보고, 매출/판매량을 기간 합산."""
    if frame.empty or "상품명" not in frame.columns:
        return pd.DataFrame()
    working = frame[frame["상품명"].ne("")].copy()
    if working.empty:
        return pd.DataFrame()
    for col in ("총매출액", "판매건수", "할인가", "홈쇼핑사", "주차"):
        if col not in working.columns:
            working[col] = "" if col in ("홈쇼핑사", "주차") else 0
    working["_week_sort"] = working["주차"].map(week_sort_key)
    working = working.sort_values("_week_sort")
    result = (working.groupby("상품명", as_index=False, sort=False)
              .agg(총매출액=("총매출액", "sum"), 판매건수=("판매건수", "sum"),
                   홈쇼핑사=("홈쇼핑사", "last"), 할인가=("할인가", "last"),
                   운영주차수=("주차", "nunique")))
    result = result.sort_values([sort_col, "총매출액", "상품명"], ascending=[False, False, True])
    return result.head(top_n).reset_index(drop=True)


def weekly_ranking(frame):
    """매출액 TOP5 주차. 상품 개수는 해당 주차의 데이터 행 수."""
    if frame.empty:
        return pd.DataFrame(columns=["순위", "운영주차", "총 매출액", "상품 개수", "TOP 5 상품"])
    work = frame.copy()
    for col in ("총매출액", "상품명"):
        if col not in work.columns:
            work[col] = 0 if col == "총매출액" else ""
    summary = (work.groupby("주차", as_index=False)
               .agg(총매출액=("총매출액", "sum"), 상품개수=("주차", "size")))
    summary = summary.sort_values(["총매출액", "주차"], ascending=[False, True]).head(5)
    rows = []
    for rank, (_, item) in enumerate(summary.iterrows(), start=1):
        week = item["주차"]
        week_data = work[(work["주차"] == week) & (work["상품명"].ne(""))]
        products = (week_data.groupby("상품명", as_index=False)["총매출액"].sum()
                    .sort_values(["총매출액", "상품명"], ascending=[False, True]).head(5))
        top5_text = "\n".join(
            f"{i}. {r['상품명']} ({format_eok(r['총매출액'])})"
            for i, (_, r) in enumerate(products.iterrows(), start=1)
        ) or "-"
        rows.append({"순위": rank, "운영주차": week,
                     "총 매출액": f"{format_eok(item['총매출액'])} ({format_won(item['총매출액'])})",
                     "상품 개수": f"{int(item['상품개수']):,}개", "TOP 5 상품": top5_text})
    return pd.DataFrame(rows)


if "menu" not in st.session_state:
    st.session_state.menu = "종합 실적"

st.sidebar.markdown('<div class="sidebar-title">B tv 핫딜 대시보드</div>', unsafe_allow_html=True)
for label in ["종합 실적", "상품 검색 / 비교", "홈쇼핑사별 분석"]:
    st.sidebar.button(label, key=f"nav_{label}", use_container_width=True,
                      type="primary" if st.session_state.menu == label else "secondary",
                      on_click=lambda value=label: st.session_state.update(menu=value))

with st.sidebar:
    if st.button("↻ 데이터 새로고침", help="캐시를 지우고 구글 시트 데이터를 다시 불러옵니다."):
        load_data.clear()
        st.rerun()

try:
    df = load_data()
except Exception as exc:
    st.error(f"구글 시트 데이터를 불러오지 못했습니다: {exc}")
    df = pd.DataFrame()

# 마지막 유효 데이터 행의 날짜를 표시 (최댓값이 아닌 마지막 행 기준).
def last_row_date(frame):
    if frame.empty:
        return "확인 불가"
    date_candidates = [c for c in frame.columns if any(k in str(c).replace(" ", "") for k in
                       ("집계일", "기준일", "등록일", "진행일", "방송일", "운영일", "판매일", "날짜", "일자", "date", "Date"))]
    # 마지막 유효 데이터 행에서 날짜 컬럼을 우선 탐색.
    populated = frame.dropna(how="all")
    if populated.empty:
        return "확인 불가"
    last = populated.iloc[-1]
    for c in date_candidates:
        raw = str(last[c]).strip()
        if raw and raw.lower() not in ("nan", "nat", "none", ""):
            parsed = pd.to_datetime(raw, errors="coerce")
            if pd.notna(parsed):
                return parsed.strftime("%y.%m.%d")
    return "날짜 컬럼 확인 필요"

latest_date = last_row_date(df)
st.sidebar.markdown(
    f'<div class="data-source-fixed"><strong>DATA SOURCE</strong><br>'
    f'↗ <a href="{html.escape(GOOGLE_SHEET_URL, quote=True)}" target="_blank">RAW 구글시트 바로가기</a><br>'
    f'최종 집계일: {html.escape(latest_date)}</div>', unsafe_allow_html=True,
)

if st.session_state.menu == "종합 실적":
    st.title("📊 종합 실적")
    st.markdown('<div class="section-caption">B tv 핫딜 전체 입점 상품의 주요 실적과 랭킹을 한눈에 확인합니다.</div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("데이터를 불러오지 못했거나 시트가 비어 있습니다.")
    elif "주차" not in df.columns:
        st.error("구글 시트에 '주차' 컬럼이 없습니다.")
    else:
        week_values = sorted([w for w in df["주차"].unique().tolist() if str(w).strip()], key=week_sort_key)
        if not week_values:
            st.warning("선택할 수 있는 주차 데이터가 없습니다.")
        else:
            f1, f2, _, _ = st.columns(4)
            with f1:
                start_week = st.selectbox("시작 주차", week_values, index=0, key="start_week")
            with f2:
                end_week = st.selectbox("끝 주차", week_values, index=len(week_values) - 1, key="end_week")
            start_idx, end_idx = week_values.index(start_week), week_values.index(end_week)
            if start_idx > end_idx:
                st.warning("시작 주차가 끝 주차보다 늦습니다. 기간을 다시 선택해 주세요.")
                filtered_df = df.iloc[0:0].copy()
            else:
                filtered_df = df[df["주차"].isin(week_values[start_idx:end_idx + 1])].copy()
            total_sales = filtered_df["총매출액"].sum() if "총매출액" in filtered_df else 0
            total_count = filtered_df["판매건수"].sum() if "판매건수" in filtered_df else 0
            product_count = filtered_df.loc[filtered_df["상품명"].ne(""), "상품명"].nunique() if "상품명" in filtered_df else 0
            operating_weeks = filtered_df["주차"].nunique()
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            kpis = [
                ("총 운영 주차", f"{operating_weeks}주", "선택한 조회 기간"),
                ("총 매출", format_eok(total_sales), format_won(total_sales)),
                ("총 판매 건수", format_man(total_count), format_count(total_count)),
                ("판매 상품 종류", f"{product_count:,}종", "선택 기간 내 고유 상품명 기준"),
            ]
            for col, (label, value, sub) in zip(st.columns(4), kpis):
                with col:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                                f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',
                                unsafe_allow_html=True)
            st.markdown("---")
            title_col, download_col = st.columns([8, 2])
            with title_col:
                st.subheader("📈 주차별 매출 추이")
            if not filtered_df.empty and "총매출액" in filtered_df:
                trend = filtered_df.groupby("주차", as_index=False)["총매출액"].sum()
                trend = trend.sort_values("주차", key=lambda s: s.map(week_sort_key))
                trend["매출(억)"] = trend["총매출액"] / 100_000_000
                with download_col:
                    excel_button(trend[["주차", "매출(억)"]].round({"매출(억)": 2}),
                                 "주차별_매출_추이.xlsx", "주차별 매출", "download_weekly_sales")
                fig = px.line(trend, x="주차", y="매출(억)", markers=True, custom_data=["주차", "매출(억)"])
                fig.update_traces(line=dict(color="#10B981", width=3), marker=dict(size=8, color="#10B981"),
                                  hovertemplate="%{customdata[0]}<br>%{customdata[1]:,.2f}억<extra></extra>")
                fig.update_layout(height=340, margin=dict(l=10, r=20, t=20, b=10),
                                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                  hoverlabel=dict(bgcolor="#102B40", font=dict(color="#FFFFFF", size=13)),
                                  xaxis=dict(title=None, type="category", categoryorder="array",
                                             categoryarray=trend["주차"].tolist(), tickangle=0, showgrid=False),
                                  yaxis=dict(title="매출액 (억 원)", tickformat=",.1f",
                                             gridcolor="rgba(130,145,160,0.18)", zeroline=False), showlegend=False)
                st.plotly_chart(fig, use_container_width=True,
                                config={"scrollZoom": False, "displayModeBar": False, "doubleClick": False})
            else:
                st.info("선택한 기간에 표시할 매출 데이터가 없습니다.")

            # 새로 추가한 주차 랭킹 (그래프 아래 / 상품 랭킹 위)
            st.markdown("---")
            week_title, week_download = st.columns([8, 2])
            with week_title:
                st.subheader("🥇 주차 랭킹")
            st.caption("선택 기간 내 주차별 총매출 TOP 5 · 상품 개수는 해당 주차의 데이터 행 수 기준")
            week_table = weekly_ranking(filtered_df) if "주차" in filtered_df else pd.DataFrame()
            if not week_table.empty:
                with week_download:
                    excel_button(week_table, "주차_랭킹_TOP5.xlsx", "주차 랭킹 TOP5", "download_week_ranking")
                make_styled_table(week_table, widths=[6, 12, 22, 10, 50], weekly=True)
            else:
                st.info("표시할 주차 랭킹이 없습니다.")

            st.markdown("---")
            st.subheader("🏆 상품 랭킹")
            st.caption("동일한 상품명은 선택 기간 내 매출액·판매건수를 합산해 순위를 계산합니다.")
            if filtered_df.empty:
                st.info("선택한 기간에 표시할 상품 랭킹 데이터가 없습니다.")
            else:
                for kind, sort_col, accent, heading, file_name, key in [
                    ("sales", "총매출액", "sales", "① 매출액 TOP 50", "매출액_TOP50.xlsx", "download_sales_top50"),
                    ("count", "판매건수", "count", "② 판매건수 TOP 50", "판매건수_TOP50.xlsx", "download_count_top50"),
                ]:
                    head_col, down_col = st.columns([8, 2])
                    with head_col:
                        st.markdown(f'<div class="ranking-heading"><span class="ranking-accent-{accent}">{heading}</span></div>',
                                    unsafe_allow_html=True)
                    top = aggregate_products(filtered_df, sort_col=sort_col)
                    if top.empty:
                        st.info("표시할 상품이 없습니다.")
                        continue
                    if kind == "sales":
                        table = pd.DataFrame({
                            "순위": range(1, len(top) + 1), "홈쇼핑사": top["홈쇼핑사"],
                            "상품명": top["상품명"], "총 매출": top["총매출액"].map(format_won),
                            "판매건수": top["판매건수"].map(format_count),
                            "운영 주차": top["운영주차수"].map(lambda n: f"{n}주"),
                            "할인가": top["할인가"].map(format_won),
                        })
                        highlight = "총 매출"
                    else:
                        table = pd.DataFrame({
                            "순위": range(1, len(top) + 1), "홈쇼핑사": top["홈쇼핑사"],
                            "상품명": top["상품명"], "판매건수": top["판매건수"].map(format_count),
                            "총매출": top["총매출액"].map(format_won),
                            "운영 주차": top["운영주차수"].map(lambda n: f"{n}주"),
                            "할인가": top["할인가"].map(format_won),
                        })
                        highlight = "판매건수"
                    with down_col:
                        excel_button(table, file_name, heading.replace("① ", "").replace("② ", ""), key)
                    make_styled_table(table, highlight)
                    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

elif st.session_state.menu == "상품 검색 / 비교":
    st.title("🔍 상품 검색 / 비교")
    st.caption("키워드, 가격대, 할인율, 카테고리 등 조건별로 상품을 검색하고 비교합니다.")
    if df.empty:
        st.warning("데이터를 불러오지 못했습니다.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            search_kw = st.text_input("상품명 키워드 검색", placeholder="예: 갈비, 코트, 에어프라이어")
            cats = ["전체"] + sorted(v for v in df["카테고리"].unique() if v) if "카테고리" in df else ["전체"]
            selected_cat = st.selectbox("카테고리 선택", cats)
        with f2:
            chans = ["전체"] + sorted(v for v in df["홈쇼핑사"].unique() if v) if "홈쇼핑사" in df else ["전체"]
            selected_chan = st.selectbox("홈쇼핑사 선택", chans)
            min_discount = st.slider("최소 할인율 (%)", 0, 100, 0, step=5)
        with f3:
            max_price = int(df["할인가"].max()) if "할인가" in df and df["할인가"].max() > 0 else 1_000_000
            price_range = st.slider("할인가 범위 (원)", 0, max_price, (0, max_price), step=max(1, max_price // 200))
        search_df = df.copy()
        if search_kw and "상품명" in search_df:
            search_df = search_df[search_df["상품명"].str.contains(search_kw, case=False, na=False, regex=False)]
        if selected_cat != "전체" and "카테고리" in search_df:
            search_df = search_df[search_df["카테고리"] == selected_cat]
        if selected_chan != "전체" and "홈쇼핑사" in search_df:
            search_df = search_df[search_df["홈쇼핑사"] == selected_chan]
        if "할인율" in search_df:
            search_df = search_df[search_df["할인율"] >= min_discount]
        if "할인가" in search_df:
            search_df = search_df[search_df["할인가"].between(*price_range)]
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        count_unique = search_df["상품명"].loc[search_df["상품명"].ne("")].nunique() if "상품명" in search_df else 0
        c1.metric("검색된 상품 종류", f"{count_unique:,}종")
        c2.metric("검색 상품 총 매출액", format_won(search_df["총매출액"].sum()) if "총매출액" in search_df else "0원")
        c3.metric("검색 상품 평균 할인가", format_won(search_df["할인가"].mean()) if len(search_df) and "할인가" in search_df else "0원")
        st.caption(f"조건에 해당하는 데이터 행 수: {len(search_df):,}건")
        display_df = search_df.drop(columns=["객단가"], errors="ignore").copy()
        for col in ("총매출액", "할인가", "정가", "판매건수"):
            if col in display_df:
                display_df[col] = display_df[col].map(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        excel_button(search_df.drop(columns=["객단가"], errors="ignore"), "상품_검색_결과.xlsx", "상품 검색 결과", "download_search")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

elif st.session_state.menu == "홈쇼핑사별 분석":
    st.title("🏢 홈쇼핑사별 분석")
    st.caption("제휴 홈쇼핑사별 입점 성과, 히스토리 및 효자 상품을 분석합니다.")
    if df.empty or "홈쇼핑사" not in df or not df["홈쇼핑사"].ne("").any():
        st.warning("홈쇼핑사 데이터가 없습니다.")
    else:
        partners = sorted(v for v in df["홈쇼핑사"].unique() if v)
        selected_partner = st.selectbox("분석할 홈쇼핑사", partners)
        partner_df = df[df["홈쇼핑사"] == selected_partner].copy()
        p1, p2, p3 = st.columns(3)
        count_unique = partner_df["상품명"].loc[partner_df["상품명"].ne("")].nunique() if "상품명" in partner_df else 0
        p1.metric("누적 진행 상품 종류", f"{count_unique:,}종")
        p2.metric("누적 총 매출액", format_won(partner_df["총매출액"].sum()) if "총매출액" in partner_df else "0원")
        top_cat = partner_df["카테고리"].loc[partner_df["카테고리"].ne("")].mode() if "카테고리" in partner_df else pd.Series(dtype=str)
        p3.metric("주력 카테고리", top_cat.iloc[0] if not top_cat.empty else "-")
        st.markdown("---")
        left, right = st.columns(2)
        with left:
            st.subheader(f"{selected_partner} 역대 효자 상품 TOP 5")
            top5 = aggregate_products(partner_df, top_n=5)
            if not top5.empty:
                excel_button(top5[["상품명", "총매출액", "판매건수", "운영주차수"]], "홈쇼핑사_TOP5.xlsx", "효자 상품 TOP5", "download_partner_top5")
                st.dataframe(top5[["상품명", "총매출액", "판매건수", "운영주차수"]], use_container_width=True, hide_index=True)
        with right:
            st.subheader(f"{selected_partner} 주차별 매출 흐름")
            if "주차" in partner_df and "총매출액" in partner_df:
                trend = partner_df.groupby("주차", as_index=False)["총매출액"].sum()
                trend = trend.sort_values("주차", key=lambda s: s.map(week_sort_key))
                trend["매출(억)"] = trend["총매출액"] / 100_000_000
                fig = px.line(trend, x="주차", y="매출(억)", markers=True)
                fig.update_traces(line=dict(color="#10B981", width=3),
                                  hovertemplate="%{x}<br>%{y:,.2f}억<extra></extra>")
                fig.update_layout(height=300, margin=dict(l=5, r=5, t=15, b=5),
                                  xaxis=dict(type="category", categoryorder="array", categoryarray=trend["주차"].tolist()),
                                  showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
        st.markdown("---")
        st.subheader(f"{selected_partner} 전체 딜 진행 히스토리")
        history = partner_df.drop(columns=["객단가"], errors="ignore").copy()
        for col in ("총매출액", "할인가", "정가", "판매건수"):
            if col in history:
                history[col] = history[col].map(lambda x: f"{int(round(x)):,}" if pd.notna(x) else "")
        excel_button(partner_df.drop(columns=["객단가"], errors="ignore"),
                     "홈쇼핑사_진행_히스토리.xlsx", "진행 히스토리", "download_partner")
        st.dataframe(history, use_container_width=True, hide_index=True)
