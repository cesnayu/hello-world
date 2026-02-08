import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Stock Comparison Dashboard", layout="wide")

st.title("⚖️ Stock Perbandingan Fundamental")
st.markdown("Bandingkan **P/E, P/S, ROE, DER, dan EPS** dari banyak saham sekaligus untuk mencari yang terbaik.")

# --- INPUT SAHAM ---
default_tickers = "BBCA, BBRI, BMRI, BBNI, ASII, TLKM, UNVR, ICBP, ADRO, PTBA, GOTO"
input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=default_tickers)

# --- FUNGSI AMBIL DATA ---
def get_fundamental_data(tickers_raw):
    # Bersihkan input dan tambah .JK
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    
    # Progress Bar karena ambil data fundamental butuh waktu (looping)
    progress_bar = st.progress(0, text="Mengambil data fundamental...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            # Update progress
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menganalisa {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Ambil Data (Gunakan .get agar tidak error jika data kosong)
            name = info.get('shortName', ticker)
            price = info.get('currentPrice', 0)
            
            # 1. P/E Ratio (Valuasi Laba)
            pe = info.get('trailingPE', None)
            
            # 2. P/S Ratio (Valuasi Penjualan)
            ps = info.get('priceToSalesTrailing12Months', None)
            
            # 3. ROE (Profitabilitas) -> Yahoo kasih dalam desimal (0.15), kita butuh persen (15)
            roe = info.get('returnOnEquity', 0)
            if roe: roe = roe * 100
            
            # 4. Debt to Equity (Kesehatan Utang) -> Yahoo kasih 80.5 artinya 80.5%
            der = info.get('debtToEquity', None)
            
            # 5. EPS (Laba per lembar)
            eps = info.get('trailingEps', None)
            
            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': price,
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except Exception as e:
            continue # Skip jika error

    progress_bar.empty()
    return pd.DataFrame(data)

# --- TOMBOL PROSES ---
if st.button("🚀 Bandingkan Sekarang"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        df = get_fundamental_data(input_saham)
        
        if not df.empty:
            st.success(f"Berhasil membandingkan {len(df)} saham.")
            
            # --- TAMPILAN 1: TABEL DENGAN HEATMAP WARNA ---
            st.subheader("📋 Tabel Perbandingan (Heatmap)")
            st.caption("Tips: Klik judul kolom untuk mengurutkan (Sort).")

            # Konfigurasi Tampilan Kolom Streamlit
            column_config = {
                "Kode": st.column_config.TextColumn("Ticker", width="small"),
                "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
                "P/E Ratio (x)": st.column_config.NumberColumn("P/E Ratio", format="%.2fx", help="Makin Rendah Makin Murah"),
                "P/S Ratio (x)": st.column_config.NumberColumn("P/S Ratio", format="%.2fx", help="Makin Rendah Makin Murah"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%", help="Makin Tinggi Makin Bagus"),
                "DER (%)": st.column_config.NumberColumn("Debt/Eq", format="%.2f%%", help="Makin Rendah Makin Aman"),
                "EPS (Rp)": st.column_config.NumberColumn("EPS", format="Rp %.2f"),
            }

            # --- LOGIC WARNA (PENTING) ---
            # Kita pakai Pandas Styler background_gradient
            # cmap='RdYlGn' artinya Merah (Red) ke Hijau (Green)
            # cmap='RdYlGn_r' artinya dibalik (Hijau ke Merah) -> _r artinya reversed
            
            styled_df = df.style.format("{:.2f}", subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']) \
                .background_gradient(subset=['ROE (%)', 'EPS (Rp)'], cmap='RdYlGn') \
                .background_gradient(subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'DER (%)'], cmap='RdYlGn_r') 
                # Penjelasan Warna:
                # ROE & EPS: Pakai RdYlGn (Makin Tinggi = Hijau/Bagus)
                # PE, PS, DER: Pakai RdYlGn_r (Makin Rendah = Hijau/Bagus, Makin Tinggi = Merah)

            st.dataframe(
                styled_df,
                column_config=column_config,
                use_container_width=True,
                height=500,
                hide_index=True
            )
            
            # --- TAMPILAN 2: GRAFIK PERBANDINGAN ---
            st.divider()
            st.subheader("📊 Visualisasi Grafik")
            
            metric_choice = st.selectbox("Pilih Metrik untuk Grafik:", 
                                         ['P/E Ratio (x)', 'ROE (%)', 'DER (%)', 'P/S Ratio (x)'])
            
            # Bar Chart Interaktif
            st.bar_chart(df.set_index('Kode')[metric_choice])
            
            # Penjelasan Metrik
            if metric_choice == 'P/E Ratio (x)':
                st.info("💡 **P/E Ratio**: Semakin rendah barnya, semakin murah valuasinya (dengan asumsi earnings stabil).")
            elif metric_choice == 'ROE (%)':
                st.info("💡 **ROE**: Semakin tinggi barnya, semakin jago manajemen menghasilkan laba dari modal.")
            elif metric_choice == 'DER (%)':
                st.info("💡 **DER**: Semakin rendah barnya, semakin aman perusahaan dari risiko utang.")
                
        else:
            st.error("Data tidak ditemukan. Cek koneksi atau kode saham.")

