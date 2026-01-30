import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Dashboard - Percentage View", layout="wide")

# --- LIST SAHAM (DEFAULT) ---
# Bisa kamu update sesuai kebutuhan
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

# --- FUNGSI CHART KHUSUS (PERSENTASE BASIS 0%) ---
def plot_percentage_chart(data, ticker):
    """
    Membuat grafik dimana titik terendah (Low) dianggap 0%.
    Sumbu Y kanan menunjukkan seberapa persen kenaikan dari titik terendah itu.
    """
    # 1. Tentukan Titik Terendah (Baseline)
    min_price = data['Close'].min()
    
    # 2. Konversi Harga ke Persentase Kenaikan dari Titik Terendah
    # Rumus: ((Harga - Terendah) / Terendah) * 100
    # Hasilnya: Titik terendah jadi 0, titik lain jadi positif (misal 5.2%)
    data['Pct_From_Low'] = ((data['Close'] - min_price) / min_price) * 100
    
    # Tentukan warna (Hijau jika close > open awal, Merah jika turun)
    color = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Pct_From_Low'],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy', # Isi area bawah biar kelihatan volumenya
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}", # Transparan
        hovertemplate='<b>%{y:.2f}%</b> dari Low<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b>",
            font=dict(size=14),
            x=0
        ),
        margin=dict(l=0, r=40, t=35, b=0), # Margin kanan r=40 untuk angka axis
        height=180,
        showlegend=False,
        # --- LOGIKA SUMBU Y PERSENTASE ---
        yaxis=dict(
            side='right',       # Angka di KANAN
            showgrid=True,      # Tampilkan garis mendatar
            gridcolor='#eee',   # Warna garis tipis
            ticksuffix='%',     # Tambah tanda %
            zeroline=False,
            tickfont=dict(size=10, color='gray')
        ),
        xaxis=dict(
            showgrid=False,
            showticklabels=False # Sembunyikan tanggal biar bersih
        ),
        hovermode="x unified"
    )
    
    return fig

# --- FUNGSI AMBIL DATA (BATCHING BIAR CEPAT) ---
@st.cache_data(ttl=600)
def get_stock_data_batch(tickers_list):
    all_results = []
    chunk_size = 50 
    
    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_tickers = len(tickers_list)
    
    for i in range(0, total_tickers, chunk_size):
        batch_tickers = tickers_list[i : i + chunk_size]
        batch_str = " ".join(batch_tickers)
        
        status_text.text(f"Scanning... ({i}/{total_tickers})")
        progress_bar.progress(min((i + chunk_size) / total_tickers, 1.0))
        
        try:
            # Ambil data 1 Bulan (agar grafik terlihat trennya)
            data = yf.download(batch_str, period='1mo', group_by='ticker', threads=True, progress=False)
            
            for ticker in batch_tickers:
                try:
                    # Handling MultiIndex Dataframe
                    if len(batch_tickers) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        hist = data[ticker].dropna()
                    else:
                        hist = data.dropna()
                    
                    if len(hist) > 5:
                        # Fix Index
                        if not isinstance(hist.index, pd.DatetimeIndex):
                            hist.index = pd.to_datetime(hist.index)
                        
                        # Data Harga
                        curr_price = hist['Close'].iloc[-1]
                        
                        # Perubahan 1 Hari
                        prev_close = hist['Close'].iloc[-2]
                        day_change = ((curr_price - prev_close) / prev_close) * 100
                        
                        # Perubahan 1 Minggu (5 hari bursa)
                        week_close = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
                        week_change = ((curr_price - week_close) / week_close) * 100
                        
                        # Volatilitas Range (High-Low)
                        range_pct = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                        
                        all_results.append({
                            'Ticker': ticker.replace('.JK', ''),
                            'Harga': curr_price,
                            'Hari Ini %': day_change,
                            '1 Minggu %': week_change,
                            'Volatilitas': range_pct,
                            'Data': hist # Simpan data untuk grafik
                        })
                except:
                    continue
        except:
            continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_results)

# --- FITUR DOWNLOAD EXCEL ---
def generate_excel(df_results):
    output = io.BytesIO()
    all_data = []
    for _, row in df_results.iterrows():
        d = row['Data'].tail(5).copy().reset_index() # 5 Hari terakhir
        d['Ticker'] = row['Ticker']
        # Rename date col if needed
        if 'index' in d.columns: d.rename(columns={'index':'Date'}, inplace=True)
        # Standardize columns
        cols = [c for c in ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'] if c in d.columns]
        all_data.append(d[cols])
        
    if all_data:
        final = pd.concat(all_data)
        final['Date'] = final['Date'].astype(str)
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final.to_excel(writer, index=False, sheet_name='Data 5 Hari')
    return output.getvalue()

# --- UTAMA (UI) ---
st.title("📊 Market Scanner: Percentage View")
st.markdown("""
**Fitur Baru:** Grafik menggunakan skala **Persentase**.
* **0% (Garis Bawah)** = Harga terendah dalam periode grafik (1 Bulan).
* **Sumbu Kanan** = Menunjukkan berapa persen harga saat ini berada di atas titik terendah tersebut.
""")

if st.button("🔄 Refresh Market Data"):
    st.cache_data.clear()
    st.rerun()

# 1. LOAD DATA
df = get_stock_data_batch(DEFAULT_TICKERS)

if not df.empty:
    # 2. TOMBOL DOWNLOAD
    with st.expander("📥 Download Data Excel"):
        st.download_button(
            "Download .xlsx (5 Hari Terakhir)",
            data=generate_excel(df),
            file_name=f"market_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    # 3. KONTROL FILTER TAMPILAN
    col_filter1, col_filter2 = st.columns([2,1])
    with col_filter1:
        sort_by = st.selectbox("Urutkan Berdasarkan:", 
                               ["Volatilitas (Paling Liar)", "Kenaikan Hari Ini", "Penurunan Hari Ini", "Kenaikan 1 Minggu"])
    
    # Logika Sorting
    if sort_by == "Volatilitas (Paling Liar)":
        df_display = df.nlargest(20, 'Volatilitas')
    elif sort_by == "Kenaikan Hari Ini":
        df_display = df.nlargest(20, 'Hari Ini %')
    elif sort_by == "Penurunan Hari Ini":
        df_display = df.nsmallest(20, 'Hari Ini %')
    elif sort_by == "Kenaikan 1 Minggu":
        df_display = df.nlargest(20, '1 Minggu %')
        
    st.divider()
    
    # 4. TAMPILAN GRID GRAFIK (4 Kolom)
    # Ini bagian inti visualisasinya
    cols = st.columns(4)
    
    for i, (index, row) in enumerate(df_display.iterrows()):
        with cols[i % 4]:
            # HEADER KECIL
            # Menampilkan Ticker dan % 1 Minggu
            color_1w = "green" if row['1 Minggu %'] > 0 else "red"
            st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
            st.markdown(f"<small>1W: <span style='color:{color_1w}'>{row['1 Minggu %']:+.2f}%</span> | Range: {row['Volatilitas']:.1f}%</small>", unsafe_allow_html=True)
            
            # GRAFIK KHUSUS (PERSENTASE)
            fig = plot_percentage_chart(row['Data'], row['Ticker'])
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("") # Spacer

else:
    st.error("Gagal mengambil data. Coba refresh.")
