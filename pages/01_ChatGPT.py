import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ------------------------
# 기본 설정
# ------------------------
st.set_page_config(
    page_title="글로벌 주식 비교",
    layout="wide",
)

st.title("🌍 글로벌 주식 수익률 비교")
st.caption("한국 🇰🇷 vs 미국 🇺🇸 주요 종목")

# ------------------------
# 주식 리스트
# ------------------------
korea_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
}

us_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
}

# ------------------------
# 사이드바
# ------------------------
st.sidebar.header("⚙️ 설정")

selected_korea = st.sidebar.multiselect(
    "🇰🇷 한국 주식",
    list(korea_stocks.keys()),
    default=["삼성전자"]
)

selected_us = st.sidebar.multiselect(
    "🇺🇸 미국 주식",
    list(us_stocks.keys()),
    default=["Apple"]
)

start_date = st.sidebar.date_input("시작 날짜", datetime(2022, 1, 1))
end_date = st.sidebar.date_input("종료 날짜", datetime.today())

# ------------------------
# 티커 변환
# ------------------------
tickers = []

for k in selected_korea:
    tickers.append(korea_stocks[k])

for u in selected_us:
    tickers.append(us_stocks[u])

if len(tickers) == 0:
    st.warning("⚠️ 최소 1개 이상의 종목을 선택하세요.")
    st.stop()

# ------------------------
# 데이터 로딩 (핵심 안정화)
# ------------------------
@st.cache_data
def load_data(tickers, start, end):
    try:
        df = yf.download(
            tickers,
            start=start,
            end=end,
            progress=False,
            threads=False
        )

        if df.empty:
            return None

        # MultiIndex 처리 (여러 종목)
        if isinstance(df.columns, pd.MultiIndex):
            if "Adj Close" in df.columns:
                data = df["Adj Close"]
            else:
                data = df["Close"]

        # 단일 종목 처리
        else:
            if "Adj Close" in df.columns:
                data = df[["Adj Close"]]
            else:
                data = df[["Close"]]

            data.columns = tickers

        return data

    except Exception:
        return None

data = load_data(tickers, start_date, end_date)

if data is None or data.empty:
    st.error("❌ 데이터를 불러오지 못했습니다. (티커 또는 기간 확인)")
    st.stop()

# ------------------------
# 수익률 계산
# ------------------------
returns = (data / data.iloc[0] - 1) * 100

# ------------------------
# 차트
# ------------------------
st.subheader("📈 수익률 비교 (%)")

fig = go.Figure()

for col in returns.columns:
    fig.add_trace(
        go.Scatter(
            x=returns.index,
            y=returns[col],
            mode="lines",
            name=col
        )
    )

fig.update_layout(
    template="plotly_dark",
    height=600,
    legend_title="종목",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 수익률 순위
# ------------------------
st.subheader("🏆 수익률 순위")

latest_returns = returns.iloc[-1].sort_values(ascending=False)

df_returns = pd.DataFrame({
    "종목": latest_returns.index,
    "수익률 (%)": latest_returns.values.round(2)
})

st.dataframe(df_returns, use_container_width=True)

# ------------------------
# 원본 데이터
# ------------------------
with st.expander("📉 원본 데이터 보기"):
    st.dataframe(data, use_container_width=True)
