import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Stock Comparison Dashboard", layout="wide")

st.title("⚖️ Stock Perbandingan Fundamental")
st.markdown("Bandingkan **P/E, P/S, ROE, DER, dan EPS** dari banyak saham sekaligus.")

# --- INPUT SAHAM ---
default_tickers = "BBCA, BBRI, BMRI, BBNI, ASII, TLKM, UNVR, ICBP, ADRO, PTBA, GOTO"
input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=default_tickers)

# --- FUNGSI AMBIL DATA ---
def get_fundamental_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Mengambil data fundamental...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menganalisa {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            name = info.get('shortName', ticker)
            price = info.get('currentPrice', 0)
            
            # Ambil data (Default None jika gagal)
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            
            # Konversi ROE ke Persen jika ada
            if roe is not None: roe = roe * 100

            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': price,
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except Exception:
            continue

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
            
            # --- PENTING: BERSIHKAN DATA SEBELUM DITAMPILKAN ---
            # 1. Pastikan semua kolom angka terbaca sebagai float (bukan object/string)
            cols_to_numeric = ['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']
            for col in cols_to_numeric:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Ubah error jadi NaN (Not a Number)

            # --- TAMPILAN TABEL ---
            st.subheader("📋 Tabel Perbandingan (Heatmap)")

            # Konfigurasi Tampilan (Streamlit yang menangani format angka)
            column_config = {
                "Kode": st.column_config.TextColumn("Ticker", width="small"),
                "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
                "P/E Ratio (x)": st.column_config.NumberColumn("P/E Ratio", format="%.2fx"),
                "P/S Ratio (x)": st.column_config.NumberColumn("P/S Ratio", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "DER (%)": st.column_config.NumberColumn("Debt/Eq", format="%.2f%%"),
                "EPS (Rp)": st.column_config.NumberColumn("EPS", format="Rp %.2f"),
            }

            # --- STYLING (Hanya Warna, Tanpa Format Angka) ---
            # Kita hapus .format() dari sini agar tidak bentrok dengan NoneType
            # background_gradient akan otomatis mengabaikan NaN (tetap putih)
            styled_df = df.style\
                .background_gradient(subset=['ROE (%)', 'EPS (Rp)'], cmap='RdYlGn')\
                .background_gradient(subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'DER (%)'], cmap='RdYlGn_r')

            st.dataframe(
                styled_df,
                column_config=column_config,
                use_container_width=True,
                height=500,
                hide_index=True
            )
            
            # --- GRAFIK ---
            st.divider()
            st.subheader("📊 Visualisasi Grafik")
            metric_choice = st.selectbox("Pilih Metrik:", ['P/E Ratio (x)', 'ROE (%)', 'DER (%)', 'P/S Ratio (x)'])
            
            # Drop NaN sebelum plot grafik agar bar chart tidak error
            chart_df = df[['Kode', metric_choice]].dropna().set_index('Kode')
            st.bar_chart(chart_df)
                
        else:
            st.error("Data tidak ditemukan atau koneksi bermasalah.")
