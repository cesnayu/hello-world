import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Trader Dashboard", layout="wide")

# --- LIST SAHAM DEFAULT ---
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

# --- 1. GRAFIK CANDLESTICK (KHUSUS INTRADAY) ---
def plot_candlestick_chart(data, ticker):
    """
    Menampilkan grafik lilin (Candlestick) untuk melihat High/Low per periode waktu.
    """
    fig = go.Figure()
    
    # Warna: Hijau (Naik), Merah (Turun)
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker,
        increasing_line_color='#00C805', # Hijau Terang
        decreasing_line_color='#FF3B30'  # Merah Terang
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> (Intraday)", font=dict(size=14), x=0),
        margin=dict(l=0, r=10, t=35, b=0),
        height=200,
        showlegend=False,
        xaxis_rangeslider_visible=False, # Hilangkan slider bawah biar rapi
        yaxis=dict(
            side='right',
            showgrid=True,
            gridcolor='#eee',
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            showgrid=False,
            type='date',
            tickformat='%H:%M' # Format Jam:Menit
        )
    )
    return fig

# --- 2. GRAFIK PERSENTASE (KHUSUS HISTORY PANJANG) ---
def plot_percentage_chart(data, ticker):
    """
    Grafik garis basis 0% (Low Terendah).
    """
    min_price = data['Close'].min()
    data['Pct_From_Low'] = ((data['Close'] - min_price) / min_price) * 100
    color = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Pct_From_Low'], mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy', fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}"
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> (1 Month)", font=dict(size=14), x=0),
        margin=dict(l=0, r=35, t=35, b=0),
        height=200,
        showlegend=False,
        yaxis=dict(side='right', showgrid=True, gridcolor='#eee', ticksuffix='%', zeroline=False),
        xaxis=dict(showgrid=False, showticklabels=False),
        hovermode="x unified"
    )
    return fig

# --- FUNGSI AMBIL DATA (DINAMIS) ---
@st.cache_data(ttl=300)
def get_stock_data(tickers_list, mode):
    all_results = []
    chunk_size = 50 
    
    # Tentukan Parameter Download berdasarkan Mode
    if mode == "Intraday (1 Hari)":
        period_req = "1d"
        interval_req = "15m" # Data per 15 menit agar jadi candlestick
    else:
        period_req = "1mo"
        interval_req = "1d"  # Data harian biasa
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(tickers_list)
    
    for i in range(0, total, chunk_size):
        batch = tickers_list[i : i + chunk_size]
        batch_str = " ".join(batch)
        
        status_text.text(f"Mengambil data {mode}... ({i}/{total})")
        progress_bar.progress(min((i + chunk_size) / total, 1.0))
        
        try:
            data = yf.download(batch_str, period=period_req, interval=interval_req, group_by='ticker', threads=True, progress=False)
            
            for ticker in batch:
                try:
                    if len(batch) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        hist = data[ticker].dropna()
                    else:
                        hist = data.dropna()
                    
                    if len(hist) > 1:
                        # Fix Index
                        if not isinstance(hist.index, pd.DatetimeIndex):
                            hist.index = pd.to_datetime(hist.index)
                        
                        curr = hist['Close'].iloc[-1]
                        op = hist['Open'].iloc[0]
                        
                        # Hitung Kenaikan (Logic beda dikit tiap mode)
                        if mode == "Intraday (1 Hari)":
                            change = ((curr - op) / op) * 100 # Change sejak Open pagi ini
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            week_change = 0 # Tidak relevan di mode intraday
                        else:
                            prev = hist['Close'].iloc[-2]
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            # 1 Week Change (Approximation)
                            w_idx = -6 if len(hist) >= 6 else 0
                            week_change = ((curr - hist['Close'].iloc[w_idx]) / hist['Close'].iloc[w_idx]) * 100

                        all_results.append({
                            'Ticker': ticker.replace('.JK', ''),
                            'Harga': curr,
                            'Change %': change,
                            '1W %': week_change,
                            'Volatilitas': volatility,
                            'Data': hist
                        })
                except: continue
        except: continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_results)

# --- UI UTAMA ---
st.title("📈 Super Trader Dashboard")

# 1. KONTROL MODE TAMPILAN
col_opt1, col_opt2, col_opt3 = st.columns([1, 1, 2])
with col_opt1:
    view_mode = st.selectbox("Pilih Timeframe:", ["Intraday (1 Hari)", "History (1 Bulan)"])
with col_opt2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# 2. PROSES DATA
df = get_stock_data(DEFAULT_TICKERS, view_mode)

if not df.empty:
    
    # 3. FILTER & SORTING
    col_sort1, col_sort2 = st.columns([2, 2])
    with col_sort1:
        sort_option = st.selectbox("Urutkan Berdasarkan:", 
                                   ["Volatilitas (Range Terlebar)", "Top Gainers", "Top Losers"])
    
    # Logic Sorting
    if sort_option == "Volatilitas (Range Terlebar)":
        df_display = df.nlargest(20, 'Volatilitas')
    elif sort_option == "Top Gainers":
        df_display = df.nlargest(20, 'Change %')
    else:
        df_display = df.nsmallest(20, 'Change %')
        
    st.divider()
    
    # 4. TAMPILAN GRID
    # Jika Candlestick, kita pakai 3 kolom biar candle-nya gak gepeng
    n_cols = 3 if view_mode == "Intraday (1 Hari)" else 4
    cols = st.columns(n_cols)
    
    for i, (index, row) in enumerate(df_display.iterrows()):
        with cols[i % n_cols]:
            # Info Header
            color_chg = "green" if row['Change %'] > 0 else "red"
            st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
            
            if view_mode == "Intraday (1 Hari)":
                st.markdown(f"<small>Chg: <span style='color:{color_chg}'>{row['Change %']:+.2f}%</span> | Volatility: {row['Volatilitas']:.2f}%</small>", unsafe_allow_html=True)
                # PLOT CANDLESTICK
                fig = plot_candlestick_chart(row['Data'], row['Ticker'])
            else:
                st.markdown(f"<small>1W: {row['1W %']:+.2f}% | Range: {row['Volatilitas']:.1f}%</small>", unsafe_allow_html=True)
                # PLOT PERCENTAGE LINE
                fig = plot_percentage_chart(row['Data'], row['Ticker'])
                
            st.plotly_chart(fig, use_container_width=True)
            st.write("")

else:
    st.warning("Data belum tersedia. Jika market tutup, data intraday mungkin kosong.")
