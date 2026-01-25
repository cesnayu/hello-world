import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. Konfigurasi Halaman ---
st.set_page_config(layout="wide", page_title="Stock Market Dashboard")

# --- 2. Inisialisasi Session State (Untuk Bookmark) ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []

# --- 3. Fungsi Helper untuk Mengambil Data & Membuat Chart ---
@st.cache_data(ttl=300) # Cache data selama 5 menit agar tidak lambat
def get_stock_data(ticker_list):
    """
    Mengambil data saham sekaligus untuk mempercepat proses.
    """
    if not ticker_list:
        return pd.DataFrame()
    
    # Ambil data 3 bulan terakhir untuk konteks chart
    data = yf.download(ticker_list, period="3mo", group_by='ticker', progress=False)
    return data

def create_stock_grid(tickers, chart_data):
    """
    Membuat Grid Chart Plotly 4 Kolom x N Baris (FIXED: Dynamic Spacing)
    """
    if not tickers:
        st.info("Tidak ada saham untuk ditampilkan.")
        return None

    # Hitung jumlah baris yang dibutuhkan (4 kolom per baris)
    rows = math.ceil(len(tickers) / 4)
    
    # --- PERBAIKAN DI SINI ---
    # Jika baris banyak, spasi harus diperkecil agar muat.
    # Rumus: Maksimal 0.05, tapi mengecil jika rows bertambah.
    # Kita batasi total spasi agar hanya memakan max 20% dari tinggi chart.
    if rows > 1:
        calculated_spacing = 0.2 / (rows - 1) # Total gap takes 20% of height
        vertical_spacing = min(0.05, calculated_spacing) 
    else:
        vertical_spacing = 0.05
    
    # Buat Subplots
    fig = make_subplots(
        rows=rows, 
        cols=4, 
        subplot_titles=tickers,
        vertical_spacing=vertical_spacing, # Gunakan spacing dinamis
        horizontal_spacing=0.02
    )

    # Tanggal 1 bulan lalu untuk garis vertikal
    one_month_ago = datetime.now() - timedelta(days=30)

    for i, ticker in enumerate(tickers):
        # Tentukan posisi grid (row, col) - Plotly index mulai dari 1
        row = (i // 4) + 1
        col = (i % 4) + 1

        # Handling data extraction
        if len(tickers) == 1:
            df = chart_data
        else:
            try:
                # Cek jika MultiIndex (biasanya terjadi jika download >1 ticker)
                if isinstance(chart_data.columns, pd.MultiIndex):
                    df = chart_data[ticker]
                else:
                    # Fallback jika struktur data flat atau ticker cuma 1 tapi list
                    df = chart_data
            except KeyError:
                continue 

        if df.empty or 'Close' not in df.columns:
            continue

        df = df.dropna()
        if len(df) < 2: 
            continue

        # Tentukan Warna Line
        last_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        
        price_change = float(last_price) - float(prev_price)
        line_color = '#00C805' if price_change >= 0 else '#FF333A' # Warna hijau/merah cerah

        # Tambahkan Trace
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df['Close'], 
                mode='lines',
                line=dict(color=line_color, width=1.5), # Tipiskan garis sedikit
                name=ticker,
                hovertemplate=f"<b>{ticker}</b><br>Price: %{{y:.2f}}<extra></extra>"
            ),
            row=row, col=col
        )

        # Tambahkan Garis Vertikal
        fig.add_vline(
            x=one_month_ago.timestamp() * 1000, 
            line_width=1, 
            line_dash="dot", 
            line_color="blue",
            row=row, col=col
        )
        
        # Sembunyikan label X dan Y untuk kebersihan
        fig.update_xaxes(showticklabels=False, row=row, col=col)
        fig.update_yaxes(showticklabels=False, row=row, col=col)

    # Update Layout Global
    # Tinggi per row dikurangi sedikit (150px) agar tidak terlalu panjang scroll-nya
    fig.update_layout(
        height=max(400, rows * 150), 
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified"
    )
    
    return fig
# --- 4. Sidebar: Input & Bookmark Manager ---
st.sidebar.header("Pengaturan")

# Contoh List Saham (Bisa diganti dengan list CSV atau API)
# Saya masukkan campuran saham US dan Indonesia (JK) sebagai contoh
default_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK",
    "INTC", "AMD", "QCOM", "CSCO", "ORCL", "IBM", "TXN", "CRM",
    "GOTO.JK", "BUKA.JK", "KLBF.JK", "PGAS.JK", "UNTR.JK", "INKP.JK", "CPIN.JK", "BRPT.JK"
] * 4 # Saya duplikasi agar listnya panjang > 100 untuk tes pagination

# Widget Bookmark di Sidebar
st.sidebar.subheader("📌 Kelola Bookmark")
selected_bookmarks = st.sidebar.multiselect(
    "Pilih saham untuk di-pin:",
    options=list(set(default_tickers)), # Unique list
    default=st.session_state.bookmarks
)
# Update session state jika user mengubah multiselect
st.session_state.bookmarks = selected_bookmarks

# --- 5. Main UI dengan Tabs ---
st.title("📈 Market Dashboard Grid")

tab1, tab2 = st.tabs(["🏢 Semua Saham (Paged)", "⭐ Bookmark Saya"])

# --- TAB 1: Semua Saham dengan Pagination ---
with tab1:
    # Pagination Logic
    items_per_page = 100
    total_pages = math.ceil(len(default_tickers) / items_per_page)
    
    col_page, _ = st.columns([1, 4])
    with col_page:
        current_page = st.number_input("Halaman", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_batch = default_tickers[start_idx:end_idx]

    st.write(f"Menampilkan saham {start_idx+1} - {min(end_idx, len(default_tickers))} dari {len(default_tickers)}")

    if current_batch:
        with st.spinner("Mengambil data pasar..."):
            data_batch = get_stock_data(current_batch)
            fig_main = create_stock_grid(current_batch, data_batch)
            if fig_main:
                st.plotly_chart(fig_main, use_container_width=True)

# --- TAB 2: Bookmark / Watchlist ---
with tab2:
    if not st.session_state.bookmarks:
        st.warning("Belum ada saham yang di-bookmark. Silakan pilih di Sidebar sebelah kiri.")
    else:
        st.success(f"Menampilkan {len(st.session_state.bookmarks)} saham pilihan kamu.")
        with st.spinner("Mengambil data bookmark..."):
            # Ambil data khusus untuk bookmark
            data_bookmark = get_stock_data(st.session_state.bookmarks)
            fig_bookmark = create_stock_grid(st.session_state.bookmarks, data_bookmark)
            if fig_bookmark:
                st.plotly_chart(fig_bookmark, use_container_width=True)
