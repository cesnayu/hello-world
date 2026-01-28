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
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
        return df
    except: return None

@st.cache_data(ttl=600)
def get_seasonal_details(tickers_str, start_month, end_month, lookback_years=5):
    """
    FIXED: Loop mulai dari 0 (Current Year Included) dan handle partial data.
    """
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    
    # Ambil data buffer extra panjang
    start_date = datetime.now() - timedelta(days=(lookback_years + 2) * 365)
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=False)
    
    results = {} 

    for ticker in ticker_list:
        try:
            if len(ticker_list) == 1: df = data; symbol = ticker_list[0]
            else: df = data[ticker]; symbol = ticker
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            
            stock_years_data = {}
            current_year = datetime.now().year
            
            # === PERBAIKAN LOGIC DI SINI ===
            # Loop dari 0 agar tahun ini (yang belum selesai) ikut terhitung
            for i in range(0, lookback_years + 1):
                y_end = current_year - i
                
                # Logic Cross Year (Misal Nov ke Apr)
                if int(start_month) > int(end_month):
                    # Nov 2025 (start) -> Apr 2026 (end)
                    y_start = y_end - 1 
                else:
                    # Jun 2026 (start) -> Agust 2026 (end)
                    y_start = y_end

                try:
                    d_start = datetime(y_start, int(start_month), 1)
                    
                    # Cek: Jika tanggal mulai cycle ini masih di masa depan, skip.
                    # Contoh: Sekarang Jan 2026. User minta Juni-Agust.
                    # Loop 0 akan cek Juni 2026. Ini belum terjadi -> Skip.
                    if d_start > datetime.now():
                        continue

                    # Tanggal akhir (handle tanggal 28 agar aman di Feb)
                    d_end = datetime(y_end, int(end_month), 28) 
                    
                    label = f"{y_start}/{y_end}" if int(start_month) > int(end_month) else f"{y_end}"
                except: continue
                
                # Filter Data
                # Walaupun d_end Apr 2026 (masa depan), pandas akan filter data yang ada saja (sampai Jan 2026)
                mask = (df['Date'] >= d_start) & (df['Date'] <= d_end)
                df_period = df.loc[mask].copy()
                
                if df_period.empty: continue
                
                # Normalisasi %
                first_price = df_period['Close'].iloc[0]
                df_period['Rel_Change'] = ((df_period['Close'] - first_price) / first_price) * 100
                
                stock_years_data[label] = df_period['Rel_Change'].reset_index(drop=True)
            
            if stock_years_data:
                results[symbol] = stock_years_data
                
        except Exception: continue
        
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
            df = data[t] if len(tickers) > 1 else data
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.sort_index()
            curr = df['Close'].iloc[-1]
            def calc_pct(d):
                if len(df) > d: return ((curr - df['Close'].iloc[-(d+1)]) / df['Close'].iloc[-(d+1)]) * 100
                return 0.0
            perf_list.append({"Ticker": t, "Price": curr, "1D %": calc_pct(1), "1W %": calc_pct(5), "1M %": calc_pct(20)})
        except: continue
    return pd.DataFrame(perf_list)

# --- 6. VISUALISASI CHART ---
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
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", showlegend=False), row=1, col=1)
    if len(df) > 20: fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), name="MA 20"), row=1, col=1)
    colors = ['#00C805' if c >= o else '#FF333A' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
    fig.update_layout(title=f"Analisa Teknikal: {ticker}", yaxis_title="Harga", xaxis_rangeslider_visible=False, hovermode="x unified", height=600)
    return fig

# --- 7. MAIN UI ---
st.title("📈 Super Stock Dashboard")
default_tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK"] * 4 

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
            fig = create_stock_grid(batch, data_grid)
            st.plotly_chart(fig, use_container_width=True)

# === TAB 2: VOLUME ===
with tab_vol:
    st.header("Analisis Volume")
    DEFAULT_VOL = ["GOTO.JK", "BBRI.JK", "BUMI.JK", "ANTM.JK", "DEWA.JK"]
    c_in, c_add, c_rst = st.columns([3, 1, 1])
    with c_in: n_vol = st.text_input("Tambah:", placeholder="ADRO.JK", key="v_in").strip().upper()
    with c_add: 
        st.write(""); st.write("") 
        if st.button("➕", key="b_av"): 
            if n_vol and n_vol not in st.session_state.vol_watchlist: st.session_state.vol_watchlist.append(n_vol); save_data(); st.rerun()
    with c_rst:
        st.write(""); st.write("")
        if st.button("🔄", key="b_rv"): st.session_state.vol_watchlist = DEFAULT_VOL; save_data(); st.rerun()
    ed_vol = st.multiselect("List:", options=st.session_state.vol_watchlist, default=st.session_state.vol_watchlist, key="ms_v", label_visibility="collapsed")
    if len(ed_vol) != len(st.session_state.vol_watchlist): st.session_state.vol_watchlist = ed_vol; save_data(); st.rerun()
    if st.session_state.vol_watchlist:
        with st.spinner("Load..."):
            df_v = get_stock_volume_stats(",".join(st.session_state.vol_watchlist))
            if df_v is not None and not df_v.empty:
                sc = st.radio("Urutkan:", ["Volume", "Avg Vol", "Est. Val"], horizontal=True)
                st.dataframe(df_v.sort_values(by=sc, ascending=False).style.format({"Last Close": "{:,.0f}", "Volume": "{:,.0f}", "Avg Vol": "{:,.0f}", "Est. Val": "Rp {:,.0f}"}), use_container_width=True)

# === TAB 3: SECTOR ===
with tab_sector:
    sec = st.selectbox("Sektor:", list(SECTOR_MAP.keys()))
    if sec:
        with st.spinner("Load..."):
            df_s = get_sector_performance(sec)
            if not df_s.empty: st.dataframe(df_s.style.applymap(lambda v: f'background-color: {"#d4f7d4" if v>0 else "#f7d4d4" if v<0 else ""}', subset=['1D %', '1W %', '1M %']).format({"Price": "{:,.0f}", "1D %": "{:+.2f}%", "1W %": "{:+.2f}%", "1M %": "{:+.2f}%"}), use_container_width=True)

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

# === TAB 5: DETAIL ===
with tab_detail:
    st.header("🔎 Analisa Saham Mendalam")
    col_search, col_period = st.columns([2, 3])
    with col_search:
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input("Ketik Kode Saham:", value=default_ticker, key="detail_input").strip().upper()
    with col_period:
        period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        selected_period_code = st.select_slider("Pilih Rentang Waktu:", options=period_options, value="1y")
    st.divider()
    if detail_ticker:
        with st.spinner(f"Mengambil data {detail_ticker}..."):
            df_detail = get_single_stock_detail(detail_ticker, selected_period_code)
            if df_detail is not None and not df_detail.empty:
                st.plotly_chart(create_detail_chart(df_detail, detail_ticker), use_container_width=True)
                last = df_detail.iloc[-1]; prev = df_detail.iloc[-2]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Harga", f"{last['Close']:,.0f}")
                c2.metric("Change", f"{last['Close']-prev['Close']:,.0f}", f"{(last['Close']-prev['Close'])/prev['Close']*100:.2f}%")
                c3.metric("Volume", f"{last['Volume']:,.0f}")
                c4.metric("High", f"{df_detail['High'].max():,.0f}")
            else: st.error("Data tidak ditemukan.")

# === TAB 6: FEATURE CYCLE (REVISI - CURRENT YEAR FIX) ===
with tab_cycle:
    st.header("🔄 Cycle Analysis (Year over Year)")
    st.write("Membandingkan pergerakan harga saham pada bulan yang sama di tahun-tahun berbeda.")
    
    # Input
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        def_t = ", ".join(st.session_state.watchlist[:2]) if st.session_state.watchlist else "GOTO.JK, BBCA.JK"
        cycle_tickers = st.text_input("Saham (Pisahkan koma):", value=def_t, key="cycle_in").strip().upper()
    with c2:
        month_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"Mei", 6:"Jun", 7:"Jul", 8:"Agust", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Des"}
        start_m = st.selectbox("Dari Bulan:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=10) # Nov
        end_m = st.selectbox("Sampai Bulan:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=3) # Apr
    with c3:
        years_lookback = st.slider("Tarik Data Berapa Tahun?", 3, 10, 5)
        st.write("")
        btn_cycle = st.button("🚀 Bandingkan")

    st.divider()
    
    if btn_cycle and cycle_tickers:
        with st.spinner("Menganalisa..."):
            # Panggil fungsi yang sudah diperbarui
            results_dict = get_seasonal_details(cycle_tickers, start_m, end_m, years_lookback)
            
            if results_dict:
                cols = st.columns(2)
                # ... (kode sebelumnya di dalam tab_cycle) ...
                
                # Loop setiap saham
                for idx, (ticker, years_data) in enumerate(results_dict.items()):
                    with cols[idx % 2]:
                        fig = go.Figure()
                        
                        sorted_years = sorted(years_data.keys(), reverse=True)
                        
                        # --- DEFINISI WARNA: HITAM, BIRU, MERAH, HIJAU ---
                        # Kamu bisa pakai nama warna Inggris atau Kode Hex
                        # Urutan: Tahun Terbaru -> Hitam, Tahun sblmnya -> Biru, dst.
                        my_colors = ['black', 'blue', 'red', 'green','yellow'] 
                        
                        for i, year_label in enumerate(sorted_years):
                            series = years_data[year_label]
                            
                            # Pilih warna secara bergantian (Cycle)
                            # Jika tahun ke-5, dia akan kembali ke warna pertama (Hitam)
                            chosen_color = my_colors[i % len(my_colors)]
                            
                            # Cek apakah ini tahun berjalan (Current Year)?
                            is_current_year = str(datetime.now().year) in year_label
                            
                            # Opsional: Jika tahun ini, garis lebih tebal biar spesial
                            line_width = 3 if is_current_year else 1.5
                            
                            fig.add_trace(go.Scatter(
                                y=series, 
                                mode='lines', 
                                name=year_label,
                                line=dict(color=chosen_color, width=line_width), # <--- Pakai warna pilihan
                                hovertemplate=f"<b>{year_label}</b><br>Hari ke-%{{x}}<br>Return: %{{y:.2f}}%<extra></extra>"
                            ))
                        
                        # ... (sisa kode layout fig.update_layout sama seperti sebelumnya) ...
                        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                        fig.update_layout(
                            title=f"<b>{ticker}</b>: {month_map[start_m]} - {month_map[end_m]}",
                            xaxis_title="Hari ke-n", yaxis_title="Gain/Loss (%)",
                            hovermode="x unified", height=400,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Data tidak cukup atau kode saham salah.")
