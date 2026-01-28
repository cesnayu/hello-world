import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os

# --- 1. KONFIGURASI & DATABASE FILE ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

DB_FILE = "stock_database.json"

# --- FUNGSI SIMPAN & LOAD DATABASE ---
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

# --- 2. INISIALISASI SESSION STATE ---
saved_data = load_data()

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]

if 'vol_watchlist' not in st.session_state:
    st.session_state.vol_watchlist = saved_data["vol_watchlist"] if (saved_data and "vol_watchlist" in saved_data) else ["GOTO.JK", "BBRI.JK", "BUMI.JK"]

# --- 3. DATA MAPPING (SEKTOR) ---
SECTOR_MAP = {
    "Banking (Finance)": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BBTN.JK", "ARTO.JK"],
    "Energy & Mining": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "MDKA.JK", "ANTM.JK", "INCO.JK", "BUMI.JK"],
    "Telco & Tech": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK", "BUKA.JK", "EMTK.JK"],
    "Consumer Goods": ["ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "GGRM.JK", "HMSP.JK", "KLBF.JK"],
    "Infrastructure & Auto": ["ASII.JK", "JSMR.JK", "UNTR.JK", "SMGR.JK", "INTP.JK"]
}

# --- 4. FUNGSI LOGIKA (BACKEND) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    """Untuk Grid View (Banyak Saham, Periode Pendek)"""
    if not tickers: return pd.DataFrame()
    data = yf.download(tickers, period=period, group_by='ticker', progress=False)
    return data

# --- INI FUNGSI YG TADINYA HILANG/ERROR ---
@st.cache_data(ttl=300)
def get_single_stock_detail(ticker, period):
    """
    Untuk Single Stock Analysis (1 Saham, Periode Fleksibel).
    Mengambil data OHLCV lengkap.
    """
    if not ticker: return None
    df = yf.download(ticker, period=period, progress=False)
    if df.empty: return None
    
    df = df.reset_index()
    # Flatten MultiIndex columns jika ada
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = [col[0] if col[1] == '' else col[0] for col in df.columns]
        except:
            pass
    return df
# ------------------------------------------

@st.cache_data(ttl=600)
def get_seasonal_cycle(tickers_str, start_month, end_month, lookback_years=5):
    """
    Menghitung rata-rata kinerja saham pada range bulan tertentu.
    """
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    
    start_date = datetime.now() - timedelta(days=(lookback_years + 1) * 365)
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=False)
    
    result_traces = []

    for ticker in ticker_list:
        try:
            if len(ticker_list) == 1:
                df = data
                symbol = ticker_list[0]
            else:
                df = data[ticker]
                symbol = ticker
            
            if df.empty: continue
            df = df.reset_index()
            if 'Date' not in df.columns:
                 pass 
            df['Date'] = pd.to_datetime(df['Date'])
            
            yearly_movements = []
            current_year = datetime.now().year
            
            for i in range(1, lookback_years + 1):
                y_end = current_year - i
                y_start = y_end if int(start_month) < int(end_month) else y_end - 1
                
                try:
                    d_start = datetime(y_start, int(start_month), 1)
                    d_end = datetime(y_end, int(end_month), 28) 
                except: continue
                
                mask = (df['Date'] >= d_start) & (df['Date'] <= d_end)
                df_period = df.loc[mask].copy()
                if df_period.empty: continue
                
                first_price = df_period['Close'].iloc[0]
                df_period['Rel_Change'] = ((df_period['Close'] - first_price) / first_price) * 100
                df_period = df_period.reset_index(drop=True)
                yearly_movements.append(df_period['Rel_Change'])
            
            if not yearly_movements: continue
            
            df_concat = pd.concat(yearly_movements, axis=1)
            avg_trend = df_concat.mean(axis=1)
            
            result_traces.append({"Ticker": symbol, "Data": avg_trend})
        except Exception: continue
    return result_traces

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_str):
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not ticker_list: return None
    data = yf.download(ticker_list, period="1mo", group_by='ticker', progress=False)
    stats = []
    for t in ticker_list:
        try:
            if len(ticker_list) == 1:
                df = data
                symbol = ticker_list[0]
            else:
                df = data[t]
                symbol = t
            if df.empty: continue
            last_vol = df['Volume'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            avg_vol_1w = df['Volume'].tail(5).mean()
            txn_value = last_close * last_vol 
            stats.append({"Ticker": symbol, "Last Close": last_close, "Volume (Hari Ini)": last_vol, "Avg Volume (1 Week)": avg_vol_1w, "Est. Value (IDR)": txn_value})
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
            df = data[t] if len(tickers) > 1 else data
            if df.empty: continue
            df = df.sort_index()
            curr = df['Close'].iloc[-1]
            def calc_pct(days_ago):
                if len(df) > days_ago:
                    prev = df['Close'].iloc[-(days_ago+1)]
                    return ((curr - prev) / prev) * 100
                return 0.0
            perf_list.append({"Ticker": t, "Price": curr, "1D %": calc_pct(1), "1W %": calc_pct(5), "1M %": calc_pct(20)})
        except: continue
    return pd.DataFrame(perf_list)

# --- VISUALISASI ---
def create_stock_grid(tickers, chart_data):
    if not tickers: return None
    rows = math.ceil(len(tickers) / 4)
    vertical_spacing = min(0.08, 0.2 / (rows - 1)) if rows > 1 else 0.1
    fig = make_subplots(rows=rows, cols=4, subplot_titles=tickers, vertical_spacing=vertical_spacing, horizontal_spacing=0.03)
    one_month_ago = datetime.now() - timedelta(days=30)

    for i, ticker in enumerate(tickers):
        row, col = (i // 4) + 1, (i % 4) + 1
        try: df = chart_data[ticker] if len(tickers) > 1 else chart_data
        except: continue
        if df.empty or 'Close' not in df.columns: continue
        df = df.dropna()
        if len(df) < 2: continue
        
        last_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        color = '#00C805' if float(last_p) >= float(prev_p) else '#FF333A'
        
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=color, width=1.5), name=ticker), row=row, col=col)
        fig.add_vline(x=one_month_ago.timestamp() * 1000, line_width=1, line_dash="dot", line_color="blue", row=row, col=col)
        fig.update_xaxes(showticklabels=False, row=row, col=col)
        fig.update_yaxes(showticklabels=False, row=row, col=col)
    fig.update_layout(height=max(300, rows * 180), showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    return fig

def create_detail_chart(df, ticker):
    """Membuat Candlestick Chart dengan Volume"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", showlegend=False), row=1, col=1)
    if len(df) > 20:
        ma20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df['Date'], y=ma20, line=dict(color='orange', width=1), name="MA 20"), row=1, col=1)
    colors = ['#00C805' if row['Close'] >= row['Open'] else '#FF333A' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
    fig.update_layout(title=f"Analisa Teknikal: {ticker}", yaxis_title="Harga", xaxis_rangeslider_visible=False, hovermode="x unified", height=600)
    return fig

# --- 5. MAIN UI ---
st.title("📈 Super Stock Dashboard")

default_tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK"] * 4 

# TABS LENGKAP 1-6
tab_grid, tab_vol, tab_sector, tab_watch, tab_detail, tab_cycle = st.tabs([
    "📊 Grid View", "🔊 Top Volume", "🏢 Sector Gain", "⭐ Watchlist", "🔎 Analisa Detail", "🔄 Feature Cycle"
])

# === TAB 1: GRID ===
with tab_grid:
    st.write("Grid Overview")
    if 'page' not in st.session_state: st.session_state.page = 1
    items_per_page = 20
    c1, _ = st.columns([1, 5])
    curr_page = c1.number_input("Halaman", 1, math.ceil(len(default_tickers)/items_per_page), key="grid_page")
    start, end = (curr_page - 1) * items_per_page, (curr_page - 1) * items_per_page + items_per_page
    batch = default_tickers[start:end]

    with st.spinner("Memuat grafik..."):
        data_grid = get_stock_history_bulk(batch)
        if not data_grid.empty:
            fig_main = create_stock_grid(batch, data_grid)
            st.plotly_chart(fig_main, use_container_width=True)

# === TAB 2: VOLUME ===
with tab_vol:
    st.header("Analisis Volume")
    DEFAULT_VOL = ["GOTO.JK", "BBRI.JK", "BUMI.JK", "ANTM.JK", "DEWA.JK"]
    c_in, c_add, c_rst = st.columns([3, 1, 1])
    with c_in: n_vol = st.text_input("Tambah:", placeholder="ADRO.JK", key="v_in").strip().upper()
    with c_add: 
        st.write(""); st.write("") 
        if st.button("➕", key="b_av"): 
            if n_vol and n_vol not in st.session_state.vol_watchlist: 
                st.session_state.vol_watchlist.append(n_vol); save_data(); st.rerun()
    with c_rst:
        st.write(""); st.write("")
        if st.button("🔄", key="b_rv"): st.session_state.vol_watchlist = DEFAULT_VOL; save_data(); st.rerun()

    ed_vol = st.multiselect("List:", options=st.session_state.vol_watchlist, default=st.session_state.vol_watchlist, key="ms_v", label_visibility="collapsed")
    if len(ed_vol) != len(st.session_state.vol_watchlist): st.session_state.vol_watchlist = ed_vol; save_data(); st.rerun()
    
    if st.session_state.vol_watchlist:
        with st.spinner("Load..."):
            df_v = get_stock_volume_stats(",".join(st.session_state.vol_watchlist))
            if df_v is not None and not df_v.empty:
                sc = st.radio("Urutkan:", ["Volume (Hari Ini)", "Avg Volume (1 Week)", "Est. Value (IDR)"], horizontal=True)
                st.dataframe(df_v.sort_values(by=sc, ascending=False).style.format({"Last Close": "{:,.0f}", "Volume (Hari Ini)": "{:,.0f}", "Avg Volume (1 Week)": "{:,.0f}", "Est. Value (IDR)": "Rp {:,.0f}"}), use_container_width=True)

# === TAB 3: SECTOR ===
with tab_sector:
    sec = st.selectbox("Sektor:", list(SECTOR_MAP.keys()))
    if sec:
        with st.spinner("Load..."):
            df_s = get_sector_performance(sec)
            if not df_s.empty:
                st.dataframe(df_s.style.applymap(lambda v: f'background-color: {"#d4f7d4" if v>0 else "#f7d4d4" if v<0 else ""}', subset=['1D %', '1W %', '1M %']).format({"Price": "{:,.0f}", "1D %": "{:+.2f}%", "1W %": "{:+.2f}%", "1M %": "{:+.2f}%"}), use_container_width=True)

# === TAB 4: WATCHLIST ===
with tab_watch:
    st.header("Watchlist Saya")
    ci, cb = st.columns([3, 1])
    with ci: nt = st.text_input("Kode:", key="sb").strip().upper()
    with cb: 
        st.write(""); st.write("")
        if st.button("➕ Tambah"): 
            if nt and nt not in st.session_state.watchlist: st.session_state.watchlist.append(nt); save_data(); st.rerun()
    
    cw = st.session_state.watchlist
    if cw:
        if st.button("🗑️ Hapus Semua"): st.session_state.watchlist = []; save_data(); st.rerun()
        ew = st.multiselect("Edit:", options=cw, default=cw)
        if len(ew) != len(cw): st.session_state.watchlist = ew; save_data(); st.rerun()
        with st.spinner("Load..."):
            dw = get_stock_history_bulk(cw)
            if not dw.empty: 
                fw = create_stock_grid(cw, dw)
                if fw: st.plotly_chart(fw, use_container_width=True)

# === TAB 5: ANALISA DETAIL ===
with tab_detail:
    st.header("🔎 Analisa Saham Mendalam")
    st.write("Lihat grafik lengkap dengan candlestick, volume, dan rentang waktu bebas.")
    col_search, col_period = st.columns([2, 3])
    with col_search:
        # Panggil elemen pertama dari watchlist jika ada
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input("Ketik Kode Saham:", value=default_ticker, key="detail_input").strip().upper()
    with col_period:
        period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        period_labels = {"1mo": "1 Bulan", "3mo": "3 Bulan", "6mo": "6 Bulan", "1y": "1 Tahun", "2y": "2 Tahun", "5y": "5 Tahun", "max": "Sejak IPO"}
        selected_period_code = st.select_slider("Pilih Rentang Waktu:", options=period_options, value="1y", format_func=lambda x: period_labels[x])

    st.divider()
    if detail_ticker:
        with st.spinner(f"Mengambil data {detail_ticker}..."):
            # === FUNGSI INI SEKARANG SUDAH ADA ===
            df_detail = get_single_stock_detail(detail_ticker, selected_period_code)
            
            if df_detail is not None and not df_detail.empty:
                fig_detail = create_detail_chart(df_detail, detail_ticker)
                st.plotly_chart(fig_detail, use_container_width=True)
                last_row = df_detail.iloc[-1]
                prev_row = df_detail.iloc[-2] if len(df_detail) > 1 else last_row
                change = last_row['Close'] - prev_row['Close']
                pct_change = (change / prev_row['Close']) * 100
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Harga", f"{last_row['Close']:,.0f}")
                c2.metric("Perubahan", f"{change:,.0f}", f"{pct_change:.2f}%")
                c3.metric("Volume", f"{last_row['Volume']:,.0f}")
                c4.metric("High", f"{df_detail['High'].max():,.0f}")
            else: st.error("Data tidak ditemukan.")

