import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Pulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f0f2f7;
    --surface:  #ffffff;
    --s2:       #f8f9fc;
    --border:   #e4e8f0;
    --b2:       #ced4e8;
    --text:     #0f1629;
    --t2:       #4a5580;
    --t3:       #8892b0;
    --up:       #059669;
    --up-bg:    #ecfdf5;
    --dn:       #dc2626;
    --dn-bg:    #fef2f2;
    --blue:     #2563eb;
    --blue-bg:  #eff4ff;
    --sh1: 0 1px 3px rgba(15,22,41,.06), 0 1px 2px rgba(15,22,41,.04);
    --sh2: 0 4px 16px rgba(15,22,41,.09), 0 2px 6px rgba(15,22,41,.04);
    --r: 14px;  --rs: 9px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.block-container { padding-top: 1.4rem !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: var(--t2) !important;
    font-size: 0.79rem !important;
    font-weight: 500 !important;
}

/* Header */
.sp-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.4rem;
    box-shadow: var(--sh1);
    display: flex; align-items: center; gap: 1.2rem;
    position: relative; overflow: hidden;
}
.sp-header::before {
    content:''; position:absolute; right:-60px; top:-80px;
    width:220px; height:220px;
    background: radial-gradient(circle, rgba(37,99,235,.07) 0%, transparent 65%);
}
.sp-logo {
    width:46px; height:46px; border-radius:12px; flex-shrink:0;
    background: linear-gradient(135deg,#2563eb,#1d4ed8);
    box-shadow: 0 4px 14px rgba(37,99,235,.35);
    display:flex; align-items:center; justify-content:center;
    font-size:1.35rem;
}
.sp-title { font-size:1.55rem; font-weight:700; letter-spacing:-.4px; color:var(--text); }
.sp-title span { color:var(--blue); }
.sp-sub { font-size:.8rem; color:var(--t3); margin-top:.2rem; }
.sp-live {
    margin-left:auto; display:inline-flex; align-items:center; gap:.35rem;
    background:var(--up-bg); color:var(--up);
    font-size:.7rem; font-weight:600; padding:.28rem .7rem;
    border-radius:100px; letter-spacing:.03em; flex-shrink:0;
}
.sp-live::before {
    content:'●'; font-size:.5rem;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }

/* Section */
.sp-sec {
    font-size:.69rem; font-weight:600; letter-spacing:.1em;
    text-transform:uppercase; color:var(--t3);
    display:flex; align-items:center; gap:.5rem;
    margin-bottom:.75rem;
}
.sp-sec::after { content:''; flex:1; height:1px; background:var(--border); }

/* Index cards */
.idx {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--r); padding:1.05rem 1.15rem;
    box-shadow:var(--sh1); position:relative; overflow:hidden;
    transition: box-shadow .2s, transform .2s;
}
.idx:hover { box-shadow:var(--sh2); transform:translateY(-1px); }
.idx::after {
    content:''; position:absolute;
    bottom:0; left:0; right:0; height:3px;
    border-radius: 0 0 var(--r) var(--r);
}
.idx.up::after  { background:var(--up); }
.idx.dn::after  { background:var(--dn); }
.idx.nt::after  { background:var(--b2); }
.idx-tk { font-family:'DM Mono',monospace; font-size:.65rem; color:var(--t3); letter-spacing:.07em; }
.idx-nm { font-size:.8rem; font-weight:600; color:var(--t2); margin:.12rem 0 .45rem; }
.idx-px { font-family:'DM Mono',monospace; font-size:1.2rem; font-weight:500;
           color:var(--text); margin-bottom:.3rem; letter-spacing:-.3px; }
.idx-rt {
    display:inline-flex; align-items:center; gap:.25rem;
    font-family:'DM Mono',monospace; font-size:.78rem; font-weight:500;
    padding:.18rem .55rem; border-radius:6px;
}
.idx-rt.up { background:var(--up-bg); color:var(--up); }
.idx-rt.dn { background:var(--dn-bg); color:var(--dn); }
.idx-rt.nt { background:var(--s2); color:var(--t3); }
.idx-pd { font-size:.67rem; color:var(--t3); margin-top:.38rem; }

/* Stock grid */
.sg { display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:.65rem; }
.sc {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--rs); padding:.85rem .95rem;
    box-shadow:var(--sh1); transition:all .18s;
}
.sc:hover { box-shadow:var(--sh2); transform:translateY(-1px); border-color:var(--b2); }
.sc-nm { font-size:.77rem; font-weight:600; color:var(--t2);
         margin-bottom:.35rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sc-px { font-family:'DM Mono',monospace; font-size:1rem; font-weight:500;
         color:var(--text); margin-bottom:.28rem; letter-spacing:-.2px; }
.sc-rt { font-family:'DM Mono',monospace; font-size:.78rem; font-weight:600; }
.sc-rt.up { color:var(--up); }
.sc-rt.dn { color:var(--dn); }
.sc-rt.nt { color:var(--t3); }
.sc-dy { font-size:.66rem; color:var(--t3); margin-top:.1rem; }

/* Info metrics */
.im {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--rs); padding:.75rem .9rem;
    text-align:center; box-shadow:var(--sh1);
}
.im-l { font-size:.66rem; font-weight:600; color:var(--t3);
        letter-spacing:.06em; text-transform:uppercase; margin-bottom:.3rem; }
.im-v { font-family:'DM Mono',monospace; font-size:.95rem; font-weight:500; color:var(--text); }

/* Rank rows */
.rr {
    display:flex; align-items:center; gap:.45rem;
    padding:.5rem .7rem; border-radius:var(--rs);
    margin-bottom:.25rem; transition:background .14s;
}
.rr:hover { background:var(--s2); }
.rr-n { font-family:'DM Mono',monospace; font-size:.68rem; color:var(--t3); width:20px; text-align:right; flex-shrink:0; }
.rr-b { font-size:.6rem; font-weight:700; padding:.13rem .42rem; border-radius:4px;
        letter-spacing:.04em; flex-shrink:0; }
.rr-b.kr { background:#e0f2fe; color:#0369a1; }
.rr-b.us { background:#ede9fe; color:#6d28d9; }
.rr-nm { flex:1; font-size:.8rem; font-weight:500; color:var(--text); }
.rr-px { font-family:'DM Mono',monospace; font-size:.72rem; color:var(--t3); margin-right:.2rem; }
.rr-rt { font-family:'DM Mono',monospace; font-size:.78rem; font-weight:600; min-width:72px; text-align:right; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":"005930.KS","SK하이닉스":"000660.KS","LG에너지솔루션":"373220.KS",
    "삼성바이오":"207940.KS","현대차":"005380.KS","NAVER":"035420.KS",
    "카카오":"035720.KS","셀트리온":"068270.KS","KB금융":"105560.KS",
    "포스코홀딩스":"005490.KS","LG화학":"051910.KS","기아":"000270.KS",
    "삼성SDI":"006400.KS","현대모비스":"012330.KS","SK이노베이션":"096770.KS",
}
US_STOCKS = {
    "Apple":"AAPL","Microsoft":"MSFT","NVIDIA":"NVDA","Amazon":"AMZN",
    "Alphabet":"GOOGL","Meta":"META","Tesla":"TSLA","Berkshire":"BRK-B",
    "Broadcom":"AVGO","JPMorgan":"JPM","Eli Lilly":"LLY","Visa":"V",
    "Walmart":"WMT","ExxonMobil":"XOM","Netflix":"NFLX",
}
INDICES = {"KOSPI":"^KS11","KOSDAQ":"^KQ11","S&P 500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI"}
PERIOD_MAP = {
    "1주":("7d","1d"),"1개월":("1mo","1d"),"3개월":("3mo","1d"),
    "6개월":("6mo","1wk"),"1년":("1y","1wk"),"3년":("3y","1mo"),
}
PT   = dict(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
            font=dict(family="DM Sans, sans-serif", color="#4a5580", size=11))
AX   = dict(gridcolor="#f0f2f7", zerolinecolor="#e4e8f0", showgrid=True,
            linecolor="#e4e8f0", showline=True)
KRC  = ["#2563eb","#0891b2","#0d9488","#059669","#65a30d","#d97706","#9333ea","#dc2626","#db2777","#0369a1"]
USC  = ["#f97316","#ef4444","#8b5cf6","#ec4899","#14b8a6","#84cc16","#f59e0b","#06b6d4","#6366f1","#10b981"]

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_info(ticker):
    try: return yf.Ticker(ticker).info
    except: return {}

def calc_ret(df):
    if df is None or df.empty or len(df) < 2: return None
    try:
        s, e = float(df["Close"].iloc[0]), float(df["Close"].iloc[-1])
        return (e-s)/s*100 if s else None
    except: return None

def last_px(df):
    try: return float(df["Close"].iloc[-1]) if not df.empty else None
    except: return None

def day_chg(df):
    try: return float((df["Close"].iloc[-1]-df["Close"].iloc[-2])/df["Close"].iloc[-2]*100) if len(df)>=2 else None
    except: return None

def fmt_r(r):
    if r is None: return "—", "nt"
    return ("▲ " if r>=0 else "▼ ")+f"{abs(r):.2f}%", "up" if r>=0 else "dn"

def fmt_p(p, kr):
    if p is None: return "—"
    return f"₩{p:,.0f}" if kr else f"${p:,.2f}"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding:.2rem .4rem 1rem'>"
                "<div style='font-size:1rem;font-weight:700;color:#0f1629;'>📈 Stock Pulse</div>"
                "<div style='font-size:.73rem;color:#8892b0;margin-top:.15rem;'>글로벌 주식 분석</div>"
                "</div>", unsafe_allow_html=True)
    period_label = st.selectbox("기간", list(PERIOD_MAP.keys()), index=2)
    period, interval = PERIOD_MAP[period_label]
    st.divider()
    kr_sel = st.multiselect("🇰🇷 한국 주식", list(KR_STOCKS.keys()),
                             default=["삼성전자","SK하이닉스","NAVER","현대차","카카오"])
    us_sel = st.multiselect("🇺🇸 미국 주식", list(US_STOCKS.keys()),
                             default=["Apple","NVIDIA","Tesla","Microsoft","Meta"])
    st.divider()
    show_idx = st.toggle("지수 카드", value=True)
    show_vol = st.toggle("거래량 차트", value=False)
    ctype    = st.radio("차트 타입", ["캔들스틱","라인"], horizontal=True)

# ── Header ────────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%Y.%m.%d %H:%M")
st.markdown(f"""
<div class='sp-header'>
  <div class='sp-logo'>📈</div>
  <div>
    <div class='sp-title'>Stock <span>Pulse</span></div>
    <div class='sp-sub'>한국 · 미국 주요 주식 실시간 수익률 비교 분석 &nbsp;·&nbsp; {now} KST</div>
  </div>
  <div class='sp-live'>LIVE DATA</div>
</div>
""", unsafe_allow_html=True)

# ── Fetch ─────────────────────────────────────────────────────────────────────
all_kr = {k: KR_STOCKS[k] for k in kr_sel}
all_us = {k: US_STOCKS[k] for k in us_sel}
with st.spinner("시장 데이터 수신 중..."):
    krd = {n: fetch(t, period, interval) for n,t in all_kr.items()}
    usd = {n: fetch(t, period, interval) for n,t in all_us.items()}
    ixd = {n: fetch(t, period, interval) for n,t in INDICES.items()} if show_idx else {}

# ── Index cards ───────────────────────────────────────────────────────────────
if show_idx and ixd:
    st.markdown("<div class='sp-sec'>주요 지수</div>", unsafe_allow_html=True)
    cols = st.columns(len(INDICES))
    for col, (name, ticker) in zip(cols, INDICES.items()):
        df = ixd.get(name, pd.DataFrame())
        r  = calc_ret(df); p = last_px(df)
        rs, rc = fmt_r(r)
        is_kr = name in ("KOSPI","KOSDAQ")
        with col:
            st.markdown(f"""
            <div class='idx {rc}'>
              <div class='idx-tk'>{ticker}</div>
              <div class='idx-nm'>{name}</div>
              <div class='idx-px'>{fmt_p(p, is_kr)}</div>
              <div class='idx-rt {rc}'>{rs}</div>
              <div class='idx-pd'>{period_label} 수익률</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Stock cards ───────────────────────────────────────────────────────────────
def cards_html(data, is_kr, flag):
    if not data:
        return "<p style='color:#8892b0;font-size:.8rem;'>사이드바에서 종목을 선택하세요.</p>"
    h = "<div class='sg'>"
    for name, df in data.items():
        r=calc_ret(df); p=last_px(df); dc=day_chg(df)
        rs,rc=fmt_r(r); dcs,_=fmt_r(dc)
        dc_color="#059669" if (dc or 0)>=0 else "#dc2626"
        h += f"""<div class='sc'>
          <div class='sc-nm'>{flag} {name}</div>
          <div class='sc-px'>{fmt_p(p,is_kr)}</div>
          <div class='sc-rt {rc}'>{rs}</div>
          <div class='sc-dy' style='color:{dc_color};'>전일 {dcs}</div>
        </div>"""
    return h + "</div>"

ck, cu = st.columns(2, gap="large")
with ck:
    st.markdown("<div class='sp-sec'>🇰🇷 한국 주식</div>", unsafe_allow_html=True)
    st.markdown(cards_html(krd, True, "🇰🇷"), unsafe_allow_html=True)
with cu:
    st.markdown("<div class='sp-sec'>🇺🇸 미국 주식</div>", unsafe_allow_html=True)
    st.markdown(cards_html(usd, False, "🇺🇸"), unsafe_allow_html=True)

st.divider()

# ── Return bar ────────────────────────────────────────────────────────────────
st.markdown("<div class='sp-sec'>수익률 비교</div>", unsafe_allow_html=True)
ret_rows = []
for n,df in krd.items():
    r=calc_ret(df)
    if r is not None: ret_rows.append({"종목":f"🇰🇷 {n}","수익률":r})
for n,df in usd.items():
    r=calc_ret(df)
    if r is not None: ret_rows.append({"종목":f"🇺🇸 {n}","수익률":r})

if ret_rows:
    rdf = pd.DataFrame(ret_rows).sort_values("수익률", ascending=True)
    bar_col = ["#059669" if v>=0 else "#dc2626" for v in rdf["수익률"]]
    fig_b = go.Figure(go.Bar(
        x=rdf["수익률"], y=rdf["종목"], orientation="h",
        marker=dict(color=bar_col, opacity=.8, line=dict(width=0)),
        text=[f"{v:+.2f}%" for v in rdf["수익률"]],
        textposition="outside",
        textfont=dict(family="DM Mono, monospace", size=10,
                      color=["#059669" if v>=0 else "#dc2626" for v in rdf["수익률"]]),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:+.2f}%<extra></extra>",
    ))
    fig_b.update_layout(**PT, height=max(260, len(rdf)*35),
                        margin=dict(l=0,r=65,t=8,b=8), showlegend=False, bargap=.38)
    fig_b.update_xaxes(**AX, ticksuffix="%", tickfont=dict(size=10))
    fig_b.update_yaxes(gridcolor="rgba(0,0,0,0)", showgrid=False,
                       tickfont=dict(size=10), showline=False)
    fig_b.add_vline(x=0, line=dict(color="#cbd5e1", width=1.5))
    st.plotly_chart(fig_b, use_container_width=True)

st.divider()

# ── Norm chart ────────────────────────────────────────────────────────────────
st.markdown("<div class='sp-sec'>정규화 가격 추이 (시작 = 100)</div>", unsafe_allow_html=True)

def mk_norm(data, palette, h=420):
    fig = go.Figure()
    for i,(name,df) in enumerate(data.items()):
        if df.empty or "Close" not in df.columns: continue
        try:
            c = df["Close"].squeeze(); base=float(c.iloc[0])
            if base==0: continue
            n2 = c/base*100; delta=float(n2.iloc[-1])-100
            sign="▲" if delta>=0 else "▼"
            fig.add_trace(go.Scatter(
                x=n2.index, y=n2.values,
                name=f"{name}  {sign}{abs(delta):.1f}%",
                line=dict(color=palette[i%len(palette)], width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>지수: %{{y:.1f}}<extra></extra>",
            ))
        except: continue
    fig.add_hline(y=100, line=dict(color="#cbd5e1", width=1.2, dash="dot"))
    fig.update_layout(**PT, height=h, margin=dict(l=0,r=0,t=8,b=8),
        legend=dict(bgcolor="rgba(255,255,255,.92)", bordercolor="#e4e8f0",
                    borderwidth=1, font=dict(size=10), orientation="v",
                    yanchor="top",y=1,xanchor="left",x=1.01),
        hovermode="x unified")
    fig.update_xaxes(**AX); fig.update_yaxes(**AX, title="지수 (시작=100)")
    return fig

t1,t2,t3 = st.tabs(["🌏 전체 비교","🇰🇷 한국","🇺🇸 미국"])
with t1:
    merged={}; mc=[]
    kl=list(krd.items()); ul=list(usd.items())
    for i in range(max(len(kl),len(ul))):
        if i<len(kl): merged[f"🇰🇷 {kl[i][0]}"]=kl[i][1]; mc.append(KRC[i%len(KRC)])
        if i<len(ul): merged[f"🇺🇸 {ul[i][0]}"]=ul[i][1]; mc.append(USC[i%len(USC)])
    st.plotly_chart(mk_norm(merged, mc, h=460), use_container_width=True)
with t2:
    st.plotly_chart(mk_norm(krd, KRC), use_container_width=True)
with t3:
    st.plotly_chart(mk_norm(usd, USC), use_container_width=True)

st.divider()

# ── Detail ────────────────────────────────────────────────────────────────────
st.markdown("<div class='sp-sec'>개별 종목 상세</div>", unsafe_allow_html=True)
all_map={**{f"🇰🇷 {k}":(v,True) for k,v in all_kr.items()},
         **{f"🇺🇸 {k}":(v,False) for k,v in all_us.items()}}

if all_map:
    pick=st.selectbox("종목", list(all_map.keys()), label_visibility="collapsed")
    ptk,pkr=all_map[pick]
    pdf=krd.get(pick.replace("🇰🇷 ",""), usd.get(pick.replace("🇺🇸 ",""), pd.DataFrame()))

    if not pdf.empty:
        info=get_info(ptk)
        mc2=info.get("marketCap"); pe=info.get("trailingPE")
        eps=info.get("trailingEps"); div=info.get("dividendYield"); beta=info.get("beta")
        mc_s=(f"${mc2/1e12:.2f}T" if mc2 and mc2>=1e12 else f"${mc2/1e9:.1f}B" if mc2 else "—")

        def im(col,lbl,val):
            with col:
                st.markdown(f"<div class='im'><div class='im-l'>{lbl}</div>"
                            f"<div class='im-v'>{val}</div></div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        im(c1,"시가총액",mc_s); im(c2,"P/E",f"{pe:.1f}x" if pe else "—")
        im(c3,"EPS",f"{eps:.2f}" if eps else "—")
        im(c4,"배당수익률",f"{div*100:.2f}%" if div else "—")
        im(c5,"Beta",f"{beta:.2f}" if beta else "—")
        st.markdown("<br>", unsafe_allow_html=True)

        cl=pdf["Close"].squeeze(); rv=calc_ret(pdf)
        lc="#059669" if (rv or 0)>=0 else "#dc2626"
        lbg=f"rgba({'5,150,105' if lc=='#059669' else '220,38,38'},.06)"

        rows=2 if show_vol else 1
        rh=[.7,.3] if show_vol else [1.0]
        figd=make_subplots(rows=rows, cols=1, shared_xaxes=True,
                           row_heights=rh, vertical_spacing=.04)

        if ctype=="캔들스틱" and all(c in pdf.columns for c in ["Open","High","Low","Close"]):
            figd.add_trace(go.Candlestick(
                x=pdf.index,
                open=pdf["Open"].squeeze(), high=pdf["High"].squeeze(),
                low=pdf["Low"].squeeze(), close=cl,
                increasing=dict(line=dict(color="#059669"), fillcolor="#059669"),
                decreasing=dict(line=dict(color="#dc2626"), fillcolor="#dc2626"),
                name="OHLC",
            ), row=1, col=1)
        else:
            figd.add_trace(go.Scatter(
                x=pdf.index, y=cl.values, mode="lines",
                line=dict(color=lc, width=2.2),
                fill="tozeroy", fillcolor=lbg, name="종가",
            ), row=1, col=1)

        if len(cl)>=20:
            figd.add_trace(go.Scatter(x=pdf.index, y=cl.rolling(20).mean().values,
                mode="lines", line=dict(color="#d97706",width=1.3,dash="dot"),
                name="MA20", opacity=.9), row=1,col=1)
        if len(cl)>=60:
            figd.add_trace(go.Scatter(x=pdf.index, y=cl.rolling(60).mean().values,
                mode="lines", line=dict(color="#7c3aed",width=1.3,dash="dot"),
                name="MA60", opacity=.9), row=1,col=1)

        if show_vol and "Volume" in pdf.columns:
            vol=pdf["Volume"].squeeze()
            vc=["#059669" if i==0 or float(cl.iloc[i])>=float(cl.iloc[i-1]) else "#dc2626"
                for i in range(len(cl))]
            figd.add_trace(go.Bar(x=pdf.index,y=vol.values,
                marker=dict(color=vc,opacity=.55), name="거래량"), row=2,col=1)

        rs,_=fmt_r(rv)
        figd.update_layout(**PT, height=470 if show_vol else 370,
            margin=dict(l=0,r=0,t=34,b=8), xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="rgba(255,255,255,.92)", bordercolor="#e4e8f0",
                        borderwidth=1, font=dict(size=10)),
            hovermode="x unified",
            title=dict(
                text=f"<b>{pick}</b>  <span style='color:#8892b0;font-size:11px;font-weight:400;'>{ptk} &nbsp; {period_label} {rs}</span>",
                font=dict(size=13,color="#0f1629",family="DM Sans, sans-serif"), x=0,
            ))
        figd.update_xaxes(**AX); figd.update_yaxes(**AX)
        st.plotly_chart(figd, use_container_width=True)

st.divider()

# ── Ranking ───────────────────────────────────────────────────────────────────
st.markdown("<div class='sp-sec'>수익률 순위</div>", unsafe_allow_html=True)
rkr=[]
for n,df in krd.items():
    r=calc_ret(df)
    if r is not None: rkr.append({"종목":n,"국가":"KR","수익률":r,"현재가":fmt_p(last_px(df),True)})
for n,df in usd.items():
    r=calc_ret(df)
    if r is not None: rkr.append({"종목":n,"국가":"US","수익률":r,"현재가":fmt_p(last_px(df),False)})

if rkr:
    rk=pd.DataFrame(rkr).sort_values("수익률",ascending=False).reset_index(drop=True)
    half=len(rk)//2+len(rk)%2
    rc1,rc2=st.columns(2,gap="large")
    def rnd(col,df_s,ttl):
        with col:
            st.markdown(f"<div style='font-size:.72rem;font-weight:600;color:#8892b0;"
                        f"letter-spacing:.07em;margin-bottom:.5rem;'>{ttl}</div>",
                        unsafe_allow_html=True)
            for i,row in df_s.iterrows():
                r=row["수익률"]; rs,_=fmt_r(r)
                rc_col="#059669" if r>=0 else "#dc2626"
                bc="kr" if row["국가"]=="KR" else "us"
                st.markdown(f"""<div class='rr'>
                  <div class='rr-n'>{i+1}</div>
                  <div class='rr-b {bc}'>{row['국가']}</div>
                  <div class='rr-nm'>{row['종목']}</div>
                  <div class='rr-px'>{row['현재가']}</div>
                  <div class='rr-rt' style='color:{rc_col};'>{rs}</div>
                </div>""", unsafe_allow_html=True)
    rnd(rc1, rk.iloc[:half], "📈 상위 종목")
    rnd(rc2, rk.iloc[half:], "📉 하위 종목")

st.divider()

# ── Scatter ───────────────────────────────────────────────────────────────────
st.markdown("<div class='sp-sec'>수익률 vs 변동성</div>", unsafe_allow_html=True)
scr=[]
for n,df in {**krd,**usd}.items():
    if df.empty or "Close" not in df.columns: continue
    r=calc_ret(df)
    try: vol=float(df["Close"].squeeze().pct_change().std()*100)
    except: continue
    if r is not None:
        scr.append({"종목":n,"수익률(%)":r,"변동성(%)":vol,
                    "국가":"🇰🇷 한국" if n in krd else "🇺🇸 미국"})

if scr:
    sc=pd.DataFrame(scr)
    fsc=px.scatter(sc,x="변동성(%)",y="수익률(%)",color="국가",
                   color_discrete_map={"🇰🇷 한국":"#2563eb","🇺🇸 미국":"#f97316"},text="종목")
    fsc.update_traces(
        textposition="top center",
        textfont=dict(size=9,family="DM Sans, sans-serif"),
        marker=dict(size=11,line=dict(width=1.5,color="white"),opacity=.85))
    fsc.add_hline(y=0, line=dict(color="#cbd5e1",width=1.2,dash="dot"))
    fsc.update_layout(**PT, height=390, margin=dict(l=0,r=0,t=8,b=8),
        legend=dict(bgcolor="rgba(255,255,255,.92)",bordercolor="#e4e8f0",
                    borderwidth=1,font=dict(size=10)))
    fsc.update_xaxes(**AX, title="변동성 (%)"); fsc.update_yaxes(**AX, title="수익률 (%)", ticksuffix="%")
    st.plotly_chart(fsc, use_container_width=True)

st.markdown("""<div style='text-align:center;padding:1.2rem 0 .3rem;color:#cbd5e1;
font-size:.68rem;letter-spacing:.08em;font-family:DM Mono,monospace;'>
STOCK PULSE · DATA: YAHOO FINANCE · BUILT WITH STREAMLIT
</div>""", unsafe_allow_html=True)
