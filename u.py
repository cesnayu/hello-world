import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px  # Penting untuk Box Plot & Bar Chart
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

# --- 2. DATA MAPPING (SEKTOR) ---
# Mapping manual karena yfinance tidak menyediakan list sektor IHSG yang rapi gratis
SECTOR_MAP = {
    "Banking (Finance)": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BBTN.JK", "ARTO.JK"],
    "Energy & Mining": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "MDKA.JK", "ANTM.JK", "INCO.JK", "BUMI.JK"],
    "Telco & Tech": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK", "BUKA.JK", "EMTK.JK"],
    "Consumer Goods": ["ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "GGRM.JK", "HMSP.JK", "KLBF.JK"],
    "Infrastructure & Auto": ["ASII.JK", "JSMR.JK", "UNTR.JK", "SMGR.JK", "INTP.JK"]
}

# --- 3. FUNGSI LOAD DATA (CACHED) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    """Mengambil history harga untuk Grid Chart."""
    if not tickers:
        return pd.DataFrame()
    data = yf.download(tickers, period=period, group_by='ticker', progress=False)
    return data

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_str):
    """Mengambil data volume & value transaksi."""
    if not tickers_str: return None
    
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not ticker_list: return None

    # Ambil data 1 bulan untuk hitung rata-rata
    data = yf.download(ticker_list, period="1mo", group_by='ticker', progress=False)
    
    stats = []
    for t in ticker_list:
        try:
            # Handle struktur data (Single vs Multi Index)
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
            txn_value = last_close * last_vol # Estimasi Value Transaksi
            
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
    """Hitung gain sektor (1D, 1W, 1M)."""
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

@st.cache_data(ttl=300)
def get_volatility_data(tickers_str):
    """Mengambil data risiko & volatilitas."""
    if not tickers_str: return None, None
    
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not ticker_list: return None, None

    data = yf.download(ticker_list, period="1mo", group_by='ticker', progress=False)
    
    combined_returns = pd.DataFrame()
    summary_stats = []

    for t in ticker_list:
        try:
            if len(ticker_list) == 1:
                df = data
                symbol = ticker_list[0]
            else:
                df = data[t]
                symbol = t
            
            if df.empty: continue
            
            # Pakai Adj Close jika ada, kalau tidak Close
            col_price = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            daily_pct = df[col_price].pct_change() * 100
            daily_pct = daily_pct.dropna()
            
            # Data untuk Box Plot
            temp_df = pd.DataFrame({
                'Ticker': symbol, 
                'Daily Return %': daily_pct.values
            })
            combined_returns = pd.concat([combined_returns, temp_df])

            # Statistik
            high_low_pct = ((df['High'] - df['Low']) / df['Open'] * 100).mean()
            
            summary_stats.append({
                "Ticker": symbol,
                "Volatilitas (Std Dev)": daily_pct.std(),
                "Rata2 Range Harian (%)": high_low_pct,
                "Max Kenaikan 1 Hari (%)": daily_pct.max(),
                "Max Penurunan 1 Hari (%)": daily_pct.min()
            })
        except Exception:
            continue
            
    return combined_returns, pd.DataFrame(summary_stats)

# --- 4. VISUALISASI GRID (FIXED SPACING) ---
def create_stock_grid(tickers, chart_data):
    if not tickers: return None
    
    rows = math.ceil(len(tickers) / 4)
    
    # Logic Spacing Dinamis (Mencegah Error ValueError)
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

# --- 5. MAIN UI & TABS ---
st.title("📈 All-in-One Stock Dashboard")

# List Default untuk Tab Grid
default_tickers = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK",
    "GOTO.JK", "BUKA.JK", "ANTM.JK", "PGAS.JK", "PTBA.JK", "INKP.JK", "CPIN.JK", "BRPT.JK",
    "AMRT.JK", "MDKA.JK", "UNTR.JK", "SMGR.JK", "INTP.JK", "TPIA.JK", "KLBF.JK", "INDF.JK",
    "AAPL", "MSFT", "TSLA", "NVDA"
] * 4 # Duplikasi agar pagination terlihat

# Tab Layout
tab_grid, tab_vol, tab_sector, tab_risk = st.tabs([
    "📊 Chart Grid", 
    "🔊 Top Volume", 
    "🏢 Sector Gain", 
    "⚡ Analisa Risiko"
])

# === TAB 1: CHART GRID (PAGINATION) ===
with tab_grid:
    st.write("Grid Overview (Close Price)")
    
    # Pagination
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
    st.write("Input kode saham (pisahkan koma) untuk membandingkan.")
    
    user_vol = st.text_area("Input Ticker:", "GOTO.JK, BBRI.JK, BUMI.JK, ANTM.JK", height=70, key="vol_input")
    
    if user_vol:
        with st.spinner("Mengambil data volume..."):
            df_vol = get_stock_volume_stats(user_vol)
            if df_vol is not None and not df_vol.empty:
                sort_col = st.radio("Urutkan:", 
                                    ["Volume (Hari Ini)", "Avg Volume (1 Week)", "Est. Value (IDR)"], 
                                    horizontal=True)
                
                # Sorting Numerik
                df_sorted = df_vol.sort_values(by=sort_col, ascending=False)
                
                st.dataframe(
                    df_sorted.style.format({
                        "Last Close": "{:,.0f}",
                        "Volume (Hari Ini)": "{:,.0f}",
                        "Avg Volume (1 Week)": "{:,.0f}",
                        "Est. Value (IDR)": "Rp {:,.0f}"
                    }), use_container_width=True
                )
            else:
                st.warning("Data tidak ditemukan.")

# === TAB 3: SECTOR GAIN ===
with tab_sector:
    st.header("Performa Sektoral")
    chosen_sector = st.selectbox("Pilih Sektor:", list(SECTOR_MAP.keys()))
    
    if chosen_sector:
        with st.spinner("Analisa sektor..."):
            df_sec = get_sector_performance(chosen_sector)
            if not df_sec.empty:
                # Coloring Logic
                def color_scale(val):
                    color = '#d4f7d4' if val > 0 else '#f7d4d4' if val < 0 else ''
                    return f'background-color: {color}'

                st.dataframe(
                    df_sec.style.applymap(color_scale, subset=['1D %', '1W %', '1M %'])
                                .format({"Price": "{:,.0f}", "1D %": "{:+.2f}%", "1W %": "{:+.2f}%", "1M %": "{:+.2f}%"}),
                    use_container_width=True
                )

# === TAB 4: RISK ANALYSIS ===
with tab_risk:
    st.header("⚡ Analisa Volatilitas & Risiko (1 Bulan)")
    risk_input = st.text_area("Input Ticker:", "GOTO.JK, BBRI.JK, BREN.JK, UNVR.JK", key="risk_in")
    
    st.write("---")
    threshold = st.slider("Cari yg pernah gerak ekstrem lebih dari (%):", 5, 25, 10)
    
    if risk_input:
        with st.spinner("Menghitung risiko..."):
            df_ret, df_summ = get_volatility_data(risk_input)
            
            if df_summ is not None and not df_summ.empty:
                # 1. Alert Extreme Move
                extreme = df_summ[
                    (df_summ['Max Kenaikan 1 Hari (%)'] >= threshold) | 
                    (df_summ['Max Penurunan 1 Hari (%)'] <= -threshold)
                ]
                if not extreme.empty:
                    st.error(f"⚠️ PERHATIAN: Saham ini bergerak > {threshold}% dalam sehari bulan ini:")
                    st.dataframe(extreme[['Ticker', 'Max Kenaikan 1 Hari (%)', 'Max Penurunan 1 Hari (%)']], hide_index=True)
                else:
                    st.success("✅ Aman: Tidak ada pergerakan ekstrem di atas threshold.")

                # 2. Box Plot
                st.subheader("1. Sebaran Return Harian (Box Plot)")
                fig_box = px.box(df_ret, x="Ticker", y="Daily Return %", color="Ticker", points="all")
                st.plotly_chart(fig_box, use_container_width=True)

                # 3. Bar Chart Range
                st.subheader("2. Rata-rata Range Harian (High - Low)")
                df_summ_sorted = df_summ.sort_values(by="Rata2 Range Harian (%)", ascending=False)
                fig_bar = px.bar(df_summ_sorted, x="Ticker", y="Rata2 Range Harian (%)", 
                                 color="Rata2 Range Harian (%)", color_continuous_scale="Reds", text_auto='.2f')
                st.plotly_chart(fig_bar, use_container_width=True)
