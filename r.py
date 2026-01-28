import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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

    # B. DOWNLOAD DATA (Raw Price)
    try:
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False, auto_adjust=False)
    except Exception:
        return pd.DataFrame()

    results = []

    # C. LOOP PER SAHAM
    for t in tickers:
        try:
            # 1. Ekstrak Data
            if len(tickers) == 1:
                df = data
                symbol = tickers[0]
            else:
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]
                symbol = t

            if df.empty: continue

            # 2. Cleaning Kolom
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: price_col = 'Close'
            elif 'Adj Close' in df.columns: price_col = 'Adj Close'
            else: continue

            df = df[[price_col]].rename(columns={price_col: 'Close'})
            df = df.dropna()
            
            # Hapus Timezone
            df.index = df.index.tz_localize(None)
            df = df.sort_index()

            if len(df) < 2: continue

            curr_price = float(df['Close'].iloc[-1])
            curr_date = df.index[-1]

            # --- LOGIKA TIME TRAVEL SLICING ---
            def get_pct_change(days_ago):
                target_date = curr_date - timedelta(days=days_ago)
                # Ambil data s.d. tanggal target
                past_data = df.loc[df.index <= target_date]
                
                if past_data.empty: return None
                
                # Ambil harga terakhir dari potongan tersebut
                past_price = float(past_data['Close'].iloc[-1])
                
                if past_price == 0: return 0.0
                
                # Dikali 100 agar jadi angka puluhan (misal 26.5)
                return ((curr_price - past_price) / past_price) * 100

            # --- YTD Logic (Indentasi Diperbaiki) ---
            last_year = curr_date.year - 1
            last_year_end = datetime(last_year, 12, 31)
            ytd_data = df.loc[df.index <= last_year_end]
            
            if not ytd_data.empty:
                last_year_close = float(ytd_data['Close'].iloc[-1])
                ytd_change = ((curr_price - last_year_close) / last_year_close) * 100
            else:
                ytd_change = None

            # --- Append Result (Indentasi Diperbaiki) ---
            results.append({
                "Ticker": symbol,
                "Harga": curr_price,
                "1 Hari": ((curr_price - df['Close'].iloc[-2])/df['Close'].iloc[-2]) * 100,
                "1 Minggu": get_pct_change(7),
                "1 Bulan": get_pct_change(30),
                "6 Bulan": get_pct_change(180),
                "YTD": ytd_change,
                "1 Tahun": get_pct_change(365),
                "3 Tahun": get_pct_change(365 * 3)
            })

        except Exception:
            # Jika ada error pada satu saham, skip saham itu dan lanjut ke berikutnya
            continue

    return pd.DataFrame(results)

# --- 3. TAMPILAN UI ---
st.title("🚀 Stock Performance Matrix (Fixed Indentation)")
st.markdown("Menggunakan **Raw Close Price** & **Calendar Date Slicing**.")

col1, col2 = st.columns([1, 4])

with col1:
    st.write("### 📝 Input Saham")
    default_input = "ADRO\nBBCA\nBBRI\nGOTO\nBREN\nPTBA"
    user_input = st.text_area("Daftar Kode:", value=default_input, height=300)
    
    if st.button("🔍 Hitung", type="primary", use_container_width=True):
        st.cache_data.clear() 

with col2:
    if user_input:
        with st.spinner("Mengambil data Real-Time..."):
            df_result = get_performance_matrix(user_input)
            
            if not df_result.empty:
                st.write(f"### 📊 Hasil Analisa ({len(df_result)} Saham)")
                
                # Format Angka: %.2f%% (Misal: 26.50%)
                pct_fmt = st.column_config.NumberColumn(format="%.2f%%")
                
                column_settings = {
                    "Ticker": st.column_config.TextColumn("Kode"),
                    "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                    "1 Hari": pct_fmt,
                    "1 Minggu": pct_fmt,
                    "1 Bulan": pct_fmt,
                    "6 Bulan": pct_fmt,
                    "YTD": pct_fmt,
                    "1 Tahun": pct_fmt,
                    "3 Tahun": pct_fmt,
                }

                # Styling Warna
                def color_negative_red(val):
                    if val is None or pd.isna(val): return 'color: gray'
                    color = '#00C805' if val > 0 else '#FF333A' if val < 0 else 'black'
                    return f'color: {color}; font-weight: bold'

                styled_df = df_result.style.format({
                    "1 Hari": "{:.2f}", "1 Minggu": "{:.2f}", "1 Bulan": "{:.2f}",
                    "6 Bulan": "{:.2f}", "YTD": "{:.2f}", "1 Tahun": "{:.2f}", "3 Tahun": "{:.2f}"
                }).applymap(color_negative_red, subset=["1 Hari", "1 Minggu", "1 Bulan", "6 Bulan", "YTD", "1 Tahun", "3 Tahun"])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_settings, 
                    height=500
                )
            else:
                st.error("Gagal mengambil data.")
