import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Stock Performance Analyzer")

# --- 2. FUNGSI LOGIKA (BACKEND) ---
@st.cache_data(ttl=600) # Cache data 10 menit
def get_performance_summary(tickers_list):
    """
    Mengambil data saham dan menghitung performa (1D, 1W, 1M, YTD, 1Y, 3Y).
    Output: DataFrame dengan tipe data Numerik (Float) agar bisa disortir.
    """
    
    # A. BERSIHKAN INPUT USER
    cleaned_tickers = []
    
    # Gabungkan semua input menjadi satu string panjang dulu, lalu split ulang
    # Ini menangani kasus campuran koma dan enter
    raw_text = " ".join(tickers_list).replace('\n', ' ').replace(',', ' ')
    
    for item in raw_text.split():
        clean_item = item.strip().upper()
        if clean_item:
            # AUTO FIX: Jika 4 huruf (kode umum IHSG) dan tidak ada titik, tambah .JK
            # Contoh: "BBCA" -> "BBCA.JK"
            if len(clean_item) == 4 and "." not in clean_item and not clean_item.isdigit():
                clean_item += ".JK"
            cleaned_tickers.append(clean_item)
    
    # Hapus duplikat
    cleaned_tickers = list(set(cleaned_tickers))
    
    if not cleaned_tickers: 
        return pd.DataFrame()

    # B. DOWNLOAD DATA (5 Tahun untuk cover hitungan 3Y)
    try:
        data = yf.download(cleaned_tickers, period="5y", group_by='ticker', progress=False)
    except Exception as e:
        return pd.DataFrame()
    
    results = []
    
    # C. LOOPING HITUNG KINERJA
    for t in cleaned_tickers:
        try:
            # Handle struktur data yfinance (Single vs Multi Ticker)
            if len(cleaned_tickers) == 1: 
                df = data
                symbol = cleaned_tickers[0]
            else: 
                # Cek keberadaan ticker di kolom
                # Handle MultiIndex columns pandas
                if isinstance(data.columns, pd.MultiIndex):
                    if t not in data.columns.levels[0]: continue
                elif t not in data.columns:
                    continue
                    
                df = data[t]
                symbol = t
            
            if df.empty: continue
            
            # Flatten & Clean Columns
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            # Hapus kolom duplikat (Solusi error Narwhals/Plotly terbaru)
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Pastikan minimal data ada
            if len(df) < 2: continue
            
            # Ambil harga terakhir
            curr_price = float(df['Close'].iloc[-1])
            
            # Fungsi Helper Hitung %
            # Mengembalikan float atau None (jika history kurang)
            def get_pct_change(days_ago):
                if len(df) > days_ago:
                    prev = float(df['Close'].iloc[-(days_ago + 1)])
                    if prev == 0: return 0.0
                    return ((curr_price - prev) / prev) * 100
                return None
            
            # Logika YTD (Year to Date)
            curr_year = df.index[-1].year
            last_year_data = df[df.index.year < curr_year]
            
            if not last_year_data.empty:
                last_year_close = float(last_year_data['Close'].iloc[-1])
                ytd_change = ((curr_price - last_year_close) / last_year_close) * 100
            else:
                ytd_change = None # Saham baru IPO tahun ini

            # Susun Dictionary Hasil
            results.append({
                "Ticker": symbol,
                "Price": curr_price,
                "1 Hari": get_pct_change(1),
                "1 Minggu": get_pct_change(5),
                "1 Bulan": get_pct_change(21),     # ~21 hari bursa
                "6 Bulan": get_pct_change(126),    # ~126 hari bursa
                "YTD": ytd_change,
                "1 Tahun": get_pct_change(252),    # ~252 hari bursa
                "3 Tahun": get_pct_change(756)     # ~756 hari bursa
            })
            
        except Exception as e:
            continue
            
    return pd.DataFrame(results)

# --- 3. UI UTAMA ---

st.title("🚀 Stock Performance Analyzer")
st.write("Masukkan daftar saham untuk membandingkan kinerja dalam berbagai rentang waktu.")

# A. Input Section
col_input, col_help = st.columns([3, 1])

with col_input:
    # Default value campur-campur format untuk tes ketangguhan kode
    default_text = "BBCA\nBBRI.JK, GOTO\nADRO, TLKM\nUNVR"
    user_input = st.text_area("Daftar Saham (Pisahkan dengan Enter atau Koma):", value=default_text, height=150)
    
    calculate_btn = st.button("🔍 Hitung Performa", type="primary")

with col_help:
    st.info("""
    **Fitur:**
    - Auto-add `.JK` (jika lupa).
    - Support Input Enter/Koma.
    - Sorting Numerik (Klik judul kolom).
    - Warna Bar Otomatis.
    """)

st.divider()

# B. Output Section
if calculate_btn and user_input:
    
    with st.spinner("Sedang mengambil data & menghitung..."):
        # Ubah input text area menjadi list string
        input_list = [user_input] 
        
        df_result = get_performance_summary(input_list)
        
        if not df_result.empty:
            st.success(f"Berhasil menganalisa {len(df_result)} saham.")
            
            # Tampilkan Dataframe
            st.dataframe(
                df_result,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ticker": st.column_config.TextColumn("Ticker", frozen=True),
                    "Price": st.column_config.NumberColumn("Harga Terkini", format="Rp %.0f"),
                    
                    # Kolom Persentase dengan Bar Chart Kecil
                    "1 Hari": st.column_config.NumberColumn("1 Hari", format="%.2f%%"),
                    "1 Minggu": st.column_config.NumberColumn("1 Minggu", format="%.2f%%"),
                    "1 Bulan": st.column_config.NumberColumn("1 Bulan", format="%.2f%%"),
                    "6 Bulan": st.column_config.NumberColumn("6 Bulan", format="%.2f%%"),
                    "YTD": st.column_config.NumberColumn("YTD", format="%.2f%%"),
                    "1 Tahun": st.column_config.NumberColumn("1 Tahun", format="%.2f%%"),
                    "3 Tahun": st.column_config.NumberColumn("3 Tahun", format="%.2f%%"),
                }
            )
            
            # Tambahan: Statistik Sederhana
            best_ytd = df_result.loc[df_result['YTD'].idxmax()] if not df_result['YTD'].isnull().all() else None
            worst_ytd = df_result.loc[df_result['YTD'].idxmin()] if not df_result['YTD'].isnull().all() else None
            
            if best_ytd is not None:
                c1, c2 = st.columns(2)
                c1.metric(label="🏆 Juara YTD", value=best_ytd['Ticker'], delta=f"{best_ytd['YTD']:.2f}%")
                c2.metric(label="📉 Terboncos YTD", value=worst_ytd['Ticker'], delta=f"{worst_ytd['YTD']:.2f}%", delta_color="inverse")

        else:
            st.error("Data tidak ditemukan.")
            st.write("Kemungkinan penyebab:")
            st.write("1. Koneksi internet terganggu.")
            st.write("2. Kode saham salah semua.")
            st.write("3. Yahoo Finance sedang membatasi request (tunggu 1 menit).")
