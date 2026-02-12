import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os
import pytz 

# --- 1. KONFIGURASI HALAMAN & WAKTU ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard Pro")

# Definisi Waktu Global (Mencegah NameError)
today = datetime.now()
end_date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
start_of_week = today - timedelta(days=today.weekday())
days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

DB_FILE = "stock_database.json"

# --- 2. DATA STATIC (LIST SAHAM IHSG) ---
LIST_SAHAM_IHSG = [
    "BREN.JK", "BBCA.JK", "DSSA.JK", "BBRI.JK", "TPIA.JK", "DCII.JK", "BYAN.JK", "AMMN.JK", "BMRI.JK", "TLKM.JK", 
    "ASII.JK", "MORA.JK", "SRAJ.JK", "CUAN.JK", "BRPT.JK", "BBNI.JK", "PANI.JK", "BNLI.JK", "BRMS.JK", "GOTO.JK",
    "ADRO.JK", "KLBF.JK", "ANTM.JK", "BUMI.JK", "ASRI.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "CPIN.JK", "AKRA.JK",
    "JSMR.JK", "PTBA.JK", "ITMG.JK", "UNTR.JK", "ADMR.JK", "INKP.JK", "MEDC.JK", "PGAS.JK", "EXCL.JK", "ISAT.JK"
] # Daftar ini bisa kamu teruskan sesuai kebutuhan

# --- 3. FUNGSI DATABASE (JSON) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "picked_stocks": st.session_state.get("picked_stocks", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 4. INISIALISASI SESSION STATE ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]
if 'picked_stocks' not in st.session_state:
    st.session_state.picked_stocks = []
if 'grid_page' not in st.session_state:
    st.session_state.grid_page = 1

# --- 5. FUNGSI BACKEND (CACHING) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo", interval="1d"):
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False)
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def get_weekly_recap_data(tickers):
    start_date = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
    data = yf.download(tickers, start=start_date, group_by="ticker", progress=False)
    all_rows = []
    for t in tickers:
        try:
            df = data[t].dropna().copy() if len(tickers) > 1 else data.dropna().copy()
            if df.empty: continue
            df["Return"] = df["Close"].pct_change() * 100
            df.index = df.index.date
            row = {"Ticker": t, "Price": round(df["Close"].iloc[-1], 2), "Today (%)": round(df["Return"].iloc[-1], 2)}
            weekly_vals = []
            gain_count = 0
            for i in range(5):
                target = (start_of_week + timedelta(days=i)).date()
                if target in df.index:
                    val = df.loc[target, "Return"]
                    if isinstance(val, pd.Series): val = val.iloc[0]
                    row[days_names[i]] = round(val, 2)
                    weekly_vals.append(val)
                    if val > 0: gain_count += 1
                else: row[days_names[i]] = 0.0
            row["Weekly Acc (%)"] = round(sum(weekly_vals), 2)
            row["Win Rate"] = f"{gain_count}/5"
            all_rows.append(row)
        except: continue
    return pd.DataFrame(all_rows)

# --- 6. FUNGSI VISUALISASI ---
def create_mini_chart_complex(df, ticker, period_code):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=color_line, width=1.5), name="Price"), secondary_y=False)
    fig.update_layout(title=dict(text=ticker, font=dict(size=12), x=0.5), margin=dict(l=5, r=5, t=30, b=5), height=180, showlegend=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=8))
    return fig

def create_detail_chart(df, ticker):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='gray'), row=2, col=1)
    fig.update_layout(height=600, xaxis_rangeslider_visible=False, title=ticker)
    return fig

# --- 7. MAIN UI DASHBOARD ---
st.title("📈 Super Stock Dashboard")

# DEFINISI 10 TAB (GABUNGAN SEMUA FITUR)
tabs = st.tabs([
    "📊 Grid", "⚖️ Bandingkan", "🔊 Volume", "⭐ Watchlist", "🔎 Detail", 
    "🔄 Cycle", "📅 Weekly Recap", "🚀 Performa", "🎲 Win/Loss", "🎯 Simulator"
])

# === TAB 1: GRID OVERVIEW ===
with tabs[0]:
    st.header("📊 Market Grid")
    period_grid = st.selectbox("Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1, key="grid_tf")
    batch_tickers = LIST_SAHAM_IHSG[:16] # Tampilkan 16 pertama
    data_grid = get_stock_history_bulk(batch_tickers, period=period_grid)
    grid_cols = st.columns(4)
    for i, t in enumerate(batch_tickers):
        with grid_cols[i % 4]:
            try:
                df_g = data_grid[t].dropna() if len(batch_tickers) > 1 else data_grid.dropna()
                if not df_g.empty:
                    st.plotly_chart(create_mini_chart_complex(df_g, t, period_grid), use_container_width=True)
                    if st.checkbox(f"Pilih {t}", key=f"sel_{t}"):
                        if t not in st.session_state.picked_stocks: st.session_state.picked_stocks.append(t)
            except: pass

# === TAB 2: BANDINGKAN ===
with tabs[1]:
    st.header("⚖️ Bandingkan Pilihan")
    if st.session_state.picked_stocks:
        if st.button("Reset Pilihan"): 
            st.session_state.picked_stocks = []
            st.rerun()
        sel_data = get_stock_history_bulk(st.session_state.picked_stocks, period="6mo")
        for t in st.session_state.picked_stocks:
            df_c = sel_data[t].dropna() if len(st.session_state.picked_stocks) > 1 else sel_data.dropna()
            st.line_chart(df_c['Close'])
    else: st.warning("Pilih saham dari Tab Grid terlebih dahulu.")

# === TAB 3: VOLUME ===
with tabs[2]:
    st.header("🔊 Analisis Volume")
    v_in = st.text_area("Input Saham (koma):", value="BBCA.JK, GOTO.JK", key="vol_in")
    if st.button("Cek Volume"):
        v_list = [x.strip().upper() for x in v_in.split(",")]
        v_data = get_stock_history_bulk(v_list, period="1mo")
        # Logika ringkasan volume sederhana
        st.write("Menampilkan data volume 1 bulan terakhir...")
        st.dataframe(v_data.tail(5))

# === TAB 5: DETAIL ===
with tabs[4]:
    st.header("🔎 Detail Candlestick")
    d_input = st.text_input("Kode Saham:", value="BBCA.JK").upper()
    if st.button("Render Chart"):
        df_d = yf.download(d_input, period="1y", progress=False)
        if not df_d.empty:
            st.plotly_chart(create_detail_chart(df_d, d_input), use_container_width=True)

# === TAB 7: WEEKLY RECAP (FITUR BARU) ===
with tabs[6]:
    st.header("📅 Weekly Performance")
    with st.spinner("Calculating weekly returns..."):
        df_weekly = get_weekly_recap_data(LIST_SAHAM_IHSG[:20]) # Ambil 20 besar
        if not df_weekly.empty:
            def style_returns(val):
                if isinstance(val, (int, float)):
                    return 'color: #00ff00' if val > 0 else 'color: #ff4b4b' if val < 0 else ''
                return ''
            st.dataframe(df_weekly.style.applymap(style_returns, subset=['Today (%)', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Weekly Acc (%)']), use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("📈 Chart Explorer")
    sel_explorer = st.multiselect("Bandingkan Grafik:", options=LIST_SAHAM_IHSG, key="explorer")
    if sel_explorer:
        chart_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        c_data = yf.download(sel_explorer, start=chart_start, end=end_date_str, progress=False)
        if not c_data.empty:
            st.line_chart(c_data['Close'])

# === TAB 9: WIN/LOSS (UPDATE HARIAN) ===
with tabs[8]:
    st.header("🎲 Win/Loss Stats (30 Hari)")
    wl_in = st.text_area("Saham:", value="BBCA.JK, GOTO.JK, BBRI.JK", key="wl_input")
    if st.button("Hitung Statistik"):
        wl_list = [x.strip().upper() for x in wl_in.split(",")]
        data_wl = yf.download(wl_list, period="3mo", group_by='ticker', progress=False)
        
        for t in wl_list:
            try:
                df_wl = data_wl[t].dropna() if len(wl_list) > 1 else data_wl.dropna()
                df_wl['Change'] = df_wl['Close'].pct_change() * 100
                df_30 = df_wl.tail(30).sort_index(ascending=False)
                
                # Summary
                win_rate = (len(df_30[df_30['Change'] > 0]) / len(df_30)) * 100
                st.write(f"**{t}** | Win Rate: {win_rate:.1f}%")
                
                with st.expander(f"Tabel 30 Hari Terakhir {t}"):
                    def bg_color(val):
                        return 'background-color: #90ee90' if val > 0 else 'background-color: #ffcccb' if val < 0 else ''
                    st.dataframe(df_30[['Close', 'Change']].style.applymap(bg_color, subset=['Change']).format("{:.2f}%", subset=['Change']), use_container_width=True)
            except: pass

# (Tab Cycle, Performa, Watchlist, Simulator bisa diisi dengan logika serupa tanpa merubah struktur ini)
st.caption(f"Last Update: {today.strftime('%Y-%m-%d %H:%M:%S')} | Data by Yahoo Finance")
