import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Stock Performance Matrix")

# --- 2. FUNGSI LOGIKA (BACKEND) ---
@st.cache_data(ttl=600) # Cache data 10 menit
def get_performance_matrix(raw_input):
    """
    Menerima input string mentah, membersihkan, download data 5 tahun,
    dan menghitung performa (1D, 1W, 1M, YTD, 1Y, 3Y).
    """
    if not raw_input: return pd.DataFrame()

    # --- A. PEMBERSIHAN INPUT ---
    # Mengubah enter/spasi menjadi koma, lalu split
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            # Auto-fix: Jika 4 huruf alfabet (contoh: BBCA) tanpa titik, tambah .JK
            if len(item) == 4 and item.isalpha():
                item += ".JK"
            tickers.append(item)
    
    # Hapus duplikat
    tickers = list(set(tickers))
    
    if not tickers: return pd.DataFrame()

    # --- B. DOWNLOAD DATA ---
    try:
        # Ambil data 5 tahun untuk cover perhitungan 3Y + hari libur
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False)
    except Exception as e:
        return pd.DataFrame()

    results = []

    # --- C. LOOP PER SAHAM ---
    for t in tickers:
        try:
            # Handle struktur data yfinance (Single vs Multi Ticker)
            if len(tickers) == 1:
                df = data
                symbol = tickers[0]
            else:
                # Cek apakah ticker ada di data yang didownload
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]
                symbol = t

            if df.empty: continue

            # Flatten kolom jika MultiIndex (kadang terjadi di yfinance terbaru)
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            # Hapus kolom duplikat & urutkan tanggal
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.sort_index()

            # Butuh minimal data 2 hari untuk hitung change
            if len(df) < 2: continue

            # Ambil harga terakhir
            curr_price = float(df['Close'].iloc[-1])

            # Fungsi helper hitung % change
            # Return angka FLOAT (bukan string) agar bisa di-sort
            def calc_change(days):
                if len(df) > days:
                    # iloc[-(days+1)] adalah harga 'days' hari yang lalu
                    prev = float(df['Close'].iloc[-(days + 1)])
                    if prev == 0: return 0.0
                    return ((curr_price - prev) / prev) # Hasil desimal (0.1 = 10%)
                return None # Return None jika history tidak cukup (misal baru IPO)

            # Hitung YTD (Year to Date)
            current_year = df.index[-1].year
            last_year_data = df[df.index.year < current_year]
            
            if not last_year_data.empty:
                last_year_close = float(last_year_data['Close'].iloc[-1])
                ytd_change = (curr_price - last_year_close) / last_year_close
            else:
                ytd_change = None # Saham baru IPO tahun ini

            # Masukkan ke list
            results.append({
                "Ticker": symbol,
                "Harga": curr_price,
                "1 Hari": calc_change(1),
                "1 Minggu": calc_change(5),
                "1 Bulan": calc_change(21),
                "6 Bulan": calc_change(126),
                "YTD": ytd_change,
                "1 Tahun": calc_change(252),
                "3 Tahun": calc_change(756)
            })

        except Exception as e:
            continue

    return pd.DataFrame(results)

# --- 3. TAMPILAN UI (FRONTEND) ---
st.title("🚀 Stock Performance Matrix")
st.markdown("""
Aplikasi untuk membandingkan kinerja saham dalam berbagai rentang waktu secara cepat.
* **Format Input:** Bisa pakai Koma (`,`) atau Enter (Baris Baru).
* **Auto .JK:** Ketik `BBCA` otomatis jadi `BBCA.JK`.
* **Sorting:** Klik judul kolom untuk mengurutkan (Tertinggi/Terendah).
""")

# Input Area
col1, col2 = st.columns([1, 4])

with col1:
    st.write("### 📝 Input Saham")
    default_input = "BBCA\nBBRI\nBMRI\nGOTO\nADRO\nUNVR\nTLKM\nAMMN\nBREN"
    user_input = st.text_area("Daftar Kode Saham:", value=default_input, height=300, help="Pisahkan dengan Enter atau Koma")
    
    calculate_btn = st.button("🔍 Hitung Performa", type="primary", use_container_width=True)
    
    if st.button("🗑️ Reset Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    if calculate_btn and user_input:
        with st.spinner("Mengambil data dari Yahoo Finance..."):
            df_result = get_performance_matrix(user_input)
            
            if not df_result.empty:
                st.write(f"### 📊 Hasil Analisa ({len(df_result)} Saham)")
                
                # Konfigurasi Kolom untuk Tampilan
                # NumberColumn format="%.2f%%" membuat angka 0.1 tampil jadi 10.00%
                # Tapi data aslinya tetap 0.1, jadi sorting tetap benar.
                column_settings = {
                    "Ticker": st.column_config.TextColumn("Kode Saham", frozen=True),
                    "Harga": st.column_config.NumberColumn("Harga Terakhir", format="Rp %.0f"),
                    "1 Hari": st.column_config.NumberColumn("1 Hari", format="%.2f%%"),
                    "1 Minggu": st.column_config.NumberColumn("1 Minggu", format="%.2f%%"),
                    "1 Bulan": st.column_config.NumberColumn("1 Bulan", format="%.2f%%"),
                    "6 Bulan": st.column_config.NumberColumn("6 Bulan", format="%.2f%%"),
                    "YTD": st.column_config.NumberColumn("YTD", format="%.2f%%"),
                    "1 Tahun": st.column_config.NumberColumn("1 Tahun", format="%.2f%%"),
                    "3 Tahun": st.column_config.NumberColumn("3 Tahun", format="%.2f%%"),
                }

                st.dataframe(
                    df_result,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_settings,
                    height=500
                )
                
                st.caption("*Catatan: Kolom kosong (None) berarti saham belum listing pada periode tersebut (misal belum ada data 3 tahun).*")
                
            else:
                st.error("Data tidak ditemukan. Pastikan koneksi internet lancar atau kode saham benar.")
                st.info("Tips: Coba masukkan kode satu per satu untuk memastikan.")
    
    elif not user_input:
        st.info("👈 Silakan masukkan kode saham di sebelah kiri.")
