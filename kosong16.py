import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os
import pytz 

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

DB_FILE = "stock_database.json"

# --- 2. FUNGSI DATABASE (JSON) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "vol_watchlist": st.session_state.get("vol_watchlist", []),
        "vol_saved_tickers": st.session_state.get("vol_saved_tickers", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 3. INISIALISASI SESSION STATE ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]
if 'vol_watchlist' not in st.session_state:
    st.session_state.vol_watchlist = saved_data["vol_watchlist"] if (saved_data and "vol_watchlist" in saved_data) else ["GOTO.JK", "BBRI.JK", "BUMI.JK"]
if 'vol_saved_tickers' not in st.session_state:
    st.session_state.vol_saved_tickers = saved_data["vol_saved_tickers"] if (saved_data and "vol_saved_tickers" in saved_data) else []
if 'picked_stocks' not in st.session_state:
    st.session_state.picked_stocks = []
if 'grid_page' not in st.session_state:
    st.session_state.grid_page = 1

# --- 4. DATA STATIC (SAMPEL TICKER) ---
GRID_TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "GOTO.JK", 
    "UNVR.JK", "ICBP.JK", "INDF.JK", "KLBF.JK", "ADRO.JK", "PTBA.JK", "ITMG.JK", 
    "PGAS.JK", "ANTM.JK", "INCO.JK", "TINS.JK", "BRPT.JK", "TPIA.JK", "INKP.JK", 
    "TKIM.JK", "SMGR.JK", "INTP.JK", "CPIN.JK", "JPFA.JK", "AMRT.JK", "MAPI.JK", 
    "ACES.JK", "ERAA.JK", "BUKA.JK", "EMTK.JK", "SCMA.JK", "MNCN.JK", "BUMI.JK", 
    "BRIS.JK", "ARTO.JK", "BBTN.JK", "SRTG.JK", "HRUM.JK", "MEDC.JK", "AKRA.JK",
    "UNTR.JK", "HEXA.JK", "JSMR.JK", "WIKA.JK", "PTPP.JK", "ADHI.JK", "WSKT.JK"
]
DEFAULT_INPUT_TXT = "BBCA.JK, BBRI.JK, GOTO.JK, ADRO.JK"

# --- 5. FUNGSI LOGIKA (BACKEND) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo", interval="1d"):
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=False)
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def get_single_stock_detail(ticker, period):
    if not ticker: return None
    interv = "5m" if period in ["1d", "5d"] else "1d"
    try:
        df = yf.download(ticker, period=period, interval=interv, progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()] 
        if 'Close' not in df.columns and 'Adj Close' in df.columns:
            df = df.rename(columns={'Adj Close': 'Close'})
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
        
        jkt_tz = pytz.timezone('Asia/Jakarta')
        if df['Date'].dt.tz is None:
            df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert(jkt_tz)
        else:
            df['Date'] = df['Date'].dt.tz_convert(jkt_tz)
        return df
    except: return None

@st.cache_data(ttl=3600)
def get_fundamental_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "pbv": info.get('priceToBook'),
            "per": info.get('trailingPE'),
            "eps": info.get('trailingEps'),
            "mkt_cap": info.get('marketCap'),
            "sector": info.get('industry', '-')
        }
    except: return None

@st.cache_data(ttl=3600)
def get_financials_history(ticker):
    try:
        stock = yf.Ticker(ticker)
        q_fin = stock.quarterly_financials.T
        if not q_fin.empty:
            q_fin.index = pd.to_datetime(q_fin.index).tz_localize(None)
            q_fin = q_fin.sort_index()
        a_fin = stock.financials.T
        if not a_fin.empty:
            a_fin.index = pd.to_datetime(a_fin.index).tz_localize(None)
            a_fin = a_fin.sort_index()
        return q_fin, a_fin
    except: return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=600)
def get_seasonal_details(tickers_str, start_month, end_month, lookback_years=5):
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    start_date = datetime.now() - timedelta(days=(lookback_years + 2) * 365)
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=False)
    results = {} 
    for ticker in ticker_list:
        try:
            if len(ticker_list) == 1: df = data; symbol = ticker_list[0]
            else: 
                if ticker not in data.columns.levels[0]: continue
                df = data[ticker]; symbol = ticker
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            
            stock_years_data = {}
            current_year = datetime.now().year
            for i in range(0, lookback_years + 1):
                y_end = current_year - i
                if int(start_month) > int(end_month): y_start = y_end - 1 
                else: y_start = y_end
                try:
                    d_start = datetime(y_start, int(start_month), 1)
                    if d_start > datetime.now(): continue
                    d_end = datetime(y_end, int(end_month), 28) 
                    label = f"{y_start}/{y_end}" if int(start_month) > int(end_month) else f"{y_end}"
                except: continue
                mask = (df['Date'] >= d_start) & (df['Date'] <= d_end)
                df_period = df.loc[mask].copy()
                if df_period.empty: continue
                first_price = df_period['Close'].iloc[0]
                df_period['Rel_Change'] = ((df_period['Close'] - first_price) / first_price) * 100
                stock_years_data[label] = df_period['Rel_Change'].reset_index(drop=True)
            if stock_years_data: results[symbol] = stock_years_data
        except: continue
    return results

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_list, period_code="1mo"):
    if not tickers_list: return None
    download_period = "5d" if period_code == "1d" else "1mo"
    if period_code == "ytd": download_period = "ytd"
    elif period_code == "1y": download_period = "1y"
    
    try:
        data = yf.download(tickers_list, period=download_period, group_by='ticker', progress=False, auto_adjust=False)
    except: return None

    stats = []
    for t in tickers_list:
        try:
            if len(tickers_list) == 1: df = data; symbol = tickers_list[0]
            else: 
                if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            last_vol = df['Volume'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            avg_vol = df['Volume'].tail(5).mean()
            
            if period_code == "1d":
                if len(df) >= 2:
                    prev_close = df['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                else: change_pct = 0.0
            else:
                first_close = df['Close'].iloc[0]
                change_pct = ((last_close - first_close) / first_close) * 100

            stats.append({
                "Ticker": symbol, "Price": last_close, "Change %": change_pct,
                "Volume": last_vol, "Avg Vol (5D)": avg_vol, "Est. Value": last_close * last_vol,
                "Vol vs Avg": (last_vol / avg_vol) if avg_vol > 0 else 0
            })
        except: continue
    return pd.DataFrame(stats)

@st.cache_data(ttl=300)
def get_latest_snapshot(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False, auto_adjust=False)
        snapshot = {}
        for t in tickers:
            try:
                if len(tickers) == 1: df = data
                else: 
                    if t in data.columns.levels[0]: df = data[t]
                    else: continue
                if not df.empty:
                    col_close = 'Close' if 'Close' in df.columns else 'Adj Close'
                    last_price = float(df[col_close].iloc[-1])
                    last_vol = float(df['Volume'].iloc[-1])
                    snapshot[t] = {
                        'price': last_price,
                        'volume_share': last_vol,
                        'volume_lot': last_vol / 100,
                        'value': last_price * last_vol
                    }
            except: continue
        return snapshot
    except: return {}

@st.cache_data(ttl=600) 
def get_performance_matrix(raw_input):
    if not raw_input: return pd.DataFrame()
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = [t.strip().upper() for t in clean_input.split(',') if t.strip()]
    # Tambah .JK
    tickers = [t + ".JK" if not t.endswith(".JK") else t for t in tickers]
    tickers = list(set(tickers))
    
    try:
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False, auto_adjust=False)
    except: return pd.DataFrame()
    
    results = []
    for t in tickers:
        try:
            try: industry = yf.Ticker(t).info.get('industry', '-')
            except: industry = '-'

            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: price_col = 'Close'
            elif 'Adj Close' in df.columns: price_col = 'Adj Close'
            else: continue
            
            df = df[[price_col]].rename(columns={price_col: 'Close'}).dropna().sort_index()
            if len(df) < 2: continue
            
            curr_price = float(df['Close'].iloc[-1])
            curr_date = df.index[-1]

            def get_pct_change(days_ago):
                target_date = curr_date - timedelta(days=days_ago)
                past_data = df.loc[df.index <= target_date]
                if past_data.empty: return None
                past_price = float(past_data['Close'].iloc[-1])
                return 0.0 if past_price == 0 else ((curr_price - past_price) / past_price) * 100

            last_year = curr_date.year - 1
            last_year_end = datetime(last_year, 12, 31)
            ytd_data = df.loc[df.index <= last_year_end]
            ytd_change = None
            if not ytd_data.empty:
                last_year_close = float(ytd_data['Close'].iloc[-1])
                ytd_change = ((curr_price - last_year_close) / last_year_close) * 100

            results.append({
                "Ticker": symbol, "Industri": industry, "Harga": curr_price,
                "1 Hari": ((curr_price - df['Close'].iloc[-2])/df['Close'].iloc[-2]) * 100,
                "1 Minggu": get_pct_change(7), "1 Bulan": get_pct_change(30),
                "6 Bulan": get_pct_change(180), "YTD": ytd_change,
                "1 Tahun": get_pct_change(365), "3 Tahun": get_pct_change(365 * 3)
            })
        except: continue
    return pd.DataFrame(results)

@st.cache_data(ttl=600)
def get_win_loss_details(raw_input):
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = [t.strip().upper() for t in clean_input.split(',') if t.strip()]
    tickers = [t + ".JK" if not t.endswith(".JK") else t for t in tickers]
    tickers = list(set(tickers))
    
    try:
        data = yf.download(tickers, period="3mo", group_by='ticker', progress=False, auto_adjust=False)
    except: return pd.DataFrame(), {}

    summary_results = []
    detail_data = {} 

    for t in tickers:
        try:
            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            col = 'Close' if 'Close' in df.columns else 'Adj Close'
            df['Change'] = df[col].pct_change() * 100
            df = df.dropna()

            df_30 = df.tail(30)
            if len(df_30) < 5: continue 

            detail_data[symbol] = df_30
            green_days = df_30[df_30['Change'] > 0]
            red_days = df_30[df_30['Change'] < 0]

            win_rate = (len(green_days) / len(df_30)) * 100
            avg_gain = green_days['Change'].mean() if not green_days.empty else 0
            avg_loss = red_days['Change'].mean() if not red_days.empty else 0
            total_return = ((df_30[col].iloc[-1] - df_30[col].iloc[0]) / df_30[col].iloc[0]) * 100

            summary_results.append({
                "Ticker": symbol, "Total Candle": len(df_30), "Hari Hijau": len(green_days), "Hari Merah": len(red_days),
                "Win Rate": win_rate, "Rata2 Naik": avg_gain, "Rata2 Turun": avg_loss, "Total Return (30 Candle)": total_return
            })
        except: continue
    return pd.DataFrame(summary_results), detail_data

@st.cache_data(ttl=3600)
def get_fundamental_screener(tickers):
    # Dummy implementation for fundamental screener to prevent error
    data = []
    for t in tickers:
        info = get_fundamental_info(t)
        if info:
            data.append({
                "Ticker": t,
                "Industry": info['sector'],
                "Price": 0, "52W High": 0, "52W Low": 0, # Placeholder
                "PBV": info['pbv'], "PER": info['per'], "EPS": info['eps']
            })
    return pd.DataFrame(data)

# --- 6. VISUALISASI CHART ---
def create_mini_chart_complex(df, ticker, period_code):
    jkt_tz = pytz.timezone('Asia/Jakarta')
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC').tz_convert(jkt_tz)
    else:
        df.index = df.index.tz_convert(jkt_tz)

    df['MA20'] = df['Close'].rolling(window=20).mean()
    first_price = df['Close'].iloc[0]
    df['Pct'] = ((df['Close'] - first_price) / first_price) * 100
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if period_code == "1d":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Price", showlegend=False
        ), secondary_y=False)
        fig.update_layout(xaxis_rangeslider_visible=False)
    else:
        last_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2] if len(df) > 1 else last_p
        color_line = '#00C805' if last_p >= prev_p else '#FF333A'
        
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=color_line, width=1.5), name="Price"), secondary_y=False)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', line=dict(color='#FF9800', width=1), name="MA20"), secondary_y=False)

    fig.add_trace(go.Scatter(x=df.index, y=df['Pct'], mode='lines', line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'), secondary_y=True)

    if period_code == "3mo":
        one_month_ago = datetime.now(jkt_tz) - timedelta(days=30)
        fig.add_vline(x=one_month_ago, line_width=1, line_dash="dot", line_color="blue")

    fig.update_layout(
        title=dict(text=ticker, font=dict(size=12), x=0.5, xanchor='center'),
        margin=dict(l=5, r=5, t=30, b=5), height=200, showlegend=False, hovermode="x unified"
    )
    fig.update_yaxes(title=None, showticklabels=True, tickfont=dict(size=8), secondary_y=False)
    fig.update_yaxes(title=None, showticklabels=True, tickfont=dict(size=8, color='gray'), tickformat=".1f%", secondary_y=True)
    fig.update_xaxes(showticklabels=False)
    return fig

def create_detail_chart(df, ticker, df_fin_filtered):
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.2, 0.3],
        subplot_titles=(f"Price Action: {ticker}", "Volume", "Revenue & Net Income")
    )
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", showlegend=False), row=1, col=1)
    if len(df) > 20: fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), name="MA 20"), row=1, col=1)
    colors = ['#00C805' if c >= o else '#FF333A' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
    if not df_fin_filtered.empty:
        rev_col = next((c for c in df_fin_filtered.columns if 'Revenue' in c or 'revenue' in c), None)
        inc_col = next((c for c in df_fin_filtered.columns if 'Net Income' in c or 'netIncome' in c), None)
        if rev_col: fig.add_trace(go.Bar(x=df_fin_filtered.index, y=df_fin_filtered[rev_col], name="Revenue", marker_color='blue', opacity=0.6), row=3, col=1)
        if inc_col: fig.add_trace(go.Bar(x=df_fin_filtered.index, y=df_fin_filtered[inc_col], name="Net Income", marker_color='green', opacity=0.8), row=3, col=1)
    fig.update_layout(height=800, xaxis_rangeslider_visible=False, hovermode="x unified")
    return fig

# --- 7. MAIN UI ---
st.title("📈 Super Stock Dashboard")

# DEFINISI TAB LENGKAP (11 TAB)
tab_grid, tab_compare, tab_vol, tab_watch, tab_detail, tab_cycle, tab_fund, tab_perf, tab_win, tab_sim, tab_hl = st.tabs([
    "📊 Grid", "⚖️ Bandingkan", "🔊 Volume", "⭐ Watchlist", "🔎 Detail", 
    "🔄 Cycle", "💎 Fundamental", "🚀 Performa", "🎲 Win/Loss", "🎯 Simulator", "📉 High/Low"
])

# === TAB 1: GRID OVERVIEW ===
with tab_grid:
    st.header("📊 Grid Overview")
    with st.expander("🔍 Filter Grid"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: min_p = st.number_input("Min Harga (Rp)", value=0, step=50)
        with c2: max_p = st.number_input("Max Harga (Rp)", value=100000, step=50)
        with c3: min_val_m = st.number_input("Min. Transaksi (Miliar Rp)", value=0, step=1)
        with c4: min_vol_l = st.number_input("Min. Volume (Lot)", value=0, step=1000)
    
    final_tickers = GRID_TICKERS
    if (max_p < 100000) or (min_p > 0) or (min_val_m > 0) or (min_vol_l > 0):
        with st.spinner("Memfilter saham..."):
            snapshot = get_latest_snapshot(GRID_TICKERS)
            filtered = []
            for t, stats in snapshot.items():
                if (min_p <= stats['price'] <= max_p) and ((stats['value']/1e9) >= min_val_m) and ((stats['volume_lot']) >= min_vol_l):
                    filtered.append(t)
            final_tickers = filtered
            st.success(f"Ditemukan {len(final_tickers)} saham.")

    col_tf, col_nav = st.columns([3, 2])
    with col_tf:
        period_label = st.selectbox("Timeframe:", ["1 Hari", "5 Hari", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun", "YTD"], index=3)
        period_map = {"1 Hari": "1d", "5 Hari": "5d", "1 Bulan": "1mo", "3 Bulan": "3mo", "6 Bulan": "6mo", "1 Tahun": "1y", "YTD": "ytd"}
        selected_code = period_map[period_label]
        selected_interval = "5m" if selected_code in ["1d", "5d"] else "1d"
    
    items_per_page = 12
    total_pages = math.ceil(len(final_tickers)/items_per_page) if final_tickers else 1
    
    with col_nav:
        c_prev, c_txt, c_next = st.columns([1, 2, 1])
        if c_prev.button("⬅️") and st.session_state.grid_page > 1: st.session_state.grid_page -= 1
        if c_next.button("➡️") and st.session_state.grid_page < total_pages: st.session_state.grid_page += 1
        c_txt.write(f"Hal {st.session_state.grid_page} dari {total_pages}")

    if final_tickers:
        start = (st.session_state.grid_page - 1) * items_per_page
        batch = final_tickers[start:start + items_per_page]
        with st.spinner(f"Memuat grafik..."):
            data_grid = get_stock_history_bulk(batch, period=selected_code, interval=selected_interval)
            cols = st.columns(4)
            for i, ticker in enumerate(batch):
                with cols[i % 4]:
                    try:
                        if isinstance(data_grid.columns, pd.MultiIndex):
                            if ticker in data_grid.columns.levels[0]: df = data_grid[ticker].copy()
                            else: df = pd.DataFrame()
                        else: df = data_grid.copy() if len(batch)==1 else pd.DataFrame()
                        
                        if not df.empty:
                            col = 'Close' if 'Close' in df.columns else 'Adj Close'
                            df = df.dropna(subset=[col]).rename(columns={col: 'Close'})
                            if len(df) >= 2:
                                st.plotly_chart(create_mini_chart_complex(df, ticker, selected_code), use_container_width=True, config={'displayModeBar': False})
                                check = st.checkbox(f"Pilih {ticker}", value=(ticker in st.session_state.picked_stocks), key=f"c_{ticker}_{st.session_state.grid_page}")
                                if check and ticker not in st.session_state.picked_stocks: st.session_state.picked_stocks.append(ticker)
                                elif not check and ticker in st.session_state.picked_stocks: st.session_state.picked_stocks.remove(ticker)
                    except: pass
    st.info(f"Keranjang: {len(st.session_state.picked_stocks)} saham. Buka tab '⚖️ Bandingkan'.")

# === TAB 2: BANDINGKAN ===
with tab_compare:
    st.header("⚖️ Bandingkan & Eliminasi")
    picked = st.session_state.picked_stocks
    if picked:
        if st.button("Hapus Semua Pilihan"): st.session_state.picked_stocks = []; st.rerun()
        comp_data = get_stock_history_bulk(picked, period="6mo", interval="1d")
        cols = st.columns(3)
        for i, ticker in enumerate(picked):
            with cols[i % 3]:
                st.divider()
                try:
                    if isinstance(comp_data.columns, pd.MultiIndex): df = comp_data[ticker].dropna()
                    else: df = comp_data.dropna()
                    st.plotly_chart(create_mini_chart_complex(df, ticker, "6mo"), use_container_width=True)
                    if st.button(f"Hapus {ticker}", key=f"del_{ticker}"): 
                        st.session_state.picked_stocks.remove(ticker); st.rerun()
                except: pass
    else: st.warning("Pilih saham dari Tab Grid.")

# === TAB 3: VOLUME ===
with tab_vol:
    st.header("Analisis Volume")
    v_in = st.text_area("Input Saham:", value="BBCA.JK, GOTO.JK")
    if st.button("Analisa Volume"):
        tickers = [t.strip().upper() for t in v_in.split(',')]
        res = get_stock_volume_stats(tickers)
        if res is not None:
            st.dataframe(res.style.format({"Price": "{:,.0f}", "Volume": "{:,.0f}"}), use_container_width=True)

# === TAB 4: WATCHLIST ===
with tab_watch:
    st.header("Watchlist")
    new_w = st.text_input("Tambah Kode:").upper()
    if st.button("Tambah"): 
        if new_w and new_w not in st.session_state.watchlist: 
            st.session_state.watchlist.append(new_w); save_data(); st.rerun()
    st.write(st.session_state.watchlist)

# === TAB 5: DETAIL ===
with tab_detail:
    st.header("Detail Saham")
    d_tick = st.text_input("Kode:", value="BBCA.JK").upper()
    if st.button("Cek Detail"):
        df = get_single_stock_detail(d_tick, "1y")
        if df is not None:
            st.plotly_chart(create_detail_chart(df, d_tick, pd.DataFrame()), use_container_width=True)

# === TAB 6: CYCLE ===
with tab_cycle:
    st.header("Cycle Analysis")
    cy_tick = st.text_input("Saham Cycle:", value="GOTO.JK, BBCA.JK").upper()
    if st.button("Analisa Cycle"):
        res = get_seasonal_details(cy_tick, 1, 12)
        if res:
            for t, data in res.items():
                st.subheader(t)
                fig = go.Figure()
                for y, s in data.items(): fig.add_trace(go.Scatter(y=s, name=y))
                st.plotly_chart(fig)

# === TAB 7: FUNDAMENTAL ===
with tab_fund:
    st.header("Fundamental")
    if st.button("Scan Fundamental"):
        st.write("Fitur ini membutuhkan API Key premium untuk data lengkap.")
        st.dataframe(get_fundamental_screener(GRID_TICKERS[:5]))

# === TAB 8: PERFORMA ===
with tab_perf:
    st.header("Performa")
    p_in = st.text_area("Saham:", value=DEFAULT_INPUT_TXT)
    if st.button("Cek Performa"):
        df = get_performance_matrix(p_in)
        st.dataframe(df)

# === TAB 9: WIN/LOSS ===
with tab_win:
    st.header("Win/Loss Stats (30 Hari)")
    w_in = st.text_area("Saham:", value=DEFAULT_INPUT_TXT, key="wl_in")
    if st.button("Hitung Stat"):
        summ, det = get_win_loss_details(w_in)
        st.dataframe(summ)

# === TAB 10: SIMULATOR ===
with tab_sim:
    st.header("🎯 Simulator & Backtest")
    c1, c2 = st.columns([3, 1])
    with c1: sim_in = st.text_area("Saham:", value="BBCA.JK, GOTO.JK, ANTM.JK")
    with c2: 
        sim_per = st.selectbox("Periode:", ["1mo", "3mo", "6mo"], index=1)
        sim_lot = st.number_input("Lot:", value=100)
    
    if st.button("Jalankan Simulasi"):
        tickers = [t.strip().upper() for t in sim_in.split(',')]
        data = get_stock_history_bulk(tickers, period=sim_per)
        res = []
        for t in tickers:
            try:
                if isinstance(data.columns, pd.MultiIndex): df = data[t].dropna()
                else: df = data.dropna()
                if not df.empty:
                    start = df['Open'].iloc[0]
                    end = df['Close'].iloc[-1]
                    profit = (end - start) * sim_lot * 100
                    res.append({"Ticker": t, "Start": start, "End": end, "Profit": profit, "Return": ((end-start)/start)*100})
            except: pass
        if res:
            st.dataframe(pd.DataFrame(res).style.format({"Start":"{:,.0f}", "End":"{:,.0f}", "Profit":"{:,.0f}", "Return":"{:.2f}%"}))

# === TAB 11: HIGH/LOW ===
with tab_hl:
    st.header("📉 High/Low Analysis")
    hl_in = st.text_input("Saham:", value="BBCA, GOTO")
    if st.button("Analisa HL"):
        ticks = [t.strip().upper() + ".JK" if not t.strip().upper().endswith(".JK") else t.strip().upper() for t in hl_in.split(',')]
        data = get_stock_history_bulk(ticks, period="6mo")
        for t in ticks:
            try:
                if isinstance(data.columns, pd.MultiIndex): df = data[t].dropna()
                else: df = data.dropna()
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(20).mean()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['High'], name='High', line=dict(color='green', dash='dot')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['Low'], name='Low', line=dict(color='red', dash='dot')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='black')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='blue')))
                    fig.update_layout(title=t, height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
            except: pass

