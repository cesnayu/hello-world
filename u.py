import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

# --- 2. INISIALISASI SESSION STATE (PENTING UNTUK BOOKMARK) ---
if 'watchlist' not in st.session_state:
    # Default watchlist awal (bisa kosong [])
    st.session_state.watchlist = ["BBCA.JK", "GOTO.JK", "BBRI.JK"]

# --- 3. DATA MAPPING (SEKTOR) ---
SECTOR_MAP = {
    "Banking (Finance)": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BBTN.JK", "ARTO.JK"],
    "Energy & Mining": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "MDKA.JK", "ANTM.JK", "INCO.JK", "BUMI.JK"],
    "Telco & Tech": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK", "BUKA.JK", "EMTK.JK"],
    "Consumer Goods": ["ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "GGRM.JK", "HMSP.JK", "KLBF.JK"],
    "Infrastructure & Auto": ["ASII.JK", "JSMR.JK", "UNTR.JK", "SMGR.JK", "INTP.JK"]
}

# --- 4. FUNGSI LOAD DATA (CACHED) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    """Mengambil history harga untuk Grid Chart."""
    if not tickers:
        return pd.DataFrame()
    # Download data
    data = yf.download(tickers, period=period, group_by='ticker', progress=False)
    return data

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_str):
    """Mengambil data volume & value transaksi."""
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
            
            stats.append({
                "Ticker": symbol,
                "Last Close": last_close,
                "Volume (Hari Ini)": last_vol,
                "Avg Volume (1 Week)": avg_vol_1w,
                "Est. Value (IDR)": txn_value
            })
        except Exception:
            continue
            
    return pd.DataFrame(stats)

@st.cache_data(ttl=600)
def get_sector_performance(sector_name):
    """Hitung gain sektor."""
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

            perf_list.append({
                "Ticker": t,
                "Price": curr,
                "1D %": calc_pct(1),
                "1W %": calc_pct(5),
                "1M %": calc_pct(20)
            })
        except Exception:
            continue
    return pd.DataFrame(perf_list)

# --- 5. FUNGSI VISUALISASI GRID (DIGUNAKAN DI TAB 1 & 4) ---
def create_stock_grid(tickers, chart_data):
    if not tickers: return None
    
    rows = math.ceil(len(tickers) / 4)
    
    # Logic Spacing Dinamis
    if rows > 1:
        calc_spacing = 0.2 / (rows - 1)
        vertical_spacing = min(0.08, calc_spacing)
    else:
        vertical_spacing = 0.1
    
    fig = make_subplots(
        rows=rows, cols=4, 
        subplot_titles=tickers,
        vertical_spacing=vertical_spacing,
        horizontal_spacing=0.03
    )

    one_month_ago = datetime.now() - timedelta(days=30)

    for i, ticker in enumerate(tickers):
        row = (i // 4) + 1
        col = (i % 4) + 1

        try:
            df = chart_data[ticker] if len(tickers) > 1 else chart_data
        except KeyError: continue

        if df.empty or 'Close' not in df.columns: continue
        df = df.dropna()
        if len(df) < 2: continue

        # Warna Chart
        last_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        color = '#00C805' if float(last_p) >= float(prev_p) else '#FF333A'

        fig.add_trace(
            go.Scatter(x=df.index, y=df['Close'], mode='lines',
                       line=dict(color=color, width=1.5), name=ticker),
            row=row, col=col
        )
        
        # Garis 1 Bulan Lalu
        fig.add_vline(x=one_month_ago.timestamp() * 1000, 
                      line_width=1, line_dash="dot", line_color="blue", row=row, col=col)
        
        fig.update_xaxes(showticklabels=False, row=row, col=col)
        fig.update_yaxes(showticklabels=False, row=row, col=col)

    fig.update_layout(height=max(300, rows * 180), showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# --- 6. MAIN UI & TABS ---
st.title("📈 All-in-One Stock Dashboard")

# List Default untuk Tab Grid
default_tickers = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK",
    "GOTO.JK", "BUKA.JK", "ANTM.JK", "PGAS.JK", "PTBA.JK", "INKP.JK", "CPIN.JK", "BRPT.JK",
    "AMRT.JK", "MDKA.JK", "UNTR.JK", "SMGR.JK", "INTP.JK", "TPIA.JK", "KLBF.JK", "INDF.JK",
    "AAPL", "MSFT", "TSLA", "NVDA"
] * 4 

# UPDATE TABS: Tab 4 diganti Search & Watchlist
tab_grid, tab_vol, tab_sector, tab_search = st.tabs([
    "📊 Chart Grid", 
    "🔊 Top Volume", 
    "🏢 Sector Gain", 
    "🔍 Search & Watchlist"
])

# === TAB 1: CHART GRID (PAGINATION) ===
with tab_grid:
    st.write("Grid Overview (All Stocks)")
    if 'page' not in st.session_state: st.session_state.page = 1
    items_per_page = 20
    total_pages = math.ceil(len(default_tickers) / items_per_page)
    
    c1, _ = st.columns([1, 5])
    curr_page = c1.number_input("Halaman", 1, total_pages, key="grid_page")
    
    start = (curr_page - 1) * items_per_page
    end = start + items_per_page
    batch = default_tickers[start:end]

    with st.spinner("Memuat grafik..."):
        data_grid = get_stock_history_bulk(batch)
        if not data_grid.empty:
            fig_main = create_stock_grid(batch, data_grid)
            if fig_main:
                st.plotly_chart(fig_main, use_container_width=True)

# === TAB 2: TOP VOLUME ===
with tab_vol:
    st.header("Analisis Volume & Likuiditas")
    user_vol = st.text_area("Input Ticker:", "GOTO.JK, BBRI.JK, BUMI.JK, ANTM.JK", height=70, key="vol_input")
    
    if user_vol:
        with st.spinner("Mengambil data volume..."):
            df_vol = get_stock_volume_stats(user_vol)
            if df_vol is not None and not df_vol.empty:
                sort_col = st.radio("Urutkan:", 
                                    ["Volume (Hari Ini)", "Avg Volume (1 Week)", "Est. Value (IDR)"], 
                                    horizontal=True)
                df_sorted = df_vol.sort_values(by=sort_col, ascending=False)
                st.dataframe(
                    df_sorted.style.format({
                        "Last Close": "{:,.0f}",
                        "Volume (Hari Ini)": "{:,.0f}",
                        "Avg Volume (1 Week)": "{:,.0f}",
                        "Est. Value (IDR)": "Rp {:,.0f}"
                    }), use_container_width=True
                )

# === TAB 3: SECTOR GAIN ===
with tab_sector:
    st.header("Performa Sektoral")
    chosen_sector = st.selectbox("Pilih Sektor:", list(SECTOR_MAP.keys()))
    
    if chosen_sector:
        with st.spinner("Analisa sektor..."):
            df_sec = get_sector_performance(chosen_sector)
            if not df_sec.empty:
                def color_scale(val):
                    color = '#d4f7d4' if val > 0 else '#f7d4d4' if val < 0 else ''
                    return f'background-color: {color}'

                st.dataframe(
                    df_sec.style.applymap(color_scale, subset=['1D %', '1W %', '1M %'])
                                .format({"Price": "{:,.0f}", "1D %": "{:+.2f}%", "1W %": "{:+.2f}%", "1M %": "{:+.2f}%"}),
                    use_container_width=True
                )

# === TAB 4: SEARCH & WATCHLIST (NEW) ===
with tab_search:
    st.header("🔍 Pencarian & Watchlist Saya")
    st.write("Cari saham dan tambahkan ke daftar pantauan. Data ini tidak akan hilang saat pindah tab.")

    # 1. INPUT SECTION
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        new_ticker = st.text_input("Ketik Kode Saham (contoh: UNTR.JK, AAPL)", key="search_box").strip().upper()
    with col_btn:
        st.write("") # Spacer agar tombol sejajar
        st.write("")
        add_btn = st.button("➕ Tambahkan ke Watchlist")

    # Logic Tambah Saham
    if add_btn and new_ticker:
        # Validasi sederhana agar tidak duplikat
        if new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            st.success(f"Saham {new_ticker} berhasil ditambahkan!")
            st.rerun() # Refresh halaman agar grid update
        else:
            st.warning(f"{new_ticker} sudah ada di watchlist.")

    st.divider()

    # 2. DISPLAY WATCHLIST SECTION
    current_watchlist = st.session_state.watchlist

    if not current_watchlist:
        st.info("Watchlist kamu masih kosong. Silakan tambahkan saham di atas.")
    else:
        # Tombol Hapus / Reset
        if st.button("🗑️ Hapus Semua Watchlist"):
            st.session_state.watchlist = []
            st.rerun()
        
        st.subheader(f"Daftar Pantauan ({len(current_watchlist)} Saham)")
        
        # Menggunakan Fungsi Grid yang SAMA dengan Tab 1
        with st.spinner("Memuat grafik watchlist..."):
            # Kita paksa ambil data baru khusus watchlist (cache terpisah dgn grid utama jika mau)
            # Tapi kita pakai fungsi yg sama 'get_stock_history_bulk' jadi tetap efisien
            data_watch = get_stock_history_bulk(current_watchlist)
            
            if not data_watch.empty:
                fig_watch = create_stock_grid(current_watchlist, data_watch)
                if fig_watch:
                    st.plotly_chart(fig_watch, use_container_width=True)
            else:
                st.error("Gagal mengambil data untuk watchlist. Cek kembali kode saham.")
