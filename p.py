import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz # Library timezone

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Dashboard Fix", layout="wide")

# --- LIST SAHAM ---
DEFAULT_TICKERS = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'ICBP.JK', 
    'INDF.JK', 'KLBF.JK', 'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK', 'ITMG.JK', 
    'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK', 'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 
    'EXCL.JK', 'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK', 'MNCN.JK', 'SCMA.JK', 
    'GGRM.JK', 'HMSP.JK', 'WIIM.JK', 'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK', 
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK', 'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 
    'UNTR.JK', 'MEDC.JK', 'HRUM.JK', 'TPIA.JK', 'INKP.JK', 'TKIM.JK', 'JPFA.JK', 'MYOR.JK',
    'BUMI.JK', 'ENRG.JK', 'DEWA.JK', 'BRMS.JK', 'ARTO.JK', 'BRIS.JK', 'AGRO.JK', 'BBHI.JK'
]

# --- FUNGSI BANTUAN TIMEZONE ---
def fix_timezone(df):
    """Konversi ke WIB (Asia/Jakarta)"""
    if df.empty: return df
    try:
        # Jika index belum punya timezone, set ke UTC dulu baru convert
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        
        # Convert ke Jakarta
        df.index = df.index.tz_convert('Asia/Jakarta')
    except Exception as e:
        pass # Jika gagal, biarkan apa adanya
    return df

# --- 1. GRAFIK GARIS (5 HARI & 1 BULAN) ---
def plot_dual_axis_line(data, ticker, title_text):
    # Tentukan Baseline (Titik 0%) = Harga Terendah di periode itu
    base_price = data['Close'].min()
    max_price = data['Close'].max()
    
    # Hitung kolom persentase untuk tooltip
    # Rumus: Seberapa persen harga ini dibandingkan harga terendah
    pct_values = ((data['Close'] - base_price) / base_price) * 100
    
    # Warna garis
    color = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    
    # Trace Harga (Sumbu Kiri)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
        name='Harga',
        # Custom Data untuk Hover
        customdata=pct_values,
        hovertemplate=(
            "<b>%{x|%d %b %H:%M}</b><br>" +
            "Harga: Rp %{y:,.0f}<br>" +
            "Posisi: <b>%{customdata:.2f}%</b> dari Low<extra></extra>"
        )
    ))
    
    # LOGIKA DUAL AXIS MANUAL
    # Kita set range sumbu kanan agar sinkron dengan sumbu kiri
    # Jika Harga (Y1) = Base Price, maka Persen (Y2) = 0%
    y_range = [base_price * 0.99, max_price * 1.01] # Padding dikit
    
    # Konversi range harga ke range persen
    y2_min = ((y_range[0] - base_price) / base_price) * 100
    y2_max = ((y_range[1] - base_price) / base_price) * 100
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> <span style='font-size:10px'>({title_text})</span>", x=0),
        margin=dict(l=45, r=40, t=35, b=20),
        height=200,
        showlegend=False,
        hovermode="x unified",
        
        # Sumbu Kiri (Harga)
        yaxis=dict(
            title=None,
            range=y_range,
            showgrid=False,
            side='left',
            tickfont=dict(size=9, color='gray')
        ),
        
        # Sumbu Kanan (Persentase)
        yaxis2=dict(
            title=None,
            range=[y2_min, y2_max], # Sinkronkan
            overlaying='y',
            side='right',
            showgrid=True,
            gridcolor='#eee',
            ticksuffix='%',
            tickfont=dict(size=9, color='gray')
        ),
        xaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

# --- 2. GRAFIK CANDLESTICK (1 HARI) - FIXED ---
def plot_dual_axis_candle(data, ticker):
    # Baseline untuk Intraday = Harga OPEN pagi ini
    open_price = data['Open'].iloc[0]
    
    # Hitung % Change untuk setiap baris (untuk tooltip)
    # Kita masukkan ke string html biar aman dan gak error
    hover_text = []
    for index, row in data.iterrows():
        chg = ((row['Close'] - open_price) / open_price) * 100
        # Format tanggal lokal
        d_str = index.strftime('%d %b %H:%M')
        txt = (f"<b>{d_str}</b><br>"
               f"O: {row['Open']:,.0f}<br>"
               f"H: {row['High']:,.0f}<br>"
               f"L: {row['Low']:,.0f}<br>"
               f"C: {row['Close']:,.0f}<br>"
               f"Chg: <b>{chg:+.2f}%</b>")
        hover_text.append(txt)

    fig = go.Figure()
    
    # Trace Candle
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        increasing_line_color='#00C805',
        decreasing_line_color='#FF3B30',
        name=ticker,
        text=hover_text, # Pakai ini biar gak crash!
        hoverinfo='text' # Suruh plotly baca text di atas
    ))
    
    # SINKRONISASI SUMBU KIRI & KANAN
    y_min = data['Low'].min()
    y_max = data['High'].max()
    padding = (y_max - y_min) * 0.1 if y_max != y_min else y_max * 0.01
    
    # Range Harga (Kiri)
    range_price = [y_min - padding, y_max + padding]
    
    # Range Persen (Kanan) - Relatif terhadap OPEN Price
    range_pct = [
        ((range_price[0] - open_price) / open_price) * 100,
        ((range_price[1] - open_price) / open_price) * 100
    ]

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> <span style='font-size:10px'>{data.index[0].strftime('%d %b %Y')}</span>", 
            x=0
        ),
        margin=dict(l=45, r=40, t=35, b=20),
        height=250,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        hovermode="closest", # Candle lebih enak hover per item
        
        # Y1: Harga
        yaxis=dict(
            title=None,
            side='left',
            showgrid=False,
            range=range_price,
            tickfont=dict(size=9, color='gray')
        ),
        
        # Y2: Persen
        yaxis2=dict(
            title=None,
            side='right',
            overlaying='y',
            showgrid=True,
            gridcolor='#eee',
            range=range_pct, # Range sinkron
            ticksuffix='%',
            tickfont=dict(size=9, color='gray')
        ),
        
        # X: Waktu
        xaxis=dict(
            type='date',
            tickformat='%H:%M',
            showgrid=False
        )
    )
    return fig

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=300)
def get_stock_data(tickers_list, mode):
    all_results = []
    chunk_size = 50 
    
    if mode == "Intraday (1 Hari)":
        period_req, interval_req = "1d", "15m"
    elif mode == "Short Term (5 Hari)":
        period_req, interval_req = "5d", "60m"
    else: 
        period_req, interval_req = "1mo", "1d"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(tickers_list)
    
    for i in range(0, total, chunk_size):
        batch = tickers_list[i : i + chunk_size]
        batch_str = " ".join(batch)
        status_text.text(f"Scanning {mode}... ({i}/{total})")
        progress_bar.progress(min((i + chunk_size) / total, 1.0))
        
        try:
            # Download
            data = yf.download(batch_str, period=period_req, interval=interval_req, group_by='ticker', threads=True, progress=False)
            
            for ticker in batch:
                try:
                    if len(batch) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        hist = data[ticker].dropna()
                    else:
                        hist = data.dropna()
                    
                    if len(hist) > 0:
                        # FIX TIMEZONE
                        hist = fix_timezone(hist)
                        
                        curr = hist['Close'].iloc[-1]
                        
                        # Logic Perhitungan
                        if mode == "Intraday (1 Hari)":
                            op_price = hist['Open'].iloc[0]
                            change = ((curr - op_price) / op_price) * 100
                            # Volatilitas Intraday
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "Intraday"
                            
                        elif mode == "Short Term (5 Hari)":
                            prev = hist['Close'].iloc[0]
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "5 Days"
                            
                        else: # 1 Month
                            prev = hist['Close'].iloc[0]
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "1 Month"

                        all_results.append({
                            'Ticker': ticker.replace('.JK', ''),
                            'Harga': curr,
                            'Change %': change,
                            'Volatilitas': volatility,
                            'Data': hist,
                            'TitleMode': title_mode
                        })
                except: continue
        except: continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_results)

# --- UI UTAMA ---
st.title("📈 Pro Trader Dashboard v3 (Dual Axis)")

# KONTROL
col1, col2 = st.columns([3, 1])
with col1:
    view_mode = st.selectbox("Timeframe:", ["Intraday (1 Hari)", "Short Term (5 Hari)", "History (1 Bulan)"])
with col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# PROSES
df = get_stock_data(DEFAULT_TICKERS, view_mode)

if not df.empty:
    # SORTING
    col_s1, col_s2 = st.columns([2, 2])
    with col_s1:
        sort_opt = st.selectbox("Urutkan:", ["Volatilitas (Range Lebar)", "Top Gainers", "Top Losers"])
    
    if sort_opt == "Volatilitas (Range Lebar)":
        df_display = df.nlargest(20, 'Volatilitas')
    elif sort_opt == "Top Gainers":
        df_display = df.nlargest(20, 'Change %')
    else:
        df_display = df.nsmallest(20, 'Change %')
        
    st.divider()
    
    # GRID LAYOUT
    n_cols = 3 if view_mode == "Intraday (1 Hari)" else 4
    cols = st.columns(n_cols)
    
    for i, (index, row) in enumerate(df_display.iterrows()):
        with cols[i % n_cols]:
            # INFO HEADER
            color_c = "green" if row['Change %'] > 0 else "red"
            st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
            st.markdown(f"<small>Chg: <span style='color:{color_c}'>{row['Change %']:+.2f}%</span> | Volatility: {row['Volatilitas']:.2f}%</small>", unsafe_allow_html=True)
            
            # PLOT CHART
            if view_mode == "Intraday (1 Hari)":
                fig = plot_dual_axis_candle(row['Data'], row['Ticker'])
            else:
                fig = plot_dual_axis_line(row['Data'], row['Ticker'], row['TitleMode'])
                
            st.plotly_chart(fig, use_container_width=True)
            st.write("")
else:
    st.error("Data tidak tersedia. Pastikan market buka atau koneksi aman.")
