import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Saham IHSG", layout="wide")

# Judul
st.title("📊 Dashboard Saham IHSG")

# Fungsi untuk mengambil data saham
@st.cache_data(ttl=3600)
def get_stock_data(ticker, period="6mo"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None
        return df
    except:
        return None

# Fungsi untuk mendapatkan daftar saham IHSG
@st.cache_data(ttl=86400)
def get_ihsg_stocks():
    # Daftar saham IHSG populer (top 50)
    # Format: ticker yfinance (tambahkan .JK untuk saham Indonesia)
    stocks = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK",
        "UNVR.JK", "KLBF.JK", "ICBP.JK", "INDF.JK", "GGRM.JK",
        "SMGR.JK", "INTP.JK", "PGAS.JK", "PTBA.JK", "ADRO.JK",
        "BBNI.JK", "HMSP.JK", "EXCL.JK", "JSMR.JK", "UNTR.JK",
        "BSDE.JK", "CPIN.JK", "AKRA.JK", "ITMG.JK", "MNCN.JK",
        "SCMA.JK", "PWON.JK", "ELSA.JK", "WIKA.JK", "PTPP.JK",
        "WSKT.JK", "SMRA.JK", "MEDC.JK", "LPKR.JK", "TKIM.JK",
        "SILO.JK", "TOWR.JK", "ERAA.JK", "TPIA.JK", "DOID.JK",
        "AMRT.JK", "BRPT.JK", "SSMS.JK", "INKP.JK", "ESSA.JK",
        "PANI.JK", "KAEF.JK", "MAPI.JK", "RALS.JK", "SRTG.JK"
    ]
    return stocks

# Fungsi untuk membuat chart individual
def create_individual_chart(df, ticker):
    if df is None or df.empty:
        return None
    
    # Hitung perubahan hari ini
    last_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
    change = last_close - prev_close
    change_pct = (change / prev_close * 100) if prev_close != 0 else 0
    
    # Tentukan warna berdasarkan perubahan
    color = 'green' if change >= 0 else 'red'
    
    # Tanggal 1 bulan lalu dari data terakhir
    last_date = df.index[-1]
    one_month_ago = last_date - timedelta(days=30)
    
    # Buat figure
    fig = go.Figure()
    
    # Tambahkan line chart
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color=color, width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Price: %{y:,.2f}<extra></extra>'
    ))
    
    # Tambahkan garis vertikal untuk 1 bulan lalu
    fig.add_vline(
        x=one_month_ago,
        line_dash="dash",
        line_color="blue",
        line_width=1,
        annotation_text="1 bulan lalu",
        annotation_position="top"
    )
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} - Change: {change_pct:+.2f}%",
        xaxis_title="",
        yaxis_title="Price (IDR)",
        hovermode='x unified',
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

# Fungsi untuk membuat grid chart
def create_grid_chart(stocks_data):
    # Hitung jumlah baris yang diperlukan
    n_stocks = len(stocks_data)
    n_cols = 4
    n_rows = (n_stocks + n_cols - 1) // n_cols
    
    # Hitung spacing dinamis berdasarkan jumlah baris dan kolom
    # Formula Plotly: vertical_spacing * (n_rows - 1) < 1.0
    # Formula Plotly: horizontal_spacing * (n_cols - 1) < 1.0
    vertical_spacing = min(0.06, 0.95 / max(1, n_rows - 1))
    horizontal_spacing = min(0.04, 0.95 / max(1, n_cols - 1))
    
    # Buat subplots
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=[ticker for ticker, _ in stocks_data],
        vertical_spacing=vertical_spacing,
        horizontal_spacing=horizontal_spacing
    )
    
    # Tambahkan trace untuk setiap saham
    for idx, (ticker, df) in enumerate(stocks_data):
        if df is None or df.empty:
            continue
            
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        
        # Hitung perubahan hari ini
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
        change = last_close - prev_close
        
        # Tentukan warna
        color = 'green' if change >= 0 else 'red'
        
        # Tanggal 1 bulan lalu dari data terakhir
        last_date = df.index[-1]
        one_month_ago = last_date - timedelta(days=30)
        
        # Tambahkan line chart
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name=ticker,
                line=dict(color=color, width=1.5),
                hovertemplate=f'<b>{ticker}</b><br>%{{x|%Y-%m-%d}}<br>Price: %{{y:,.2f}}<extra></extra>',
                showlegend=False
            ),
            row=row,
            col=col
        )
        
        # Tambahkan garis vertikal
        fig.add_vline(
            x=one_month_ago,
            line_dash="dash",
            line_color="blue",
            line_width=0.8,
            row=row,
            col=col
        )
    
    # Update layout
    total_height = 350 * n_rows
    fig.update_layout(
        height=total_height,
        showlegend=False,
        hovermode='closest',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Matikan label x-axis dan update y-axis
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickformat='.0f', nticks=5)
    
    return fig

# Tabs
tab1, tab2 = st.tabs(["🔍 Pencarian Saham", "📈 Semua Saham"])

# Tab 1: Pencarian Saham
with tab1:
    st.subheader("Cari Saham Individual")
    
    # Input pencarian
    col1, col2 = st.columns([3, 1])
    with col1:
        search_ticker = st.text_input(
            "Masukkan Kode Saham (contoh: BBCA.JK, BBRI.JK)",
            placeholder="Ketik kode saham..."
        ).upper()
    
    with col2:
        search_button = st.button("🔍 Cari", use_container_width=True)
    
    # Tampilkan hasil pencarian
    if search_ticker and search_button:
        with st.spinner(f"Mengambil data {search_ticker}..."):
            df = get_stock_data(search_ticker)
            
            if df is not None and not df.empty:
                st.success(f"✅ Data {search_ticker} berhasil dimuat!")
                
                # Tampilkan informasi singkat
                last_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
                change = last_close - prev_close
                change_pct = (change / prev_close * 100) if prev_close != 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Harga Terakhir", f"Rp {last_close:,.2f}")
                with col2:
                    st.metric("Perubahan", f"Rp {change:,.2f}", f"{change_pct:+.2f}%")
                with col3:
                    st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
                
                # Tampilkan chart
                fig = create_individual_chart(df, search_ticker)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"❌ Saham {search_ticker} tidak ditemukan atau tidak ada data.")

# Tab 2: Semua Saham dengan Paginasi
with tab2:
    st.subheader("Grid View Semua Saham IHSG")
    
    # Tombol refresh
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Ambil daftar saham
    stocks = get_ihsg_stocks()
    total_stocks = len(stocks)
    
    # Pagination: 100 saham per halaman
    stocks_per_page = 100
    total_pages = (total_stocks + stocks_per_page - 1) // stocks_per_page
    
    # Selector halaman
    st.write(f"**Total: {total_stocks} saham** | Tampil: {stocks_per_page} saham per halaman")
    page = st.selectbox(
        "Pilih Halaman:",
        options=range(1, total_pages + 1),
        format_func=lambda x: f"Halaman {x} (Saham {(x-1)*stocks_per_page + 1} - {min(x*stocks_per_page, total_stocks)})"
    )
    
    # Ambil saham untuk halaman yang dipilih
    start_idx = (page - 1) * stocks_per_page
    end_idx = min(start_idx + stocks_per_page, total_stocks)
    stocks_page = stocks[start_idx:end_idx]
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Ambil data saham untuk halaman ini
    stocks_data = []
    for idx, ticker in enumerate(stocks_page):
        status_text.text(f"Memuat data {ticker}... ({idx + 1}/{len(stocks_page)})")
        progress_bar.progress((idx + 1) / len(stocks_page))
        
        df = get_stock_data(ticker)
        if df is not None and not df.empty:
            stocks_data.append((ticker, df))
    
    # Hapus progress bar
    progress_bar.empty()
    status_text.empty()
    
    # Tampilkan informasi
    st.info(f"📊 Menampilkan {len(stocks_data)} dari {len(stocks_page)} saham di Halaman {page}")
    
    # Buat dan tampilkan grid chart
    if stocks_data:
        with st.spinner("Membuat visualisasi..."):
            fig = create_grid_chart(stocks_data)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data saham yang berhasil dimuat untuk halaman ini.")

# Footer
st.markdown("---")
st.markdown("💡 **Tips**: Gunakan scroll mouse untuk zoom, klik dan drag untuk pan, double click untuk reset zoom")
st.markdown("📅 Data diperbarui otomatis setiap 1 jam")
