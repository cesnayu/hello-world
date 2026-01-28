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

    # B. DOWNLOAD DATA (AUTO_ADJUST=FALSE)
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

            # YTD Logic
            last_year = curr_date.year - 1
            last
