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
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            # Auto-fix .JK
            if len(item) == 4 and item.isalpha():
                item += ".JK"
            tickers.append(item)
    
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame()

    # B. DOWNLOAD DATA (AUTO_ADJUST=FALSE AGAR HARGA SESUAI PASAR)
    try:
        # PENTING: auto_adjust=False agar dapat harga MURNI (bukan adjusted dividend)
        # Ini akan memperbaiki masalah persentase ADRO yang tidak sesuai
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
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]
                symbol = t

            if df.empty: continue

            # Bersihkan Kolom
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            # Kita paksa ambil kolom 'Close' (Harga Penutupan Asli)
            # Kadang yfinance kasih 'Adj Close', kita hindari itu untuk kasus ini
            if 'Close' in df.columns:
                price_col = 'Close'
            elif 'Adj Close' in df.columns:
                price_col = 'Adj Close'
            else:
                continue

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

            # YTD Logic (Start of Year)
            current_year = df.index[-1].year
            # Ambil data tahun lalu
            last_year_data = df[df.index.year < current_year]
            
            if not last_year_data.empty:
                # Harga penutupan hari terakhir tahun lalu
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
st.title("🚀 Stock Performance Matrix (Real Price)")
st.markdown("Data menggunakan **Harga Penutupan Asli (Raw Close)**, bukan Adjusted, agar sesuai dengan aplikasi sekuritas.")

col1, col2 = st.columns([1, 4])

with col1:
    st.write("### 📝 Input Saham")
    default_input = "ADRO\nBBCA\nBBRI\nGOTO\nBREN\nPTBA"
    user_input = st.text_area("Daftar Kode:", value=default_input, height=300)
    
    if st.button("🔍 Hitung", type="primary", use_container_width=True):
        st.cache_data.clear() # Paksa refresh data baru

with col2:
    if user_input:
        with st.spinner("Mengambil data Real-Time..."):
            df_result = get_performance_matrix(user_input)
            
            if not df_result.empty:
                st.write(f"### 📊 Hasil Analisa ({len(df_result)} Saham)")
                
                # Format Kolom (Angka & Warna Bar)
                # Kita tambah column_config.ProgressColumn agar visualnya jelas
                # Tapi user minta numerik sortable, jadi kita pakai NumberColumn dengan format %
                
                pct_fmt = st.column_config.NumberColumn(format="%.2f%%")
                
                column_settings = {
                    "Ticker": st.column_config.TextColumn("Kode", frozen=True),
                    "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                    "1 Hari": pct_fmt,
                    "1 Minggu": pct_fmt,
                    "1 Bulan": pct_fmt,
                    "6 Bulan": pct_fmt,
                    "YTD": pct_fmt,
                    "1 Tahun": pct_fmt,
                    "3 Tahun": pct_fmt,
                }

                # Trik Styling Pandas untuk mewarnai Text (Hijau/Merah)
                # Ini tidak merusak sorting karena styler hanya visual
                def color_negative_red(val):
                    if val is None: return 'color: black'
                    color = '#00C805' if val > 0 else '#FF333A' if val < 0 else 'black'
                    return f'color: {color}; font-weight: bold'

                styled_df = df_result.style.format({
                    "1 Hari": "{:.2%}", "1 Minggu": "{:.2%}", "1 Bulan": "{:.2%}",
                    "6 Bulan": "{:.2%}", "YTD": "{:.2%}", "1 Tahun": "{:.2%}", "3 Tahun": "{:.2%}"
                }).applymap(color_negative_red, subset=["1 Hari", "1 Minggu", "1 Bulan", "6 Bulan", "YTD", "1 Tahun", "3 Tahun"])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_settings, # Config header tetap dipakai
                    height=500
                )
            else:
                st.error("Gagal mengambil data. Coba lagi.")
