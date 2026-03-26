import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한/미 주요 주식 비교 분석", layout="wide", page_icon="📈")

st.title("📈 한/미 주요 주식 수익률 비교 분석기")
st.markdown("한국과 미국의 주요 주식들의 **누적 수익률**과 **주가 흐름**을 한눈에 비교해 보세요.")

# --- 사이드바: 설정 영역 ---
st.sidebar.header("설정 (Settings)")

# 1. 날짜 선택
end_date = datetime.today()
start_date = st.sidebar.date_input("시작일", end_date - timedelta(days=365))
end_date = st.sidebar.date_input("종료일", end_date)

# 2. 티커 딕셔너리 (종목명: 티커)
tickers_dict = {
    # 미국 주요 주식
    "Apple (미국)": "AAPL",
    "Microsoft (미국)": "MSFT",
    "NVIDIA (미국)": "NVDA",
    "Tesla (미국)": "TSLA",
    "S&P 500 ETF (미국)": "SPY",
    # 한국 주요 주식 (yfinance에서는 한국 주식 티커 뒤에 .KS(코스피) 또는 .KQ(코스닥)를 붙임)
    "삼성전자 (한국)": "005930.KS",
    "SK하이닉스 (한국)": "000660.KS",
    "NAVER (한국)": "035420.KS",
    "현대차 (한국)": "005380.KS",
    "KODEX 200 (한국)": "069500.KS"
}

# 3. 종목 선택 (기본값 설정)
selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요",
    list(tickers_dict.keys()),
    default=["Apple (미국)", "NVIDIA (미국)", "삼성전자 (한국)", "SK하이닉스 (한국)"]
)

# 데이터 다운로드 함수 (캐싱하여 속도 향상)
@st.cache_data
def load_data(tickers, start, end):
    if not tickers:
        return pd.DataFrame()
    
    # yfinance로 데이터 일괄 다운로드 (Adj Close: 수정 종가 사용)
    data = yf.download(tickers, start=start, end=end)["Adj Close"]
    
    # 단일 종목일 경우 Series로 반환되므로 DataFrame으로 변환
    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])
        
    # 누적 수익률 계산 ( (현재가 - 시작가) / 시작가 * 100 )
    # 데이터의 첫 번째 유효한 행을 기준으로 수익률을 계산합니다.
    returns = (data / data.iloc[0] - 1) * 100
    return data, returns

# --- 메인 화면: 데이터 로드 및 시각화 ---
if selected_names:
    selected_tickers = [tickers_dict[name] for name in selected_names]
    
    with st.spinner('데이터를 불러오는 중입니다...'):
        price_df, return_df = load_data(selected_tickers, start_date, end_date)
    
    # 티커 대신 알아보기 쉬운 종목명으로 컬럼 이름 변경
    reverse_dict = {v: k for k, v in tickers_dict.items()}
    return_df.columns = [reverse_dict.get(col, col) for col in return_df.columns]
    price_df.columns = [reverse_dict.get(col, col) for col in price_df.columns]

    st.subheader(f"📊 누적 수익률 비교 차트 (%)")
    st.markdown("선택한 기간 동안 각 주식에 투자했을 때의 수익률을 보여줍니다. (시작일 = 0%)")
    
    # Plotly로 선 그래프 그리기
    # melt를 사용하여 데이터를 Plotly 친화적인 형태로 변환
    return_df_reset = return_df.reset_index()
    return_df_melted = return_df_reset.melt(id_vars=['Date'], var_name='종목', value_name='수익률(%)')
    
    fig = px.line(return_df_melted, x='Date', y='수익률(%)', color='종목')
    fig.update_layout(hovermode="x unified", xaxis_title="날짜", yaxis_title="누적 수익률 (%)")
    st.plotly_chart(fig, use_container_width=True)

    # 요약 지표 (Metrics)
    st.subheader("💡 기간 내 요약 수익률")
    cols = st.columns(len(selected_names))
    for i, name in enumerate(return_df.columns):
        # 마지막 날의 수익률
        final_return = return_df[name].iloc[-1]
        cols[i].metric(label=name, value=f"{final_return:.2f}%")

    # 원본 데이터 테이블 (옵션)
    with st.expander("원화/달러 종가 상세 데이터 보기"):
        st.dataframe(price_df.sort_index(ascending=False))

else:
    st.warning("👈 사이드바에서 최소 하나 이상의 종목을 선택해 주세요.")
