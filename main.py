import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 레이더",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');

:root {
    --bg: #0a0e1a;
    --panel: #111827;
    --border: #1e293b;
    --accent: #00e5a0;
    --accent2: #3b82f6;
    --accent3: #f59e0b;
    --red: #ef4444;
    --green: #22c55e;
    --text: #e2e8f0;
    --muted: #64748b;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Header */
.radar-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f172a 50%, #0a0e1a 100%);
    border-bottom: 1px solid var(--accent);
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}
.radar-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 40%;
    height: 300%;
    background: radial-gradient(ellipse, rgba(0,229,160,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.radar-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 40%;
    height: 300%;
    background: radial-gradient(ellipse, rgba(59,130,246,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -1px;
    margin: 0;
}
.header-sub {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.25rem;
    letter-spacing: 0.05em;
}

/* Metric cards */
.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--accent); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.up::before { background: var(--green); }
.metric-card.down::before { background: var(--red); }
.metric-card.neutral::before { background: var(--muted); }

.metric-ticker {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.metric-name {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text);
    margin: 0.2rem 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-price {
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text);
    margin: 0.3rem 0;
}
.metric-return {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
}
.metric-return.up { color: var(--green); }
.metric-return.down { color: var(--red); }
.metric-vol {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
}
.flag { font-size: 1rem; margin-right: 0.3rem; }

/* Section labels */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    border-left: 3px solid var(--accent);
    padding-left: 0.75rem;
    margin-bottom: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text) !important;
    font-size: 0.85rem;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0; }

/* Plotly chart background */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* Rank table */
.rank-row {
    display: flex;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
}
.rank-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    width: 24px;
    flex-shrink: 0;
}
.rank-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    margin-right: 0.5rem;
    flex-shrink: 0;
}
.rank-badge.kr { background: rgba(0,229,160,0.15); color: var(--accent); }
.rank-badge.us { background: rgba(59,130,246,0.15); color: var(--accent2); }

/* Loading */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Stock universe ────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "포스코홀딩스": "005490.KS",
    "LG화학": "051910.KS",
    "기아": "000270.KS",
    "삼성SDI": "006400.KS",
    "현대모비스": "012330.KS",
    "SK이노베이션": "096770.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire": "BRK-B",
    "Broadcom": "AVGO",
    "JPMorgan": "JPM",
    "Eli Lilly": "LLY",
    "Visa": "V",
    "Walmart": "WMT",
    "ExxonMobil": "XOM",
    "Netflix": "NFLX",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
}

PERIOD_MAP = {
    "1주": ("7d", "1d"),
    "1개월": ("1mo", "1d"),
    "3개월": ("3mo", "1d"),
    "6개월": ("6mo", "1wk"),
    "1년": ("1y", "1wk"),
    "3년": ("3y", "1mo"),
}

PLOTLY_THEME = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
)

AXIS_STYLE = dict(gridcolor="#1e293b", zerolinecolor="#334155", showgrid=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval,
                         progress=False, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return info
    except Exception:
        return {}

def calc_return(df: pd.DataFrame) -> float | None:
    if df is None or df.empty or len(df) < 2:
        return None
    try:
        start = float(df["Close"].iloc[0])
        end = float(df["Close"].iloc[-1])
        if start == 0:
            return None
        return (end - start) / start * 100
    except Exception:
        return None

def latest_price(df: pd.DataFrame) -> float | None:
    if df is None or df.empty:
        return None
    try:
        return float(df["Close"].iloc[-1])
    except Exception:
        return None

def fmt_return(r: float | None) -> tuple[str, str]:
    if r is None:
        return "N/A", "neutral"
    sign = "▲" if r >= 0 else "▼"
    cls = "up" if r >= 0 else "down"
    return f"{sign} {abs(r):.2f}%", cls

def fmt_price(price: float | None, is_kr: bool) -> str:
    if price is None:
        return "—"
    if is_kr:
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"

def daily_change(df: pd.DataFrame) -> float | None:
    if df is None or len(df) < 2:
        return None
    try:
        return float((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100)
    except Exception:
        return None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:Space Mono,monospace;color:#00e5a0;font-size:1.1rem;
    font-weight:700;letter-spacing:-0.5px;margin-bottom:0.25rem;'>📡 RADAR</div>
    <div style='font-size:0.75rem;color:#64748b;margin-bottom:1.5rem;'>글로벌 주식 분석 대시보드</div>
    """, unsafe_allow_html=True)

    period_label = st.selectbox(
        "📅 기간 선택",
        list(PERIOD_MAP.keys()),
        index=2,
    )
    period, interval = PERIOD_MAP[period_label]

    st.markdown("---")

    kr_selected = st.multiselect(
        "🇰🇷 한국 주식",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER", "현대차", "카카오"],
    )

    us_selected = st.multiselect(
        "🇺🇸 미국 주식",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla", "Microsoft", "Meta"],
    )

    st.markdown("---")
    show_indices = st.toggle("지수 비교 표시", value=True)
    show_volume = st.toggle("거래량 차트 표시", value=False)
    chart_type = st.radio("차트 타입", ["캔들스틱", "라인"], horizontal=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='radar-header'>
  <div class='header-title'>📡 GLOBAL STOCK RADAR</div>
  <div class='header-sub'>한국 · 미국 주요 주식 실시간 수익률 비교 분석</div>
</div>
""", unsafe_allow_html=True)

# ── Fetch data ────────────────────────────────────────────────────────────────
all_selected_kr = {k: KR_STOCKS[k] for k in kr_selected}
all_selected_us = {k: US_STOCKS[k] for k in us_selected}

with st.spinner("시장 데이터 수신 중..."):
    kr_data = {name: fetch_stock(ticker, period, interval) for name, ticker in all_selected_kr.items()}
    us_data = {name: fetch_stock(ticker, period, interval) for name, ticker in all_selected_us.items()}
    if show_indices:
        idx_data = {name: fetch_stock(ticker, period, interval) for name, ticker in INDICES.items()}

# ── Index overview ────────────────────────────────────────────────────────────
if show_indices:
    st.markdown("<div class='section-label'>▸ 주요 지수</div>", unsafe_allow_html=True)
    idx_cols = st.columns(len(INDICES))
    for col, (name, ticker) in zip(idx_cols, INDICES.items()):
        df = idx_data.get(name, pd.DataFrame())
        ret = calc_return(df)
        price = latest_price(df)
        ret_str, ret_cls = fmt_return(ret)
        is_kr = name in ("KOSPI", "KOSDAQ")
        price_str = fmt_price(price, is_kr)
        with col:
            st.markdown(f"""
            <div class='metric-card {ret_cls}'>
              <div class='metric-ticker'>{ticker}</div>
              <div class='metric-name'>{name}</div>
              <div class='metric-price'>{price_str}</div>
              <div class='metric-return {ret_cls}'>{ret_str}</div>
              <div class='metric-vol'>{period_label} 수익률</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Stock cards ───────────────────────────────────────────────────────────────
def render_stock_cards(data_dict: dict, is_kr: bool, flag: str):
    if not data_dict:
        st.info("종목을 선택해주세요.")
        return
    cols = st.columns(min(len(data_dict), 5))
    for i, (name, df) in enumerate(data_dict.items()):
        col = cols[i % 5]
        ret = calc_return(df)
        price = latest_price(df)
        d_chg = daily_change(df)
        ret_str, ret_cls = fmt_return(ret)
        price_str = fmt_price(price, is_kr)
        d_str, d_cls = fmt_return(d_chg)
        with col:
            st.markdown(f"""
            <div class='metric-card {ret_cls}'>
              <div class='metric-ticker'>{flag} {name}</div>
              <div class='metric-price'>{price_str}</div>
              <div class='metric-return {ret_cls}'>{ret_str}</div>
              <div class='metric-vol'>전일대비 <span class='{d_cls}'>{d_str}</span></div>
            </div>
            """, unsafe_allow_html=True)

col_kr, col_us = st.columns(2)
with col_kr:
    st.markdown("<div class='section-label'>▸ 🇰🇷 한국 주식</div>", unsafe_allow_html=True)
    render_stock_cards(kr_data, True, "🇰🇷")

with col_us:
    st.markdown("<div class='section-label'>▸ 🇺🇸 미국 주식</div>", unsafe_allow_html=True)
    render_stock_cards(us_data, False, "🇺🇸")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Return comparison bar chart ───────────────────────────────────────────────
st.markdown("<div class='section-label'>▸ 수익률 비교</div>", unsafe_allow_html=True)

returns_data = []
for name, df in kr_data.items():
    r = calc_return(df)
    if r is not None:
        returns_data.append({"종목": name, "수익률(%)": r, "국가": "🇰🇷 한국", "color": r})
for name, df in us_data.items():
    r = calc_return(df)
    if r is not None:
        returns_data.append({"종목": name, "수익률(%)": r, "국가": "🇺🇸 미국", "color": r})

if returns_data:
    rdf = pd.DataFrame(returns_data).sort_values("수익률(%)", ascending=True)
    colors = ["#22c55e" if v >= 0 else "#ef4444" for v in rdf["수익률(%)"]]
    markers = ["🇰🇷" if c == "🇰🇷 한국" else "🇺🇸" for c in rdf["국가"]]
    labels = [f"{m} {n}" for m, n in zip(markers, rdf["종목"])]

    fig_bar = go.Figure(go.Bar(
        x=rdf["수익률(%)"],
        y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.2f}%" for v in rdf["수익률(%)"]],
        textposition="outside",
        textfont=dict(family="Space Mono, monospace", size=10, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        **PLOTLY_THEME,
        height=max(300, len(rdf) * 38),
        margin=dict(l=0, r=80, t=20, b=20),
        xaxis=dict(ticksuffix="%", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), showgrid=False),
        showlegend=False,
        bargap=0.3,
    )
    fig_bar.update_xaxes(**AXIS_STYLE)
    fig_bar.update_yaxes(gridcolor="rgba(0,0,0,0)", showgrid=False)
    # Zero line
    fig_bar.add_vline(x=0, line=dict(color="#334155", width=1.5))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Normalized price chart ────────────────────────────────────────────────────
st.markdown("<div class='section-label'>▸ 정규화 가격 추이 (기준: 100)</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🌏 전체 비교", "🇰🇷 한국", "🇺🇸 미국"])

KR_PALETTE = ["#00e5a0", "#34d399", "#6ee7b7", "#a7f3d0", "#059669",
              "#047857", "#10b981", "#065f46", "#d1fae5", "#ecfdf5"]
US_PALETTE = ["#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#2563eb",
              "#1d4ed8", "#1e40af", "#1e3a8a", "#dbeafe", "#eff6ff"]

def build_norm_chart(data_dict: dict, label: str, palette: list, height=450):
    fig = go.Figure()
    for i, (name, df) in enumerate(data_dict.items()):
        if df.empty or "Close" not in df.columns:
            continue
        try:
            close = df["Close"].squeeze()
            base = float(close.iloc[0])
            if base == 0:
                continue
            norm = (close / base * 100)
            color = palette[i % len(palette)]
            latest_val = float(norm.iloc[-1])
            delta = latest_val - 100
            sign = "▲" if delta >= 0 else "▼"
            fig.add_trace(go.Scatter(
                x=norm.index,
                y=norm.values,
                name=f"{name} ({sign}{abs(delta):.1f}%)",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>지수: %{{y:.1f}}<extra></extra>",
            ))
        except Exception:
            continue
    fig.add_hline(y=100, line=dict(color="#334155", width=1, dash="dot"))
    fig.update_layout(
        **PLOTLY_THEME,
        height=height,
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, ticksuffix="", title="지수 (시작=100)"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#1e293b",
            borderwidth=1,
            font=dict(size=10),
            orientation="v",
            yanchor="top", y=1,
            xanchor="left", x=1.01,
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig

with tab1:
    all_data = {**{f"🇰🇷{k}": v for k, v in kr_data.items()},
                **{f"🇺🇸{k}": v for k, v in us_data.items()}}
    mixed_palette = []
    for i in range(max(len(kr_data), len(us_data))):
        if i < len(kr_data):
            mixed_palette.append(KR_PALETTE[i % len(KR_PALETTE)])
        if i < len(us_data):
            mixed_palette.append(US_PALETTE[i % len(US_PALETTE)])
    fig_all = build_norm_chart(all_data, "전체", mixed_palette, height=500)
    st.plotly_chart(fig_all, use_container_width=True)

with tab2:
    fig_kr = build_norm_chart(kr_data, "한국", KR_PALETTE)
    st.plotly_chart(fig_kr, use_container_width=True)

with tab3:
    fig_us = build_norm_chart(us_data, "미국", US_PALETTE)
    st.plotly_chart(fig_us, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Individual stock detail ────────────────────────────────────────────────────
st.markdown("<div class='section-label'>▸ 개별 종목 상세 차트</div>", unsafe_allow_html=True)

all_stocks_map = {**{f"🇰🇷 {k}": (v, True) for k, v in all_selected_kr.items()},
                  **{f"🇺🇸 {k}": (v, False) for k, v in all_selected_us.items()}}

if all_stocks_map:
    detail_name = st.selectbox("종목 선택", list(all_stocks_map.keys()), label_visibility="collapsed")
    detail_ticker, detail_is_kr = all_stocks_map[detail_name]
    detail_df = kr_data.get(detail_name.replace("🇰🇷 ", ""),
                us_data.get(detail_name.replace("🇺🇸 ", ""), pd.DataFrame()))

    if not detail_df.empty:
        info = fetch_info(detail_ticker)
        # Info row
        ic1, ic2, ic3, ic4, ic5 = st.columns(5)
        mkt_cap = info.get("marketCap", None)
        pe = info.get("trailingPE", None)
        eps = info.get("trailingEps", None)
        div = info.get("dividendYield", None)
        beta = info.get("beta", None)

        def info_metric(col, label, value):
            with col:
                st.markdown(f"""
                <div style='background:#111827;border:1px solid #1e293b;border-radius:8px;
                padding:0.75rem;text-align:center;'>
                  <div style='font-size:0.7rem;color:#64748b;margin-bottom:0.3rem;
                  font-family:Space Mono,monospace;letter-spacing:0.05em;'>{label}</div>
                  <div style='font-family:Space Mono,monospace;font-size:0.95rem;
                  font-weight:700;color:#e2e8f0;'>{value}</div>
                </div>
                """, unsafe_allow_html=True)

        cap_str = f"${mkt_cap/1e12:.2f}T" if mkt_cap and mkt_cap >= 1e12 else \
                  (f"${mkt_cap/1e9:.1f}B" if mkt_cap else "—")
        info_metric(ic1, "시가총액", cap_str)
        info_metric(ic2, "P/E Ratio", f"{pe:.1f}x" if pe else "—")
        info_metric(ic3, "EPS", f"{eps:.2f}" if eps else "—")
        info_metric(ic4, "배당수익률", f"{div*100:.2f}%" if div else "—")
        info_metric(ic5, "Beta", f"{beta:.2f}" if beta else "—")

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart
        rows = 2 if show_volume else 1
        row_heights = [0.7, 0.3] if show_volume else [1.0]
        fig_detail = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                                   row_heights=row_heights, vertical_spacing=0.05)

        close = detail_df["Close"].squeeze()
        ret_total = calc_return(detail_df)
        line_color = "#22c55e" if (ret_total or 0) >= 0 else "#ef4444"

        if chart_type == "캔들스틱" and all(c in detail_df.columns for c in ["Open", "High", "Low", "Close"]):
            fig_detail.add_trace(go.Candlestick(
                x=detail_df.index,
                open=detail_df["Open"].squeeze(),
                high=detail_df["High"].squeeze(),
                low=detail_df["Low"].squeeze(),
                close=close,
                increasing=dict(line=dict(color="#22c55e"), fillcolor="#22c55e"),
                decreasing=dict(line=dict(color="#ef4444"), fillcolor="#ef4444"),
                name="OHLC",
            ), row=1, col=1)
        else:
            fig_detail.add_trace(go.Scatter(
                x=detail_df.index,
                y=close.values,
                mode="lines",
                line=dict(color=line_color, width=2),
                fill="tozeroy",
                fillcolor=f"rgba({'34,197,94' if line_color=='#22c55e' else '239,68,68'},0.08)",
                name="종가",
            ), row=1, col=1)

        # MA
        if len(close) >= 20:
            ma20 = close.rolling(20).mean()
            fig_detail.add_trace(go.Scatter(
                x=detail_df.index, y=ma20.values,
                mode="lines", line=dict(color="#f59e0b", width=1.2, dash="dot"),
                name="MA20", opacity=0.8,
            ), row=1, col=1)
        if len(close) >= 60:
            ma60 = close.rolling(60).mean()
            fig_detail.add_trace(go.Scatter(
                x=detail_df.index, y=ma60.values,
                mode="lines", line=dict(color="#a78bfa", width=1.2, dash="dot"),
                name="MA60", opacity=0.8,
            ), row=1, col=1)

        if show_volume and "Volume" in detail_df.columns:
            vol = detail_df["Volume"].squeeze()
            vol_colors = []
            for i in range(len(close)):
                if i == 0:
                    vol_colors.append("#3b82f6")
                else:
                    vol_colors.append("#22c55e" if float(close.iloc[i]) >= float(close.iloc[i-1]) else "#ef4444")
            fig_detail.add_trace(go.Bar(
                x=detail_df.index, y=vol.values,
                marker=dict(color=vol_colors, opacity=0.7),
                name="거래량",
            ), row=2, col=1)

        fig_detail.update_layout(
            **PLOTLY_THEME,
            height=500 if show_volume else 400,
            margin=dict(l=0, r=0, t=30, b=20),
            xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            hovermode="x unified",
            title=dict(
                text=f"<b>{detail_name}</b>  <span style='color:#64748b;font-size:12px;'>{detail_ticker}</span>",
                font=dict(size=15, color="#e2e8f0"),
                x=0,
            ),
        )
        fig_detail.update_xaxes(**AXIS_STYLE)
        fig_detail.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_detail, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Ranking table ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>▸ 수익률 순위</div>", unsafe_allow_html=True)

rank_data = []
for name, df in kr_data.items():
    r = calc_return(df)
    if r is not None:
        rank_data.append({"종목": name, "국가": "KR", "수익률(%)": r,
                          "현재가": fmt_price(latest_price(df), True)})
for name, df in us_data.items():
    r = calc_return(df)
    if r is not None:
        rank_data.append({"종목": name, "국가": "US", "수익률(%)": r,
                          "현재가": fmt_price(latest_price(df), False)})

if rank_data:
    rk_df = pd.DataFrame(rank_data).sort_values("수익률(%)", ascending=False).reset_index(drop=True)
    rc1, rc2 = st.columns(2)

    def render_rank(col, title, df_slice):
        with col:
            st.markdown(f"<div style='font-size:0.8rem;color:#64748b;margin-bottom:0.5rem;'>{title}</div>",
                        unsafe_allow_html=True)
            for i, row in df_slice.iterrows():
                r = row["수익률(%)"]
                ret_str, ret_cls = fmt_return(r)
                badge_cls = "kr" if row["국가"] == "KR" else "us"
                st.markdown(f"""
                <div class='rank-row'>
                  <div class='rank-num'>{i+1}</div>
                  <div class='rank-badge {badge_cls}'>{'KR' if row['국가']=='KR' else 'US'}</div>
                  <div style='flex:1;font-size:0.85rem;'>{row['종목']}</div>
                  <div style='font-family:Space Mono,monospace;font-size:0.8rem;margin-right:1rem;
                  color:#64748b;'>{row['현재가']}</div>
                  <div style='font-family:Space Mono,monospace;font-size:0.85rem;font-weight:700;
                  color:{"#22c55e" if r>=0 else "#ef4444"};'>{ret_str}</div>
                </div>
                """, unsafe_allow_html=True)

    half = len(rk_df) // 2 + len(rk_df) % 2
    render_rank(rc1, "📈 상위권", rk_df.iloc[:half])
    render_rank(rc2, "📉 하위권", rk_df.iloc[half:])

# ── Scatter: return vs volatility ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>▸ 수익률 vs 변동성 산점도</div>", unsafe_allow_html=True)

scatter_data = []
for name, df in {**kr_data, **us_data}.items():
    if df.empty or "Close" not in df.columns:
        continue
    r = calc_return(df)
    try:
        close = df["Close"].squeeze()
        vol = float(close.pct_change().std() * 100)
    except Exception:
        vol = None
    if r is not None and vol is not None:
        is_kr = name in kr_data
        scatter_data.append({
            "종목": name,
            "수익률(%)": r,
            "변동성(%)": vol,
            "국가": "🇰🇷 한국" if is_kr else "🇺🇸 미국",
        })

if scatter_data:
    sc_df = pd.DataFrame(scatter_data)
    fig_sc = px.scatter(
        sc_df, x="변동성(%)", y="수익률(%)",
        color="국가",
        color_discrete_map={"🇰🇷 한국": "#00e5a0", "🇺🇸 미국": "#3b82f6"},
        text="종목",
        size_max=12,
    )
    fig_sc.update_traces(
        textposition="top center",
        textfont=dict(size=9, family="Noto Sans KR, sans-serif"),
        marker=dict(size=10, line=dict(width=1, color="#1e293b")),
    )
    fig_sc.add_hline(y=0, line=dict(color="#334155", width=1, dash="dot"))
    fig_sc.update_layout(
        **PLOTLY_THEME,
        height=420,
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis=dict(title="변동성 (%)"),
        yaxis=dict(title="수익률 (%)", ticksuffix="%"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b", borderwidth=1),
    )
    fig_sc.update_xaxes(**AXIS_STYLE)
    fig_sc.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_sc, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 1rem;color:#1e293b;
font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.1em;'>
GLOBAL STOCK RADAR · DATA: YAHOO FINANCE · BUILT WITH STREAMLIT
</div>
""", unsafe_allow_html=True)
