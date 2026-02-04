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

# --- 2. FUNGSI DATABASE ---
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

# --- 3. INISIALISASI SESSION ---
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

# --- 4. DATA STATIC ---
GRID_TICKERS = [
    "AALI.JK","ACES.JK","ADHI.JK","ADRO.JK","AKRA.JK","AMRT.JK","ANTM.JK","APLN.JK","ARTO.JK","ASII.JK","ASRI.JK","AUTO.JK",
    "BBCA.JK","BBKP.JK","BBNI.JK","BBRI.JK","BBTN.JK","BDMN.JK","BEST.JK","BFIN.JK","BIRD.JK","BJBR.JK","BJTM.JK","BMRI.JK",
    "BMTR.JK","BNGA.JK","BRIS.JK","BRPT.JK","BSDE.JK","BUMI.JK","BYAN.JK","CASA.JK","CENT.JK","CLEO.JK","CPIN.JK","CTRA.JK",
    "DEWA.JK","DILD.JK","DMAS.JK","ELSA.JK","EMTK.JK","ENRG.JK","ERAA.JK","EXCL.JK","FILM.JK","GGRM.JK","GIAA.JK","GJTL.JK",
    "GOTO.JK","HEAL.JK","HERO.JK","HMSP.JK","HRUM.JK","ICBP.JK","INCO.JK","INDF.JK","INDY.JK","INKP.JK","INTP.JK","ISAT.JK",
    "ITMG.JK","JPFA.JK","JRPT.JK","JSMR.JK","KLBF.JK","KPIG.JK","LPCK.JK","LPKR.JK","LPPF.JK","LSIP.JK","MAPI.JK","MDKA.JK",
    "MEDC.JK","MIKA.JK","MNCN.JK","MPPA.JK","MTEL.JK","MYOR.JK","PGAS.JK","PNBN.JK","PNLF.JK","PTBA.JK","PTPP.JK","PWON.JK",
    "RALS.JK","ROTI.JK","SCMA.JK","SIDO.JK","SILO.JK","SIMP.JK","SMGR.JK","SMRA.JK","SRIL.JK","SSIA.JK","TAPG.JK","TBIG.JK",
    "TINS.JK","TKIM.JK","TLKM.JK","TOWR.JK","TPIA.JK","UNTR.JK","UNVR.JK","WIKA.JK","WSKT.JK","WTON.JK","AMMN.JK","BREN.JK",
    "CUAN.JK","MBMA.JK","NCKL.JK","PGEO.JK","VKTR.JK"
]

SAMPLE_SCREENER_TICKERS = GRID_TICKERS
DEFAULT_INPUT_TXT = "BBCA.JK\nBBRI.JK\nGOTO.JK\nADRO.JK"

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
            else: df = data[ticker]; symbol = ticker
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
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
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            
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
                    if isinstance(data.columns, pd.MultiIndex):
                        if t in data.columns.levels[0]: df = data[t]
                        else: continue
                    else:
                        if len(tickers) == 1: df = data 
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
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            if len(item) == 4 and item.isalpha(): item += ".JK"
            tickers.append(item)
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame()

    try:
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False, auto_adjust=False)
    except Exception: return pd.DataFrame()
    
    results = []
    for t in tickers:
        try:
            try: industry = yf.Ticker(t).info.get('industry', '-')
            except: industry = '-'

            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: price_col = 'Close'
            elif 'Adj Close' in df.columns: price_col = 'Adj Close'
            else: continue
            
            df = df[[price_col]].rename(columns={price_col: 'Close'})
            df = df.dropna()
            df.index = df.index.tz_localize(None)
            df = df.sort_index()
            if len(df) < 2: continue
            
            curr_price = float(df['Close'].iloc[-1])
            curr_date = df.index[-1]

            def get_pct_change(days_ago):
                target_date = curr_date - timedelta(days=days_ago)
                past_data = df.loc[df.index <= target_date]
                if past_data.empty: return None
                past_price = float(past_data['Close'].iloc[-1])
                if past_price == 0: return 0.0
                return ((curr_price - past_price) / past_price) * 100

            last_year = curr_date.year - 1
            last_year_end = datetime(last_year, 12, 31)
            ytd_data = df.loc[df.index <= last_year_end]
            if not ytd_data.empty:
                last_year_close = float(ytd_data['Close'].iloc[-1])
                ytd_change = ((curr_price - last_year_close) / last_year_close) * 100
            else: ytd_change = None

            results.append({
                "Ticker": symbol, "Industri": industry, "Harga": curr_price,
                "1 Hari": ((curr_price - df['Close'].iloc[-2])/df['Close'].iloc[-2]) * 100,
                "1 Minggu": get_pct_change(7), "1 Bulan": get_pct_change(30),
                "6 Bulan": get_pct_change(180), "YTD": ytd_change,
                "1 Tahun": get_pct_change(365), "3 Tahun": get_pct_change(365 * 3)
            })
        except Exception: continue
    return pd.DataFrame(results)

@st.cache_data(ttl=600)
def get_win_loss_details(raw_input):
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            if len(item) == 4 and item.isalpha(): item += ".JK"
            tickers.append(item)
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame(), {}

    try:
        data = yf.download(tickers, period="3mo", group_by='ticker', progress=False, auto_adjust=False)
    except: return pd.DataFrame(), {}

    summary_results = []
    detail_data = {} 

    for t in tickers:
        try:
            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: col = 'Close'
            elif 'Adj Close' in df.columns: col = 'Adj Close'
            else: continue

            df['Change'] = df[col].pct_change() * 100
            df = df.dropna()

            df_30 = df.tail(30)
            if len(df_30) < 5: continue 

            detail_data[symbol] = df_30

            green_days = df_30[df_30['Change'] > 0]
            red_days = df_30[df_30['Change'] < 0]

            count_green = len(green_days)
            count_red = len(red_days)
            win_rate = (count_green / len(df_30)) * 100

            avg_gain = green_days['Change'].mean() if not green_days.empty else 0
            avg_loss = red_days['Change'].mean() if not red_days.empty else 0
            total_return_30d = ((df_30[col].iloc[-1] - df_30[col].iloc[0]) / df_30[col].iloc[0]) * 100

            summary_results.append({
                "Ticker": symbol, "Total Candle": len(df_30), "Hari Hijau": count_green, "Hari Merah": count_red,
                "Win Rate": win_rate, "Rata2 Naik": avg_gain, "Rata2 Turun": avg_loss, "Total Return (30 Candle)": total_return_30d
            })
        except: continue
    
    return pd.DataFrame(summary_results), detail_data

# --- 6. VISUALISASI ---

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
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', 
            line=dict(color=color_line, width=1.5), name="Price"
        ), secondary_y=False)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA20'], mode='lines', 
            line=dict(color='#FF9800', width=1), name="MA20"
        ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['Pct'], mode='lines',
        line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'
    ), secondary_y=True)

    if period_code == "3mo":
        one_month_ago = datetime.now(jkt_tz) - timedelta(days=30)
        fig.add_vline(x=one_month_ago, line_width=1, line_dash="dot", line_color="blue")

    fig.update_layout(
        title=dict(text=ticker, font=dict(size=12), x=0.5, xanchor='center'),
        margin=dict(l=5, r=5, t=30, b=5),
        height=200,
        showlegend=False,
        hovermode="x unified"
    )
    
    fig.update_yaxes(title=None, showticklabels=True, tickfont=dict(size=8), secondary_y=False)
    fig.update_yaxes(title=None, showticklabels=True, tickfont=dict(size=8, color='gray'), tickformat=".1f%", secondary_y=True)
    fig.update_xaxes(showticklabels=False)

    return fig

def create_detail_chart(df, ticker, df_fin_filtered):
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        row_heights=[0.5, 0.2, 0.3],
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

# === SIDEBAR MENU ===
st.sidebar.title("Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Fitur:",
    ["📊 Grid Overview", "⚖️ Bandingkan", "🔊 Analisa Volume", "⭐ Watchlist", "🔎 Detail Saham", "🔄 Cycle Analysis", "💎 Fundamental", "🚀 Performa", "🎲 Win/Loss Stats", "🔎 Multi-Chart"]
)

# === PAGE 1: GRID ===
if menu == "📊 Grid Overview":
    st.header("📊 Grid Overview")
    
    with st.expander("🔍 Filter Grid (Harga & Volume)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1: min_p = st.number_input("Min Harga (Rp)", value=0, step=50)
        with c2: max_p = st.number_input("Max Harga (Rp)", value=100000, step=50)
        with c3: min_val_m = st.number_input("Min. Transaksi (Miliar Rp)", value=0, step=1)
        with c4: min_vol_l = st.number_input("Min. Volume (Lot)", value=0, step=1000)
    
    final_tickers = GRID_TICKERS
    is_filtering = (max_p < 100000) or (min_p > 0) or (min_val_m > 0) or (min_vol_l > 0)
    
    if is_filtering:
        with st.spinner("Memfilter saham..."):
            snapshot = get_latest_snapshot(GRID_TICKERS)
            filtered_list = []
            for t, stats in snapshot.items():
                price = stats['price']
                val_miliar = stats['value'] / 1_000_000_000
                vol_lot = stats['volume_lot']
                if (min_p <= price <= max_p) and (val_miliar >= min_val_m) and (vol_lot >= min_vol_l):
                    filtered_list.append(t)
            final_tickers = filtered_list
            st.success(f"Ditemukan {len(final_tickers)} saham sesuai filter.")

    col_tf, col_nav = st.columns([3, 2])
    with col_tf:
        period_label = st.selectbox("Timeframe:", ["1 Hari", "5 Hari", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun", "YTD"], index=3)
        period_map = {"1 Hari": "1d", "5 Hari": "5d", "1 Bulan": "1mo", "3 Bulan": "3mo", "6 Bulan": "6mo", "1 Tahun": "1y", "YTD": "ytd"}
        selected_code = period_map[period_label]
        selected_interval = "5m" if selected_code in ["1d", "5d"] else "1d"

    items_per_page = 12 
    if not final_tickers:
        st.warning("Tidak ada data.")
        total_pages = 1
    else:
        total_pages = math.ceil(len(final_tickers)/items_per_page)

    with col_nav:
        c_prev, c_txt, c_next = st.columns([1, 2, 1])
        with c_prev:
            if st.button("⬅️") and st.session_state.grid_page > 1:
                st.session_state.grid_page -= 1
        with c_next:
            if st.button("➡️") and st.session_state.grid_page < total_pages:
                st.session_state.grid_page += 1
        with c_txt:
            st.write(f"Hal {st.session_state.grid_page} dari {total_pages}")

    if final_tickers:
        start = (st.session_state.grid_page - 1) * items_per_page
        end = start + items_per_page
        batch = final_tickers[start:end]
        
        def toggle_pick(ticker):
            if ticker in st.session_state.picked_stocks:
                st.session_state.picked_stocks.remove(ticker)
            else:
                st.session_state.picked_stocks.append(ticker)

        with st.spinner(f"Memuat grafik {period_label}..."):
            data_grid = get_stock_history_bulk(batch, period=selected_code, interval=selected_interval)
            
            if not data_grid.empty:
                cols = st.columns(4) 
                for i, ticker in enumerate(batch):
                    col_idx = i % 4
                    with cols[col_idx]:
                        try:
                            df_target = pd.DataFrame()
                            if isinstance(data_grid.columns, pd.MultiIndex):
                                if ticker in data_grid.columns.levels[0]: df_target = data_grid[ticker].copy()
                            else:
                                if len(batch) == 1: df_target = data_grid.copy()
                            
                            if df_target.empty:
                                st.caption(f"❌ {ticker}")
                                continue
                            
                            if 'Close' not in df_target.columns and 'Adj Close' in df_target.columns:
                                df_target = df_target.rename(columns={'Adj Close': 'Close'})
                            
                            df_target = df_target.dropna(subset=['Close'])
                            min_pts = 5 if selected_code != "1d" else 2
                            
                            if len(df_target) >= min_pts:
                                fig = create_mini_chart_complex(df_target, ticker, selected_code)
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                                is_checked = ticker in st.session_state.picked_stocks
                                st.checkbox(f"Pilih {ticker}", value=is_checked, key=f"chk_{ticker}_{st.session_state.grid_page}", on_change=toggle_pick, args=(ticker,))
                            else:
                                st.caption(f"⚠️ {ticker} (No Data)")
                        except Exception as e:
                            st.caption(f"Error {ticker}")

    st.info(f"🛒 Keranjang Pilihan: {len(st.session_state.picked_stocks)} saham. Buka menu '⚖️ Bandingkan'.")

# === PAGE 2: BANDINGKAN ===
elif menu == "⚖️ Bandingkan":
    st.header("⚖️ Bandingkan & Eliminasi")
    picked = st.session_state.picked_stocks
    if not picked:
        st.warning("Belum ada saham yang dipilih dari Menu '📊 Grid'.")
    else:
        st.write(f"Membandingkan **{len(picked)}** saham pilihanmu.")
        if st.button("🗑️ Hapus Semua Pilihan"):
            st.session_state.picked_stocks = []
            st.rerun()
        with st.spinner("Mengambil data detail..."):
            comp_data = get_stock_history_bulk(picked, period="6mo", interval="1d")
            comp_cols = st.columns(3) 
            for i, ticker in enumerate(picked):
                c_idx = i % 3
                with comp_cols[c_idx]:
                    st.divider()
                    try:
                        df_c = pd.DataFrame()
                        if isinstance(comp_data.columns, pd.MultiIndex):
                            if ticker in comp_data.columns.levels[0]: df_c = comp_data[ticker].copy()
                        else:
                            if len(picked) == 1: df_c = comp_data.copy()
                        
                        if not df_c.empty:
                            df_c = df_c.dropna()
                            fig = create_mini_chart_complex(df_c, ticker, "6mo") 
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            if st.button(f"❌ Hapus {ticker}", key=f"del_{ticker}"):
                                st.session_state.picked_stocks.remove(ticker)
                                st.rerun()
                    except: st.error(f"Gagal load {ticker}")

# === PAGE 3: VOLUME ===
elif menu == "🔊 Analisa Volume":
    st.header("Analisis Volume")
    
    default_text = ", ".join(st.session_state.vol_saved_tickers)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        vol_input = st.text_area("Input Saham:", value=default_text, height=70, placeholder="Misal: BBCA, GOTO", key="vol_in_multi")
    with c2:
        st.write("")
        vol_period = st.selectbox("Rentang Waktu:", ["1 Hari", "1 Minggu", "1 Bulan", "YTD"], index=2)
        vol_period_map = {"1 Hari": "1d", "1 Minggu": "5d", "1 Bulan": "1mo", "YTD": "ytd"}
        selected_vol_period = vol_period_map[vol_period]
        
    c3, c4, c5 = st.columns([1, 1, 1])
    with c3:
        btn_custom = st.button("🔍 Analisa Input", use_container_width=True)
    with c4:
        btn_top20 = st.button("🔥 Top 20 Volume", use_container_width=True)
    with c5:
        if st.button("🗑️ Hapus List", use_container_width=True):
            st.session_state.vol_saved_tickers = []
            save_data()
            st.rerun()

    df_vol_result = pd.DataFrame()

    if btn_custom and vol_input:
        raw_list = vol_input.replace('\n', ',').replace(' ', ',').split(',')
        clean_list = []
        for t in raw_list:
            item = t.strip().upper()
            if item:
                if len(item) == 4 and item.isalpha(): item += ".JK"
                clean_list.append(item)
        if clean_list:
            st.session_state.vol_saved_tickers = list(set(clean_list))
            save_data()
            with st.spinner("Menganalisa input..."):
                df_vol_result = get_stock_volume_stats(list(set(clean_list)), period_code=selected_vol_period)
                st.session_state['vol_result'] = df_vol_result 
                st.rerun()

    elif btn_top20:
        with st.spinner("Scanning Top 20 Volume..."):
            df_all = get_stock_volume_stats(GRID_TICKERS, period_code=selected_vol_period)
            if df_all is not None and not df_all.empty:
                df_vol_result = df_all.sort_values(by="Volume", ascending=False).head(20)
                st.session_state['vol_result'] = df_vol_result

    if 'vol_result' in st.session_state and not st.session_state['vol_result'].empty:
        df_show = st.session_state['vol_result']
        st.divider()
        st.subheader(f"Hasil Analisa Volume ({vol_period})")
        
        sort_col = st.radio("Urutkan berdasarkan:", ["Volume", "Est. Value", "Vol vs Avg"], horizontal=True)
        if sort_col == "Volume": df_show = df_show.sort_values(by="Volume", ascending=False)
        elif sort_col == "Est. Value": df_show = df_show.sort_values(by="Est. Value", ascending=False)
        elif sort_col == "Vol vs Avg": df_show = df_show.sort_values(by="Vol vs Avg", ascending=False)
        
        def highlight_vol_spike(val):
            color = '#d4f7d4' if val >= 1.5 else ''
            return f'background-color: {color}'
            
        st.dataframe(df_show.style.format({
                "Price": "{:,.0f}",
                "Change %": "{:+.2f}%",
                "Volume": "{:,.0f}", 
                "Avg Vol (5D)": "{:,.0f}", 
                "Est. Value": "Rp {:,.0f}", 
                "Vol vs Avg": "{:.2f}x"
            }).applymap(highlight_vol_spike, subset=['Vol vs Avg']), use_container_width=True, hide_index=True)

# === PAGE 4: WATCHLIST ===
elif menu == "⭐ Watchlist":
    st.header("Watchlist Saya")
    ci, cb = st.columns([3, 1])
    with ci: nt = st.text_input("Kode:", key="sb").strip().upper()
    with cb: 
        st.write(""); st.write("")
        if st.button("➕ Tambah"): 
            if nt and nt not in st.session_state.watchlist: st.session_state.watchlist.append(nt); save_data(); st.rerun()
    cw = st.session_state.watchlist
    if cw:
        if st.button("🗑️ Hapus Semua"): st.session_state.watchlist = []; save_data(); st.rerun()
        ew = st.multiselect("Edit:", options=cw, default=cw)
        if len(ew) != len(cw): st.session_state.watchlist = ew; save_data(); st.rerun()
        with st.spinner("Load..."):
            dw = get_stock_history_bulk(cw, period="3mo", interval="1d")
            if not dw.empty: 
                w_cols = st.columns(4)
                for i, ticker in enumerate(cw):
                    with w_cols[i % 4]:
                        try:
                            df = pd.DataFrame()
                            if isinstance(dw.columns, pd.MultiIndex):
                                if ticker in dw.columns.levels[0]: df = dw[ticker].copy()
                            else:
                                if len(cw) == 1: df = dw.copy()
                            
                            if not df.empty:
                                df = df.dropna()
                                fig = create_mini_chart_complex(df, ticker, "3mo")
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        except: pass

# === PAGE 5: DETAIL ===
elif menu == "🔎 Detail Saham":
    st.header("🔎 Analisa Saham Mendalam")
    col_search, col_period = st.columns([2, 3])
    with col_search:
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input("Ketik Kode Saham:", value=default_ticker, key="detail_input").strip().upper()
    with col_period:
        period_options = ["1d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        period_labels = {"1d": "1 Hari", "1mo": "1 Bulan", "3mo": "3 Bulan", "6mo": "6 Bulan", "1y": "1 Tahun", "2y": "2 Tahun", "5y": "5 Tahun", "max": "Sejak IPO"}
        selected_period_code = st.select_slider("Pilih Rentang Waktu:", options=period_options, value="1y", format_func=lambda x: period_labels[x])
    st.divider()
    if detail_ticker:
        with st.spinner(f"Mengambil data {detail_ticker}..."):
            df_detail = get_single_stock_detail(detail_ticker, selected_period_code)
            fund_info = get_fundamental_info(detail_ticker)
            if df_detail is not None and not df_detail.empty:
                last_row = df_detail.iloc[-1]
                prev_row = df_detail.iloc[-2] if len(df_detail) > 1 else last_row
                change = last_row['Close'] - prev_row['Close']
                pct_change = (change / prev_row['Close']) * 100
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Harga", f"{last_row['Close']:,.0f}", f"{pct_change:.2f}%")
                m2.metric("Volume", f"{last_row['Volume']:,.0f}")
                m3.metric("High", f"{df_detail['High'].max():,.0f}")
                if fund_info:
                    m4.metric("Market Cap", f"{fund_info['mkt_cap']:,.0f}" if fund_info['mkt_cap'] else "-")
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("PER (TTM)", f"{fund_info['per']:.2f}x" if fund_info['per'] else "-")
                    f2.metric("PBV", f"{fund_info['pbv']:.2f}x" if fund_info['pbv'] else "-")
                    f3.metric("EPS (TTM)", f"{fund_info['eps']:.2f}" if fund_info['eps'] else "-")
                    f4.metric("Industri", fund_info['sector'])
                q_fin, a_fin = get_financials_history(detail_ticker)
                is_long_term = selected_period_code in ["2y", "5y", "max"]
                df_fin_use = a_fin if is_long_term and not a_fin.empty else q_fin
                if df_fin_use.empty: df_fin_use = q_fin if not q_fin.empty else a_fin
                start_date_chart = df_detail['Date'].min()
                if not df_fin_use.empty: df_fin_filtered = df_fin_use[df_fin_use.index >= start_date_chart]
                else: df_fin_filtered = pd.DataFrame()
                st.plotly_chart(create_detail_chart(df_detail, detail_ticker, df_fin_filtered), use_container_width=True)
            else: st.error("Data tidak ditemukan.")

# === PAGE 6: CYCLE ===
elif menu == "🔄 Cycle Analysis":
    st.header("🔄 Cycle Analysis")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        def_t = ", ".join(st.session_state.watchlist[:2]) if st.session_state.watchlist else "GOTO.JK, BBCA.JK"
        cycle_tickers = st.text_input("Saham:", value=def_t, key="cycle_in").strip().upper()
    with c2:
        month_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"Mei", 6:"Jun", 7:"Jul", 8:"Agust", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Des"}
        start_m = st.selectbox("Dari:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=10) 
        end_m = st.selectbox("Sampai:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=3)
    with c3:
        years_lookback = st.slider("Tahun:", 3, 10, 5)
        st.write(""); 
        if st.button("🚀 Bandingkan", key="btn_cycle"):
            with st.spinner("Menganalisa..."):
                st.session_state['cycle_data'] = get_seasonal_details(cycle_tickers, start_m, end_m, years_lookback)
    st.divider()
    if 'cycle_data' in st.session_state and st.session_state['cycle_data']:
        results_dict = st.session_state['cycle_data']
        if results_dict:
            cols = st.columns(2)
            for idx, (ticker, years_data) in enumerate(results_dict.items()):
                with cols[idx % 2]:
                    fig = go.Figure()
                    sorted_years = sorted(years_data.keys(), reverse=True)
                    my_colors = ['black', 'blue', 'red', 'green'] 
                    for i, year_label in enumerate(sorted_years):
                        series = years_data[year_label]
                        chosen_color = my_colors[i % len(my_colors)]
                        is_current = str(datetime.now().year) in year_label
                        width = 3 if is_current else 1.5
                        fig.add_trace(go.Scatter(y=series, mode='lines', name=year_label, line=dict(width=width, color=chosen_color)))
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                    fig.update_layout(title=f"<b>{ticker}</b>", xaxis_title="Hari", yaxis_title="Gain/Loss (%)", hovermode="x unified", height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else: st.warning("Data tidak cukup.")

# === PAGE 7: FUNDAMENTAL ===
elif menu == "💎 Fundamental":
    st.header("💎 Fundamental & Classification Screener")
    user_screener_input = st.text_area("Input Saham (Pisahkan koma):", value=DEFAULT_INPUT_TXT, height=100)
    col_run, col_export = st.columns([1, 5])
    with col_run: 
        if st.button("🔍 Scan Fundamental", key="btn_fund"):
            tickers_to_scan = [t.strip().upper() for t in user_screener_input.split(',') if t.strip()]
            st.write(f"Sedang mengambil data fundamental untuk {len(tickers_to_scan)} saham...")
            st.session_state['fund_data'] = get_fundamental_screener(tickers_to_scan)
    st.divider()
    if 'fund_data' in st.session_state and not st.session_state['fund_data'].empty:
        df_fund = st.session_state['fund_data']
        unique_industries = df_fund["Industry"].unique()
        for industry in sorted(unique_industries):
            df_sub = df_fund[df_fund["Industry"] == industry].copy().drop(columns=["Industry"])
            st.subheader(f"🏭 {industry}")
            st.dataframe(df_sub, use_container_width=True, hide_index=True, column_config={
                    "Price": st.column_config.NumberColumn("Price", format="Rp %.0f"),
                    "52W High": st.column_config.NumberColumn("52W High", format="Rp %.0f"),
                    "52W Low": st.column_config.NumberColumn("52W Low", format="Rp %.0f"),
                    "PBV": st.column_config.NumberColumn("PBV", format="%.2fx"),
                    "PER": st.column_config.NumberColumn("PER", format="%.2fx"),
                    "EPS": st.column_config.NumberColumn("EPS", format="%.2f")})
            st.write("")

# === PAGE 8: PERFORMANCE ===
elif menu == "🚀 Performa":
    st.header("🚀 Tabel Performa Saham")
    perf_tickers_input = st.text_area("Input Saham:", value=DEFAULT_INPUT_TXT, height=100, key="perf_in_main")
    if st.button("Hitung Performa", key="btn_perf"):
        with st.spinner("Mengambil Data & Metadata..."):
            st.session_state['perf_data'] = get_performance_matrix(perf_tickers_input)
    if 'perf_data' in st.session_state and not st.session_state['perf_data'].empty:
        df_perf = st.session_state['perf_data']
        pct_fmt = st.column_config.NumberColumn(format="%.2f%%")
        def color_negative_red(val):
            if val is None or pd.isna(val): return 'color: gray'
            color = '#00C805' if val > 0 else '#FF333A' if val < 0 else 'black'
            return f'color: {color}; font-weight: bold'
        styled_df = df_perf.style.format({
            "1 Hari": "{:.2f}", "1 Minggu": "{:.2f}", "1 Bulan": "{:.2f}",
            "6 Bulan": "{:.2f}", "YTD": "{:.2f}", "1 Tahun": "{:.2f}", "3 Tahun": "{:.2f}"
        }).applymap(color_negative_red, subset=["1 Hari", "1 Minggu", "1 Bulan", "6 Bulan", "YTD", "1 Tahun", "3 Tahun"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config={
                "Ticker": st.column_config.TextColumn("Kode"),
                "Industri": st.column_config.TextColumn("Industri"), 
                "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                "1 Hari": pct_fmt, "1 Minggu": pct_fmt, "1 Bulan": pct_fmt,
                "6 Bulan": pct_fmt, "YTD": pct_fmt, "1 Tahun": pct_fmt, "3 Tahun": pct_fmt})

# === PAGE 9: WIN/LOSS & SIMULATOR ===
elif menu == "🎲 Win/Loss Stats":
    st.title("🎲 Analisa Win/Loss & Simulator")
    
    # Sub-tabs
    wl_tab1, wl_tab2 = st.tabs(["📅 Probabilitas Harian (30 Hari)", "⚙️ Advanced Simulator (Backtest)"])
    
    # --- SUB-TAB 1: PROBABILITAS HARIAN ---
    with wl_tab1:
        st.subheader("Probabilitas Harian (30 Hari Terakhir)")
        win_input = st.text_area("Input Saham (Harian):", value=DEFAULT_INPUT_TXT, height=100, key="win_in")
        
        if st.button("Hitung Probabilitas", key="btn_win"):
            with st.spinner("Menganalisis data harian..."):
                summary_df, detail_dict = get_win_loss_details(win_input)
                st.session_state['win_summary'] = summary_df
                st.session_state['win_details'] = detail_dict
                
        if 'win_summary' in st.session_state and not st.session_state['win_summary'].empty:
            st.write("### Rangkuman Statistik")
            df_win = st.session_state['win_summary']
            def highlight_win(val):
                color = '#d4f7d4' if val >= 60 else '#f7d4d4' if val <= 40 else ''
                return f'background-color: {color}'
            st.dataframe(df_win.style.format({
                    "Win Rate": "{:.1f}%", "Rata2 Naik": "+{:.2f}%", "Rata2 Turun": "{:.2f}%", "Total Return (30 Candle)": "{:.2f}%"
                }).applymap(highlight_win, subset=['Win Rate']), use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("### 🗓️ Detail Pergerakan Harian (Grid 30 Hari)")
            detail_data = st.session_state['win_details']
            
            st.markdown("""
            <style>
            .day-box {
                display: inline-block; width: 70px; height: 70px; margin: 4px; padding: 8px 2px;
                border-radius: 8px; text-align: center; color: white; font-family: sans-serif;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            }
            .day-date { font-size: 10px; margin-bottom: 4px; opacity: 0.9; font-weight: bold; }
            .day-val { font-size: 13px; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)

            for ticker, df_30 in detail_data.items():
                with st.expander(f"📊 {ticker} - Detail 30 Hari", expanded=True):
                    html_code = "<div style='display: flex; flex-wrap: wrap;'>"
                    for date, row in df_30.iterrows():
                        val = row['Change']
                        color = "#00C805" if val >= 0 else "#FF333A"
                        date_str = date.strftime("%d %b")
                        val_str = f"{val:+.2f}%"
                        html_code += f"<div class='day-box' style='background-color: {color};'><div class='day-date'>{date_str}</div><div class='day-val'>{val_str}</div></div>"
                    html_code += "</div>"
                    st.markdown(html_code, unsafe_allow_html=True)

    # --- SUB-TAB 2: ADVANCED SIMULATOR ---
    with wl_tab2:
        st.subheader("🎲 Advanced Win Rate & Backtest Simulator")
        
        # 1. Kontrol Input Simulator
        col_sim1, col_sim2, col_sim3 = st.columns([2, 1, 1])
        with col_sim1:
            def_sim = "BBCA.JK, BBRI.JK, BMRI.JK, ADRO.JK, GOTO.JK, ANTM.JK"
            sim_tickers_input = st.text_area("Daftar Saham (Pisahkan koma):", value=def_sim, height=100)
        with col_sim2:
            sim_period = st.selectbox("Rentang Waktu Simulasi:", ["1 Minggu", "1 Bulan", "3 Bulan"], index=1)
            period_map = {"1 Minggu": "5d", "1 Bulan": "1mo", "3 Bulan": "3mo"}
            yf_period = period_map[sim_period]
        with col_sim3:
            sim_lot = st.number_input("Simulasi Jumlah Lot:", min_value=1, value=100, step=10)
            chart_type = st.radio("Tipe Grafik:", ["Return (%)", "Harga (Rp)"], horizontal=True)

        run_sim = st.button("🚀 Jalankan Simulasi")

        # 2. Logika Proses Simulator
        if run_sim:
            with st.spinner("Mengambil data historis & menghitung probabilitas..."):
                tickers = [x.strip().upper() for x in sim_tickers_input.split(',') if x.strip()]
                tickers = [t if t.endswith('.JK') else t + '.JK' for t in tickers]
                
                # Download Data
                data = yf.download(tickers, period=yf_period, group_by='ticker', progress=False, auto_adjust=False)
                sim_results = []
                
                for t in tickers:
                    try:
                        if len(tickers) > 1:
                            if isinstance(data.columns, pd.MultiIndex):
                                if t not in data.columns.levels[0]: continue
                            hist = data[t].dropna()
                        else:
                            hist = data.dropna()
                        
                        if len(hist) > 0:
                            start_price = hist['Open'].iloc[0]
                            end_price = hist['Close'].iloc[-1]
                            change_pct = ((end_price - start_price) / start_price) * 100
                            status = "WIN" if change_pct > 0 else "LOSS"
                            profit_rp = (end_price - start_price) * sim_lot * 100
                            
                            sim_results.append({
                                'Add': False,
                                'Ticker': t.replace('.JK', ''),
                                'Start Price': start_price,
                                'End Price': end_price,
                                'Return (%)': change_pct,
                                'Est. Profit (Rp)': profit_rp,
                                'Status': status,
                                'Data': hist
                            })
                    except: continue
                
                st.session_state['sim_results'] = sim_results

        # 3. Tampilkan Hasil Simulator
        if 'sim_results' in st.session_state and st.session_state['sim_results']:
            results = st.session_state['sim_results']
            df_sim = pd.DataFrame(results)
            
            total_trades = len(df_sim)
            wins = len(df_sim[df_sim['Status'] == 'WIN'])
            win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
            total_pnl = df_sim['Est. Profit (Rp)'].sum()
            
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}/{total_trades} Win")
            m2.metric("Total Estimasi PnL", f"Rp {total_pnl:,.0f}", help=f"Asumsi {sim_lot} Lot per saham")
            m3.metric("Periode Analisa", sim_period)
            
            # Interactive Table
            st.write("### 📋 Detail Performa")
            col_cfg = {
                "Add": st.column_config.CheckboxColumn("Add to Watchlist", default=False),
                "Ticker": st.column_config.TextColumn("Saham", disabled=True),
                "Start Price": st.column_config.NumberColumn("Harga Awal", format="Rp %d"),
                "End Price": st.column_config.NumberColumn("Harga Akhir", format="Rp %d"),
                "Return (%)": st.column_config.NumberColumn("Return", format="%.2f%%"),
                "Est. Profit (Rp)": st.column_config.NumberColumn("Profit/Loss", format="Rp %d"),
                "Status": st.column_config.TextColumn("Status"),
            }
            
            edited_df = st.data_editor(
                df_sim[['Add', 'Ticker', 'Start Price', 'End Price', 'Return (%)', 'Est. Profit (Rp)', 'Status']],
                column_config=col_cfg,
                hide_index=True,
                use_container_width=True,
                disabled=['Ticker', 'End Price', 'Return (%)', 'Est. Profit (Rp)', 'Status']
            )
            
            selected_rows = edited_df[edited_df['Add'] == True]
            if not selected_rows.empty:
                new_watch_items = [t + ".JK" for t in selected_rows['Ticker'].tolist()]
                current_wl = st.session_state.get('watchlist', [])
                updated_wl = list(set(current_wl + new_watch_items))
                st.session_state.watchlist = updated_wl
                save_data()
                st.success(f"✅ {len(new_watch_items)} saham ditambahkan ke Watchlist!")

            # Chart Simulation
            st.write(f"### 📈 Grafik Pergerakan ({chart_type})")
            fig_sim = go.Figure()
            for item in results:
                hist_data = item['Data']
                ticker_name = item['Ticker']
                if chart_type == "Return (%)":
                    start_val = hist_data['Close'].iloc[0]
                    y_data = ((hist_data['Close'] - start_val) / start_val) * 100
                    hover_temp = "<b>%{x|%d %b}</b><br>Return: %{y:.2f}%"
                    y_suffix = "%"
                else:
                    y_data = hist_data['Close']
                    hover_temp = "<b>%{x|%d %b}</b><br>Harga: Rp %{y:,.0f}"
                    y_suffix = ""
                
                line_color = '#00C805' if item['Return (%)'] > 0 else '#FF3B30'
                fig_sim.add_trace(go.Scatter(x=hist_data.index, y=y_data, mode='lines', name=ticker_name, line=dict(width=2, color=line_color), hovertemplate=hover_temp))
            
            fig_sim.update_layout(height=400, hovermode="x unified", yaxis=dict(ticksuffix=y_suffix, gridcolor='#eee'), xaxis=dict(showgrid=False), margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_sim, use_container_width=True)

# === PAGE 10: MULTI CHART (NEW) ===
elif menu == "🔎 Multi-Chart":
    st.header("🔎 Analisa Grafik Multi-Saham")
    
    col_mc1, col_mc2, col_mc3 = st.columns([3, 1, 1])
    with col_mc1:
        def_mc = "BBCA, ADRO, GOTO, TLKM"
        mc_input = st.text_input("Masukkan Kode Saham (Pisahkan koma, tanpa .JK):", value=def_mc)
    with col_mc2:
        mc_tf = st.selectbox("Rentang Waktu:", ["1 Hari", "1 Minggu", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun"], index=2)
    with col_mc3:
        run_mc = st.button("Tampilkan Grafik")

    if run_mc or mc_input:
        tf_map = {
            "1 Hari":   {"p": "1d", "i": "15m"}, 
            "1 Minggu": {"p": "5d",  "i": "60m"}, 
            "1 Bulan":  {"p": "1mo", "i": "1d"},
            "3 Bulan":  {"p": "3mo", "i": "1d"},
            "6 Bulan":  {"p": "6mo", "i": "1d"},
            "1 Tahun":  {"p": "1y",  "i": "1d"},
        }
        params = tf_map[mc_tf]
        
        raw_tickers = [x.strip().upper() for x in mc_input.split(',')]
        clean_tickers = [t + ".JK" if not t.endswith(".JK") else t for t in raw_tickers if t]
        
        if clean_tickers:
            with st.spinner(f"Mengambil data {mc_tf} untuk {len(clean_tickers)} saham..."):
                try:
                    data = yf.download(" ".join(clean_tickers), period=params['p'], interval=params['i'], group_by='ticker', progress=False)
                except Exception as e:
                    st.error(f"Gagal mengambil data: {e}")
                    data = pd.DataFrame()

            for ticker in clean_tickers:
                try:
                    if len(clean_tickers) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        df = data[ticker].dropna()
                    else:
                        df = data.dropna()
                    
                    if len(df) > 0:
                        jkt_tz = pytz.timezone('Asia/Jakarta')
                        if df.index.tz is None: df.index = df.index.tz_localize('UTC')
                        df.index = df.index.tz_convert(jkt_tz)
                        
                        df['MA20'] = df['Close'].rolling(window=20).mean()
                        
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                            increasing_line_color='#00C805', decreasing_line_color='#FF3B30', name='Harga'
                        ))
                        fig.add_trace(go.Scatter(
                            x=df.index, y=df['MA20'], mode='lines', 
                            line=dict(color='#FFA500', width=1.5), name='MA 20'
                        ))
                        
                        curr_price = df['Close'].iloc[-1]
                        chg_pct = ((curr_price - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
                        
                        fig.update_layout(
                            title=dict(text=f"<b>{ticker.replace('.JK','')}</b> : Rp {curr_price:,.0f} ({chg_pct:+.2f}%)", x=0, font=dict(size=16)),
                            height=350, xaxis_rangeslider_visible=False, hovermode="x unified",
                            margin=dict(l=10, r=10, t=40, b=10),
                            yaxis=dict(showgrid=True, gridcolor='#eee'),
                            xaxis=dict(showgrid=False, type='date', tickformat='%H:%M' if mc_tf in ["1 Hari", "1 Minggu"] else '%d %b')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.divider()
                except Exception as e: continue
        else:
            st.warning("Masukkan setidaknya satu kode saham.")
