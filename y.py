import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="IHSG Dashboard", layout="wide")

# --- LIST SAHAM ---
STOCK_LIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK',
    'ASII.JK', 'UNVR.JK', 'ICBP.JK', 'INDF.JK', 'KLBF.JK',
    'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK',
    'ITMG.JK', 'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK',
    'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 'EXCL.JK',
    'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK',
    'MNCN.JK', 'SCMA.JK', 'GGRM.JK', 'HMSP.JK', 'WIIM.JK',
    'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK',
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK',
    'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 'UNTR.JK', 'MEDC.JK'
]

# --- FUNGSI ---

@st.cache_data(ttl=300) # Cache data selama 5 menit agar loading cepat
def get_all_stock_data(tickers):
    """Mengambil data semua saham sekaligus untuk efisiensi"""
    results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Mengambil data: {ticker} ({i+1}/{total})")
        try:
            stock = yf.Ticker(ticker)
            # Ambil data 3 bulan untuk grafik & perhitungan
            hist = stock.history(period='3mo')
            
            if len(hist) > 1:
                # Harga terkini
                current_price = hist['Close'].iloc[-1]
                
                # Perhitungan % perubahan
                day_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) >= 2 else 0
                week_change = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 5 else 0
                month_change = ((current_price - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100 if len(hist) >= 20 else 0
                month3_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) >= 60 else 0

                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': current_price,
                    'Hari Ini': day_change,
                    '1 Minggu': week_change,
                    '1 Bulan': month_change,
                    '3 Bulan': month3_change,
                    'Data': hist # Menyimpan dataframe history
                })
        except Exception as e:
            continue
        
        # Update progress
        progress_bar.progress((i + 1) / total)
            
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def generate_excel_5_days(df_results):
    """Membuat file Excel dari data 5 hari terakhir semua saham"""
    output = io.BytesIO()
    
    # Kita akan membuat satu sheet berisi gabungan data
    all_history = []
    
    for _, row in df_results.iterrows():
        ticker = row['Ticker']
        hist_data = row['Data'].tail(5).copy() # Ambil 5 hari terakhir
        hist_data['Ticker'] = ticker
        hist_data = hist_data.reset_index()
        # Format tanggal agar rapi
        hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
        all_history.append(hist_data[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']])
    
    if all_history:
        final_df = pd.concat(all_history)
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False, sheet_name='5 Hari Terakhir')
            # Auto-adjust column width (opsional, basic formatting)
            worksheet = writer.sheets['5 Hari Terakhir']
            worksheet.set_column('A:G', 12)
            
    return output.getvalue()

def plot_sparkline(data, ticker, color):
    """Membuat grafik garis sederhana"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], 
        mode='lines', 
        line=dict(color=color, width=2),
        hoverinfo='x+y'
    ))
    fig.update_layout(
        title=ticker,
        title_font_size=12,
        margin=dict(l=0, r=0, t=30, b=0),
        height=150,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

# --- MAIN APP UI ---

st.title("🇮🇩 Dashboard Pantau Saham IHSG")
st.markdown(f"Update Terakhir: **{datetime.now().strftime('%d %B %Y %H:%M:%S')}**")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# 1. Load Data
df = get_all_stock_data(STOCK_LIST)

if not df.empty:
    # Pisahkan Gainers & Losers
    df_gainers = df.nlargest(10, 'Hari Ini')
    df_losers = df.nsmallest(10, 'Hari Ini')

    # --- BAGIAN DOWNLOAD DATA ---
    st.divider()
    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.write("### 📥 Unduh Riwayat Data")
        st.write("Klik tombol di samping untuk mengunduh data OHLCV 5 hari terakhir dari semua saham di dalam list.")
    with col_dl2:
        excel_data = generate_excel_5_days(df)
        st.download_button(
            label="Download Excel (5 Hari)",
            data=excel_data,
            file_name=f'saham_ihsg_5hari_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    st.divider()

    # --- TAMPILAN DASHBOARD ---
    
    # Tab layout
    tab1, tab2 = st.tabs(["📈 Top Gainers", "📉 Top Losers"])

    with tab1:
        st.subheader("Top 10 Kenaikan Hari Ini")
        
        # Tampilkan Tabel Ringkas
        st.dataframe(
            df_gainers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan']],
            column_config={
                "Harga": st.column_config.NumberColumn(format="Rp %d"),
                "Hari Ini": st.column_config.NumberColumn(format="%.2f%%"),
                "1 Minggu": st.column_config.NumberColumn(format="%.2f%%"),
                "1 Bulan": st.column_config.NumberColumn(format="%.2f%%"),
            },
            hide_index=True,
            use_container_width=True
        )

        # Tampilkan Grafik Grid
        st.write("#### Grafik Pergerakan (3 Bulan)")
        cols = st.columns(5) # 5 kolom per baris
        for i, (index, row) in enumerate(df_gainers.iterrows()):
            with cols[i % 5]:
                st.plotly_chart(
                    plot_sparkline(row['Data'], row['Ticker'], 'green'), 
                    use_container_width=True
                )

    with tab2:
        st.subheader("Top 10 Penurunan Hari Ini")
        
        # Tampilkan Tabel Ringkas
        st.dataframe(
            df_losers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan']],
            column_config={
                "Harga": st.column_config.NumberColumn(format="Rp %d"),
                "Hari Ini": st.column_config.NumberColumn(format="%.2f%%"),
                "1 Minggu": st.column_config.NumberColumn(format="%.2f%%"),
                "1 Bulan": st.column_config.NumberColumn(format="%.2f%%"),
            },
            hide_index=True,
            use_container_width=True
        )

        # Tampilkan Grafik Grid
        st.write("#### Grafik Pergerakan (3 Bulan)")
        cols = st.columns(5)
        for i, (index, row) in enumerate(df_losers.iterrows()):
            with cols[i % 5]:
                st.plotly_chart(
                    plot_sparkline(row['Data'], row['Ticker'], 'red'), 
                    use_container_width=True
                )

else:
    st.error("Gagal mengambil data. Coba refresh kembali.")