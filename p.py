import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Trader Dashboard v2", layout="wide")

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

# --- HELPER: TIMEZONE CONVERSION ---
def fix_timezone(df):
    """Mengubah zona waktu UTC (Yahoo) ke Asia/Jakarta (WIB)"""
    if df.empty: return df
    
    # Cek apakah index sudah punya timezone
    if df.index.tz is None:
        # Jika naive (tidak ada info tz), anggap UTC lalu convert ke Jakarta
        df.index = df.index.tz_localize('UTC').tz_convert('Asia/Jakarta')
    else:
        # Jika sudah aware, langsung convert
        df.index = df.index.tz_convert('Asia/Jakarta')
    return df

# --- 1. GRAFIK DUAL AXIS: LINE (Untuk 5 Hari & 1 Bulan) ---
def plot_dual_axis_line(data, ticker, title_text):
    """
    Kiri: Harga (Rp)
    Kanan: Persentase (%) dari Low Terendah
    """
    min_price = data['Close'].min()
    max_price = data['Close'].max()
    
    # Hitung persentase untuk plotting
    data['Pct_Change'] = ((data['Close'] - min_price) / min_price) * 100
    
    # Warna garis (Hijau jika close > open awal)
    color_line = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    
    # Plot Garis (Kita bind ke sumbu Y Utama/Kiri untuk Harga)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='Harga',
        line=dict(color=color_line, width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(int(color_line.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
        # Custom Hover: Menampilkan Harga & Persentase
        hovertemplate=(
            "<b>%{x|%d %b %H:%M}</b><br>" +
            "Harga: Rp %{y:,.0f}<br>" +
            "Posisi: %{customdata:.2f}% dari Low<extra></extra>"
        ),
        customdata=data['Pct_Change'] # Data tambahan untuk tooltip
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> <span style='font-size:10px'>({title_text})</span>", font=dict(size=14), x=0),
        margin=dict(l=50, r=40, t=40, b=20), # Margin kiri diperbesar untuk angka harga
        height=220,
        showlegend=False,
        hovermode="x unified",
        
        # SUMBU Y KIRI (HARGA)
        yaxis=dict(
            title=None,
            showgrid=False, # Grid ikut yang kanan saja biar ga numpuk
            tickfont=dict(size=9, color='gray'),
            side='left'
        ),
        
        # SUMBU Y KANAN (PERSENTASE)
        # Trik: Kita mapping range harga ke range persentase
        yaxis2=dict(
            title=None,
            overlaying='y',
            side='right',
            showgrid=True,
            gridcolor='#eee',
            ticksuffix='%',
            tickfont=dict(size=9, color='gray'),
            # Sinkronisasi range agar 0% match dengan min_price
            range=[0, ((max_price - min_price)/min_price)*100 * 1.1] # Kasih buffer atas 10%
        ),
        
        # Sumbu X (Waktu)
        xaxis=dict(
            showgrid=False,
            showticklabels=False # Sembunyikan label tanggal biar bersih di grid view
        )
    )
    
    # Trik Sinkronisasi Axis Manual (Agar garis 0% kanan sejajar dengan Harga Low kiri)
    # Di Plotly simple dual axis agak tricky, jadi kita biarkan auto-scale tapi informatif.
    # Versi lebih simple: Biarkan Y1 (Harga) yang menggambar, Y2 cuma visual tick.
    # Tapi karena user minta kiri harga kanan persen, ini layout terbaik.
    
    # Update range Y1 (Harga) agar match visual dengan Y2
    fig.update_layout(yaxis=dict(range=[min_price, max_price * 1.01])) # Buffer dikit
    
    return fig

# --- 2. GRAFIK DUAL AXIS: CANDLESTICK (Untuk 1 Hari) ---
def plot_dual_axis_candle(data, ticker):
    """
    Kiri: Harga (Rp)
    Kanan: Persentase (%) Perubahan dari Harga OPEN hari ini
    """
    open_price = data['Open'].iloc[0] # Harga pembukaan hari ini
    
    # Warna Candle
    inc_color = '#00C805'
    dec_color = '#FF3B30'
    
    fig = go.Figure()
    
    # Candlestick (Bind ke Y1 - Harga)
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        name=ticker,
        increasing_line_color=inc_color,
        decreasing_line_color=dec_color,
        # Hover info lengkap
        tooltip_data=data.apply(
            lambda r: f"Open: {r['Open']:,.0f}<br>High: {r['High']:,.0f}<br>Low: {r['Low']:,.0f}<br>Close: {r['Close']:,.0f}<br>Chg: {((r['Close']-open_price)/open_price)*100:+.2f}%", 
            axis=1
        )
    ))

    # Konfigurasi Range untuk Axis Kanan (Persentase)
    # Kita harus memastikan Range Y1 (Harga) dan Y2 (Persen) sinkron secara matematis
    y_min = data['Low'].min()
    y_max = data['High'].max()
    padding = (y_max - y_min) * 0.1 # 10% padding
    
    range_price = [y_min - padding, y_max + padding]
    
    # Konversi range harga ke range persen relatif terhadap Open Price
    range_pct = [
        ((range_price[0] - open_price) / open_price) * 100,
        ((range_price[1] - open_price) / open_price) * 100
    ]

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> <span style='font-size:10px'>{data.index[0].strftime('%d %b %Y')}</span>", 
            font=dict(size=14), x=0
        ),
        margin=dict(l=50, r=40, t=40, b=20),
        height=250, # Sedikit lebih tinggi buat candle
        showlegend=False,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        
        # Y-Axis 1 (KIRI - HARGA)
        yaxis=dict(
            title=None,
            side='left',
            showgrid=False,
            range=range_price,
            tickfont=dict(size=9, color='gray')
        ),
        
        # Y-Axis 2 (KANAN - PERSENTASE)
        yaxis2=dict(
            title=None,
            side='right',
            overlaying='y',
            showgrid=True,
            gridcolor='#eee',
            range=range_pct, # Range disamakan secara proporsional
            ticksuffix='%',
            tickfont=dict(size=9, color='gray')
        ),
        
        # X-Axis (JAM WIB)
        xaxis=dict(
            type='date',
            tickformat='%H:%M', # Format Jam Menit
            showgrid=False
        )
    )
    return fig

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=300)
def get_stock_data(tickers_list, mode):
    all_results = []
    chunk_size = 50 
    
    # Tentukan Parameter
    if mode == "Intraday (1 Hari)":
        period_req = "1d"
        interval_req = "15m" # Detail candle 15 menit
    elif mode == "Short Term (5 Hari)":
        period_req = "5d"
        interval_req = "60m" # Data 1 jam-an agar garisnya smooth tapi detail
    else: # History 1 Bulan
        period_req = "1mo"
        interval_req = "1d"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(tickers_list)
    
    for i in range(0, total, chunk_size):
        batch = tickers_list[i : i + chunk_size]
        batch_str = " ".join(batch)
        
        status_text.text(f"Mengambil data {mode}... ({i}/{total})")
        progress_bar.progress(min((i + chunk_size) / total, 1.0))
        
        try:
            # Download Data
            data = yf.download(batch_str, period=period_req, interval=interval_req, group_by='ticker', threads=True, progress=False)
            
            for ticker in batch:
                try:
                    if len(batch) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        hist = data[ticker].dropna()
                    else:
                        hist = data.dropna()
                    
                    if len(hist) > 0:
                        # --- FIX TIMEZONE DI SINI ---
                        hist = fix_timezone(hist)
                        
                        curr = hist['Close'].iloc[-1]
                        
                        # Hitung Metrik
                        if mode == "Intraday (1 Hari)":
                            op_price = hist['Open'].iloc[0]
                            change = ((curr - op_price) / op_price) * 100
                            # Volatilitas harian (Range High-Low)
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "Intraday"
                            
                        elif mode == "Short Term (5 Hari)":
                            prev = hist['Close'].iloc[0] # Close 5 hari lalu (awal data)
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "5 Days"
                            
                        else: # 1 Bulan
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
                except Exception as e: continue
        except: continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_results)

# --- UI UTAMA ---
st.title("📈 Pro Trader Dashboard v2")

# 1. KONTROL
col_opt1, col_opt2, col_opt3 = st.columns([2, 1, 2])
with col_opt1:
    view_mode = st.selectbox("Pilih Timeframe:", 
                             ["Intraday (1 Hari)", "Short Term (5 Hari)", "History (1 Bulan)"])

with col_opt2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# 2. LOAD DATA
df = get_stock_data(DEFAULT_TICKERS, view_mode)

if not df.empty:
    
    # 3. SORTING
    col_sort1, col_sort2 = st.columns([2, 2])
    with col_sort1:
        sort_option = st.selectbox("Urutkan:", 
                                   ["Volatilitas (Range Terlebar)", "Top Gainers", "Top Losers"])
    
    if sort_option == "Volatilitas (Range Terlebar)":
        df_display = df.nlargest(20, 'Volatilitas')
    elif sort_option == "Top Gainers":
        df_display = df.nlargest(20, 'Change %')
    else:
        df_display = df.nsmallest(20, 'Change %')
        
    st.divider()
    
    # 4. TAMPILAN GRID
    # Jika Intraday (Candlestick) pake 3 kolom biar lebar, Lainnya 4 kolom
    n_cols = 3 if view_mode == "Intraday (1 Hari)" else 4
    cols = st.columns(n_cols)
    
    for i, (index, row) in enumerate(df_display.iterrows()):
        with cols[i % n_cols]:
            # Header Info
            color_chg = "green" if row['Change %'] > 0 else "red"
            st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
            st.markdown(f"<small>Chg: <span style='color:{color_chg}'>{row['Change %']:+.2f}%</span> | Volatility: {row['Volatilitas']:.2f}%</small>", unsafe_allow_html=True)
            
            # PILIH TIPE CHART
            if view_mode == "Intraday (1 Hari)":
                # Candlestick dengan Dual Axis
                fig = plot_dual_axis_candle(row['Data'], row['Ticker'])
            else:
                # Line Chart (5 Hari / 1 Bulan) dengan Dual Axis
                fig = plot_dual_axis_line(row['Data'], row['Ticker'], row['TitleMode'])
                
            st.plotly_chart(fig, use_container_width=True)
            st.write("")

else:
    st.warning("Data tidak tersedia. Cek koneksi atau market mungkin sedang tutup libur panjang.")
