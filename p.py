import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Live Scanner IHSG", layout="wide")

# --- LIST SAHAM (Gunakan List Kamu) ---
# Ini contoh sebagian saham Kompas100 agar demo berjalan.
# Silakan timpa variabel ini dengan list 800 sahammu.
STOCK_LIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'ICBP.JK', 
    'INDF.JK', 'KLBF.JK', 'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK', 'ITMG.JK', 
    'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK', 'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 
    'EXCL.JK', 'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK', 'MNCN.JK', 'SCMA.JK', 
    'GGRM.JK', 'HMSP.JK', 'WIIM.JK', 'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK', 
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK', 'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 
    'UNTR.JK', 'MEDC.JK', 'HRUM.JK', 'TPIA.JK', 'INKP.JK', 'TKIM.JK', 'JPFA.JK', 'MYOR.JK',
    'ARTO.JK', 'BRIS.JK', 'BBYB.JK', 'BBHI.JK', 'AGRO.JK', 'BUMI.JK', 'ENRG.JK', 'DEWA.JK'
]

# --- FUNGSI GRAFIK SPESIAL ---
def create_dual_axis_chart(data, ticker):
    """
    Membuat grafik Harga (Rupiah) tapi dengan Sumbu Kanan Persentase
    """
    # Hitung High & Low Periode ini
    period_low = data['Low'].min()
    period_high = data['High'].max()
    current_price = data['Close'].iloc[-1]
    
    # Hitung total volatilitas (Range %)
    volatility_range = ((period_high - period_low) / period_low) * 100
    
    # Cari tanggal dimana High dan Low terjadi untuk penempatan titik
    date_high = data['High'].idxmax()
    date_low = data['Low'].idxmin()

    fig = go.Figure()

    # 1. GARIS HARGA (Utama - Sumbu Kiri)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Harga',
        mode='lines',
        line=dict(color='#2962FF', width=2)
    ))

    # 2. MARKER HIGH (Titik Merah)
    fig.add_trace(go.Scatter(
        x=[date_high], y=[period_high],
        mode='markers+text',
        name='Max',
        marker=dict(color='red', size=8),
        text=[f"Hi: {period_high:,.0f}"],
        textposition="top center",
        textfont=dict(size=10, color='red')
    ))

    # 3. MARKER LOW (Titik Hijau)
    fig.add_trace(go.Scatter(
        x=[date_low], y=[period_low],
        mode='markers+text',
        name='Min',
        marker=dict(color='green', size=8),
        text=[f"Lo: {period_low:,.0f}"],
        textposition="bottom center",
        textfont=dict(size=10, color='green')
    ))

    # --- SETUP DUAL AXIS ---
    # Sumbu Kiri: Harga Rupiah
    # Sumbu Kanan: Persentase (Relatif terhadap Low)
    
    # Kita "menipu" sumbu kanan dengan tickvals manual
    # Agar garisnya tetap garis harga, tapi angkanya persen.
    
    # Tentukan 5 titik tick di sumbu kanan (0%, 25%, 50%, 75%, 100% dari Range)
    tick_vals = [period_low, 
                 period_low + (period_high - period_low)*0.25,
                 period_low + (period_high - period_low)*0.50,
                 period_low + (period_high - period_low)*0.75,
                 period_high]
    
    tick_text = ["0% (Low)", 
                 f"{volatility_range*0.25:.1f}%", 
                 f"{volatility_range*0.50:.1f}%", 
                 f"{volatility_range*0.75:.1f}%", 
                 f"{volatility_range:.1f}% (High)"]

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> (Range: {volatility_range:.1f}%)",
            font=dict(size=14),
            x=0
        ),
        margin=dict(l=0, r=50, t=30, b=0),
        height=250,
        showlegend=False,
        hovermode="x unified",
        
        # Sumbu Y Kiri (Harga)
        yaxis=dict(
            title=None,
            showgrid=False,
            tickformat=",.0f" # Format ribuan
        ),
        
        # Sumbu Y Kanan (Persentase)
        yaxis2=dict(
            title=None,
            overlaying='y', # Menimpa sumbu Y utama
            side='right',   # Posisi di kanan
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text,
            showgrid=True,  # Grid ikut yang persen
            gridcolor='lightgray',
            tickfont=dict(size=9, color='gray')
        ),
        
        xaxis=dict(showgrid=False)
    )
    
    return fig

# --- MAIN APP ---

st.title("⚡ Live Stock Scanner (Progressive)")
st.caption("Data ditampilkan per batch (setiap 20 saham) agar tidak perlu menunggu lama.")

# Pilihan Periode
period = st.selectbox("Pilih Periode Waktu:", ["1mo", "3mo", "1wk"], index=0)
batch_size = 20

if st.button("🚀 Mulai Scan"):
    
    # Placeholder untuk status
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    total_stocks = len(STOCK_LIST)
    processed_count = 0
    
    # --- LOOPING UTAMA (BATCHING) ---
    for i in range(0, total_stocks, batch_size):
        
        # 1. Ambil potongan list (20 saham)
        batch_tickers = STOCK_LIST[i : i + batch_size]
        batch_str = " ".join(batch_tickers)
        
        status_text.text(f"Mengambil data batch {i+1} - {min(i+batch_size, total_stocks)}...")
        
        try:
            # 2. Download Data Batch Ini
            data = yf.download(batch_str, period=period, group_by='ticker', threads=True, progress=False)
            
            # 3. LANGSUNG TAMPILKAN (Render)
            # Buat container baru agar data muncul di bawah data sebelumnya
            with st.container():
                st.markdown(f"#### Batch {i+1} - {min(i+batch_size, total_stocks)}")
                
                # Gunakan st.columns untuk grid layout (4 kolom per baris)
                cols = st.columns(4)
                col_index = 0
                
                for ticker in batch_tickers:
                    try:
                        # Ekstrak data per saham
                        if len(batch_tickers) > 1:
                            if ticker not in data.columns.levels[0]: continue
                            df_stock = data[ticker].dropna()
                        else:
                            df_stock = data.dropna()

                        if len(df_stock) < 2: continue
                        
                        # Buat Grafik & Tampilkan di Kolom yang sesuai
                        fig = create_dual_axis_chart(df_stock, ticker.replace('.JK', ''))
                        
                        with cols[col_index % 4]:
                            st.plotly_chart(fig, use_container_width=True)
                        
                        col_index += 1
                        
                    except Exception as e:
                        continue
            
            # Update Progress
            processed_count += len(batch_tickers)
            progress_bar.progress(min(processed_count / total_stocks, 1.0))
            
        except Exception as e:
            st.error(f"Error pada batch {i}: {e}")

    status_text.success("✅ Scan Selesai!")
    progress_bar.empty()
