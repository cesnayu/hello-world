import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

DB_FILE = "stock_database.json"

# --- 2. FUNGSI DATABASE ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "vol_watchlist": st.session_state.get("vol_watchlist", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 3. INISIALISASI SESSION ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]
if 'vol_watchlist' not in st.session_state:
    st.session_state.vol_watchlist = saved_data["vol_watchlist"] if (saved_data and "vol_watchlist" in saved_data) else ["GOTO.JK", "BBRI.JK", "BUMI.JK"]

# --- 4. DATA MAPPING ---
SECTOR_MAP = {
    "Banking": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "ARTO.JK"],
    "Energy": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "MDKA.JK", "ANTM.JK", "BUMI.JK"],
    "Telco/Tech": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK", "BUKA.JK", "EMTK.JK"],
    "Consumer": ["ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "KLBF.JK"],
    "Auto": ["ASII.JK", "UNTR.JK", "SMGR.JK", "INTP.JK"]
}

SAMPLE_SCREENER_TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BBTN.JK", "ARTO.JK", "BRIS.JK",
    "TLKM.JK", "ISAT.JK", "EXCL.JK", "TOWR.JK", "TBIG.JK", "MTEL.JK",
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "BUMI.JK", "BYAN.JK",
    "MDKA.JK", "ANTM.JK", "INCO.JK", "AMMN.JK",
    "ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK",
    "AMRT.JK", "MAPI.JK", "ACES.JK",
    "ASII.JK", "UNTR.JK", "AUTO.JK",
    "GOTO.JK", "BUKA.JK", "EMTK.JK",
    "BSDE.JK", "CTRA.JK", "PWON.JK",
    "CPIN.JK", "JPFA.JK"
]

# --- 5. FUNGSI LOGIKA (BACKEND) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    if not tickers: return pd.DataFrame()
    data = yf.download(tickers, period=period, group_by='ticker', progress=False)
    return data

@st.cache_data(ttl=300)
def get_single_stock_detail(ticker, period):
    if not ticker: return None
    try:
        df = yf.download(ticker, period=period, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()] 
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
        return df
    except: return None

@st.cache_data(ttl=600)
def get_seasonal_details(tickers_str, start_month, end_month, lookback_years=5):
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    start_date = datetime.now() - timedelta(days=(lookback_years + 2) * 365)
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=False)
    results = {} 
    for ticker in ticker_list:
        try:
            if len(ticker_list) == 1: df = data; symbol = ticker_list[0]
            else: df = data[ticker]; symbol = ticker
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            stock_years_data = {}
            current_year = datetime.now().year
            for i in range(0, lookback_years + 1):
                y_end = current_year - i
                if int(start_month) > int(end_month): y_start = y_end - 1 
                else: y_start = y_end
                try:
                    d_start = datetime(y_start, int(start_month), 1)
                    if d_start > datetime.now(): continue
                    d_end = datetime(y_end, int(end_month), 28) 
                    label = f"{y_start}/{y_end}" if int(start_month) > int(end_month) else f"{y_end}"
                except: continue
                mask = (df['Date'] >= d_start) & (df['Date'] <= d_end)
                df_period = df.loc[mask].copy()
                if df_period.empty: continue
                first_price = df_period['Close'].iloc[0]
                df_period['Rel_Change'] = ((df_period['Close'] - first_price) / first_price) * 100
                stock_years_data[label] = df_period['Rel_Change'].reset_index(drop=True)
            if stock_years_data: results[symbol] = stock_years_data
        except: continue
    return results

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_str):
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not ticker_list: return None
    data = yf.download(ticker_list, period="1mo", group_by='ticker', progress=False)
    stats = []
    for t in ticker_list:
        try:
            if len(ticker_list) == 1: df = data; symbol = ticker_list[0]
            else: df = data[t]; symbol = t
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            stats.append({
                "Ticker": symbol, 
                "Last Close": df['Close'].iloc[-1], 
                "Volume": df['Volume'].iloc[-1], 
                "Avg Vol": df['Volume'].tail(5).mean(), 
                "Est. Val": df['Close'].iloc[-1] * df['Volume'].iloc[-1]
            })
        except: continue
    return pd.DataFrame(stats)

@st.cache_data(ttl=600)
def get_sector_performance(sector_name):
    tickers = SECTOR_MAP.get(sector_name, [])
    if not tickers: return pd.DataFrame()
    data = yf.download(tickers, period="3mo", group_by='ticker', progress=False)
    perf_list = []
    for t in tickers:
        try:
            if len(tickers) == 1: df = data; symbol = tickers[0]
            else: df = data[t]; symbol = t
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.sort_index()
            curr = df['Close'].iloc[-1]
            def calc_pct(d):
                if len(df) > d: return ((curr - df['Close'].iloc[-(d+1)]) / df['Close'].iloc[-(d+1)]) * 100
                return 0.0
            perf_list.append({"Ticker": symbol, "Price": curr, "1D %": calc_pct(1), "1W %": calc_pct(5), "1M %": calc_pct(20)})
        except: continue
    return pd.DataFrame(perf_list)

@st.cache_data(ttl=3600)
def get_fundamental_screener(tickers_list):
    screener_data = []
    progress_bar = st.progress(0)
    total = len(tickers_list)
    for i, ticker in enumerate(tickers_list):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info 
            industry = info.get('industry', 'Others/Unknown')
            curr_price = info.get('currentPrice', info.get('previousClose', 0))
            high_52 = info.get('fiftyTwoWeekHigh', 0)
            low_52 = info.get('fiftyTwoWeekLow', 0)
            pbv = info.get('priceToBook', None)
            per = info.get('trailingPE', None)
            eps_ttm = info.get('trailingEps', None)
            screener_data.append({
                "Ticker": ticker, "Industry": industry,
                "Price": float(curr_price) if curr_price else 0,
                "52W High": float(high_52) if high_52 else 0,
                "52W Low": float(low_52) if low_52 else 0,
                "PBV": float(pbv) if pbv else None, "PER": float(per) if per else None, "EPS": float
