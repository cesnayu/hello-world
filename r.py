import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Stock Performance Matrix")

# --- 2. FUNGSI LOGIKA (BACKEND) ---
@st.cache_data(ttl=600) 
def get_performance_matrix(raw_input):
    if not raw_input: return pd.DataFrame()

    # A. BERSIHKAN INPUT
    # Mengubah enter/spasi menjadi koma
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            # Auto-fix .JK (Jika 4 huruf tanpa titik)
            if len(item) == 4 and item.isalpha():
                item += ".JK"
            tickers.append(item)
    
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame()

    # B. DOWNLOAD DATA 
    # auto_adjust=False PENTING agar harga ADRO/Dividen saham lain tidak ter-adjust (Raw Price)
    try:
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False, auto_adjust=False)
    except Exception:
        return pd.DataFrame()

    results = []

    # C. LOOP PER SAHAM
    for t in tickers:
        try:
            # Ekstrak Data
            if len(tickers) == 1:
                df = data
                symbol = tickers[0]
            else:
                # Cek MultiIndex
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]
                symbol = t

            if df.empty: continue

            # Bersihkan Kolom
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            # Hapus kolom duplikat jika ada
            df = df.loc[:, ~df.columns.duplicated()]

            # Pastikan ambil 'Close' (Harga Raw) bukan 'Adj Close'
            if 'Close' in df.columns:
                price_col = 'Close'
            elif 'Adj Close' in df.columns:
                price_col = 'Adj Close'
            else:
                continue # Skip jika tidak ada data harga

            df = df[[price_col]].rename(columns={price_col: 'Close'})
            df = df.sort_index()

            if len(df) < 2: continue

            curr_price = float(df['Close'].iloc[-1])

            # Helper Hitung %
            def calc_change(days):
                if len(df) > days:
                    prev = float(df['Close'].iloc[-(days + 1)])
                    if prev == 0: return 0.0
                    return ((curr_price - prev) / prev) 
                return None 

            # YTD Logic
            current_year = df.index[-1].year
            last_year_data = df[df.index.year < current_year]
            
            if not last_year_data.empty:
                last_year_close = float(last_year_data['Close'].iloc[-1])
                ytd_change = (curr_price - last_year_close) / last_year_close
            else:
                ytd_change = None 

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

        except Exception:
            continue

    return pd.DataFrame(results)

# --- 3. TAMPILAN UI ---
st.title("🚀 Stock Performance Matrix (Raw Price)")
st.markdown("Data menggunakan **Harga Penutupan Asli (Raw Close)**. Urutan bisa di-sort dengan klik judul kolom.")

col1, col2 = st.columns([1, 4])

with col1:
    st.write("### 📝 Input Saham")
    default_input = "ADRO\nBBCA\nBBRI\nGOTO\nBREN\nPTBA"
    user_input = st.text_area("Daftar Kode:", value=default_input, height=300, help="Pisahkan Enter/Koma")
    
    if st.button("🔍 Hitung", type="primary", use_container_width=True):
        st.cache_data.clear() 

with col2:
    if user_input:
        with st.spinner("Mengambil data Real-Time..."):
            df_result = get_performance_matrix(user_input)
            
            if not df_result.empty:
                st.write(f"### 📊 Hasil Analisa ({len(df_result)} Saham)")
                
                # Definisi Format Kolom (Tanpa frozen=True yg bikin error)
                pct_fmt = st.column_config.NumberColumn(format="%.2f%%")
                
                column_settings = {
                    "Ticker": st.column_config.TextColumn("Kode Saham"), # FIXED: Hapus frozen=True
                    "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                    "1 Hari": pct_fmt,
                    "1 Minggu": pct_fmt,
                    "1 Bulan": pct_fmt,
                    "6 Bulan": pct_fmt,
                    "YTD": pct_fmt,
                    "1 Tahun": pct_fmt,
                    "3 Tahun": pct_fmt,
                }

                # Styling Warna (Hijau/Merah)
                def color_negative_red(val):
                    if val is None: return 'color: black'
                    color = '#00C805' if val > 0 else '#FF333A' if val < 0 else 'black'
                    return f'color: {color}; font-weight: bold'

                # Apply styling format angka % dan warna
                styled_df = df_result.style.format({
                    "1 Hari": "{:.2%}", "1 Minggu": "{:.2%}", "1 Bulan": "{:.2%}",
                    "6 Bulan": "{:.2%}", "YTD": "{:.2%}", "1 Tahun": "{:.2%}", "3 Tahun": "{:.2%}"
                }).applymap(color_negative_red, subset=["1 Hari", "1 Minggu", "1 Bulan", "6 Bulan", "YTD", "1 Tahun", "3 Tahun"])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_settings, 
                    height=500
                )
            else:
                st.error("Gagal mengambil data. Pastikan kode saham benar atau coba lagi nanti.")
