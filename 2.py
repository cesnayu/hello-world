import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Grafik Saham", layout="wide")

st.title("📈 Dashboard Analisa Teknikal Sederhana")
st.markdown("Pantau pergerakan harga saham dengan indikator **Moving Average (MA)**.")

# ==========================================
# 2. SIDEBAR (INPUT USER)
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    # Input List Saham
    default_tickers = "BBCA, BBRI, INDF, TLKM"
    input_saham = st.text_area("Masukkan Kode Saham (Pisahkan koma):", value=default_tickers, height=100)
    st.caption("Contoh: bbca, bmri, goto (Tidak perlu ketik .JK)")
    
    # Pilihan Rentang Waktu (Timeframe)
    range_option = st.selectbox(
        "Pilih Rentang Waktu:",
        ["1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun", "3 Tahun", "5 Tahun", "Max"]
    )
    
    # Mapping nama pilihan ke kode Yahoo Finance
    period_map = {
        "1 Bulan": "1mo",
        "3 Bulan": "3mo",
        "6 Bulan": "6mo",
        "1 Tahun": "1y",
        "3 Tahun": "3y",
        "5 Tahun": "5y",
        "Max": "max"
    }
    selected_period = period_map[range_option]

    st.divider()
    
    # Pilihan Indikator
    st.subheader("Indikator")
    show_ma20 = st.checkbox("Tampilkan MA 20 (Garis Kuning)", value=True)
    show_ma52 = st.checkbox("Tampilkan MA 52 (Garis Ungu)", value=True)
    
    st.divider()
    if st.button("🔄 Update Grafik"):
        st.experimental_rerun()

# ==========================================
# 3. FUNGSI PENGOLAH DATA
# ==========================================
def process_tickers(raw_input):
    """Membersihkan input user dan menambahkan .JK"""
    tickers = [t.strip().upper() for t in raw_input.split(',')]
    clean_tickers = []
    for t in tickers:
        if t: # Cek biar ga ada string kosong
            if not t.endswith(".JK"):
                clean_tickers.append(f"{t}.JK")
            else:
                clean_tickers.append(t)
    return list(set(clean_tickers)) # Hapus duplikat

# ==========================================
# 4. UTAMA (LOOPING & PLOTTING)
# ==========================================

tickers = process_tickers(input_saham)

if not tickers:
    st.warning("Silakan masukkan kode saham terlebih dahulu.")
else:
    # Loop untuk setiap saham yang dimasukkan
    for ticker in tickers:
        try:
            # Ambil data dari Yahoo Finance
            # Gunakan Ticker().history() agar lebih fleksibel per saham
            stock = yf.Ticker(ticker)
            df = stock.history(period=selected_period)
            
            # Cek apakah data ada
            if df.empty:
                st.error(f"❌ Data tidak ditemukan untuk **{ticker}**. Cek kembali kode sahamnya.")
                continue
            
            # --- HITUNG MOVING AVERAGE ---
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA52'] = df['Close'].rolling(window=52).mean()
            
            # Nama Saham (Biar lebih jelas)
            stock_name = stock.info.get('shortName', ticker)
            curr_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = ((curr_price - prev_price) / prev_price) * 100
            
            # Warna Header berdasarkan Naik/Turun
            color_delta = "green" if change >= 0 else "red"
            emoji_delta = "🔼" if change >= 0 else "🔻"
            
            # --- TAMPILAN PER SAHAM ---
            st.markdown(f"### {emoji_delta} {stock_name} ({ticker.replace('.JK','')})")
            st.markdown(f"**Harga: Rp {curr_price:,.0f}** (<span style='color:{color_delta}'>{change:+.2f}%</span>)", unsafe_allow_html=True)

            # --- BUAT GRAFIK INTERAKTIF (PLOTLY) ---
            fig = go.Figure()

            # 1. Grafik Harga (Candlestick atau Line)
            # Kita pakai Line Chart area filled biar cantik, atau Candlestick kalau mau pro.
            # Disini pakai Line Chart tebal biar mudah dibaca bareng MA.
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['Close'],
                mode='lines',
                name='Harga Close',
                line=dict(color='#00F0FF', width=2) # Warna Cyan Cerah
            ))

            # 2. Grafik MA 20
            if show_ma20:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['MA20'],
                    mode='lines',
                    name='MA 20',
                    line=dict(color='#FFD700', width=1.5, dash='dash') # Warna Emas Putus-putus
                ))

            # 3. Grafik MA 52
            if show_ma52:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['MA52'],
                    mode='lines',
                    name='MA 52',
                    line=dict(color='#BD00FF', width=1.5) # Warna Ungu
                ))

            # Layout Grafik
            fig.update_layout(
                title=f"Pergerakan Harga {ticker.replace('.JK','')} ({range_option})",
                xaxis_title="Tanggal",
                yaxis_title="Harga (Rp)",
                template="plotly_dark", # Tema Gelap biar keren
                height=450,
                hovermode="x unified", # Biar cursor nyala semua info
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Tampilkan Grafik
            st.plotly_chart(fig, use_container_width=True)
            st.divider()

        except Exception as e:
            st.error(f"Terjadi kesalahan pada {ticker}: {e}")
