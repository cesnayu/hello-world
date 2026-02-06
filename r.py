import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================================
# 1. SETUP JUDUL DASHBOARD
# ==========================================
st.set_page_config(page_title="Pantau Cuan Saham", layout="wide")
st.title("📊 Dashboard Return Saham (5 Hari Terakhir)")
st.caption("Memantau pergerakan harga saham Close-to-Close selama 5 hari bursa terakhir.")

# ==========================================
# 2. INPUT SAHAM (BISA DIEDIT USER)
# ==========================================
# Default list
default_tickers = 'BBCA.JK, BBRI.JK, BMRI.JK, ASII.JK, GOTO.JK, TLKM.JK, ADRO.JK, UNVR.JK'

# Input box biar user bisa nambah saham sendiri di layar
input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=default_tickers)

# Tombol untuk mulai hitung
if st.button("🚀 Hitung Return"):
    
    # Rapikan input user menjadi list
    daftar_saham = [x.strip() for x in input_saham.split(',')]
    
    with st.spinner('Sedang menarik data dari Yahoo Finance...'):
        try:
            # Ambil data 1 bulan untuk aman
            df = yf.download(daftar_saham, period="1mo", progress=False)['Close']
            
            # Ambil 6 data terakhir
            df_last_5 = df.tail(6)
            
            if len(df_last_5) < 6:
                st.error("Data tidak cukup. Mungkin pasar sedang libur panjang atau saham baru IPO.")
            else:
                # ==========================================
                # 3. HITUNG RETURN
                # ==========================================
                price_now = df_last_5.iloc[-1]
                price_5days_ago = df_last_5.iloc[0]
                
                # Hitung % Return
                total_return_5d = ((price_now - price_5days_ago) / price_5days_ago) * 100
                
                # Buat DataFrame
                result_df = pd.DataFrame({
                    'Harga 5 Hari Lalu': price_5days_ago,
                    'Harga Terakhir': price_now,
                    'Total Gain 5D (%)': total_return_5d
                })

                # Sorting (Tertinggi ke Terendah)
                result_df = result_df.sort_values(by='Total Gain 5D (%)', ascending=False)

                # ==========================================
                # 4. TAMPILKAN METRICS (KOTAK RINGKASAN)
                # ==========================================
                # Ambil Juara & Boncos
                top_gainer_ticker = result_df.index[0]
                top_gainer_val = result_df['Total Gain 5D (%)'].iloc[0]
                
                top_loser_ticker = result_df.index[-1]
                top_loser_val = result_df['Total Gain 5D (%)'].iloc[-1]

                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(label="🏆 Top Gainer (5 Hari)", 
                              value=top_gainer_ticker, 
                              delta=f"{top_gainer_val:.2f}%")
                
                with col2:
                    st.metric(label="💀 Top Loser (5 Hari)", 
                              value=top_loser_ticker, 
                              delta=f"{top_loser_val:.2f}%")

                st.divider()

                # ==========================================
                # 5. TAMPILKAN TABEL UTAMA
                # ==========================================
                st.subheader("📋 Detail Performa")
                
                # Formatting warna tabel otomatis via Pandas Styler
                # Hijau jika positif, Merah jika negatif
                def warna_return(val):
                    color = '#d4edda' if val > 0 else '#f8d7da' if val < 0 else ''
                    return f'background-color: {color}; color: black'

                # Tampilkan tabel di Streamlit
                st.dataframe(
                    result_df.style.applymap(warna_return, subset=['Total Gain 5D (%)'])
                             .format("{:.2f}", subset=['Harga 5 Hari Lalu', 'Harga Terakhir'])
                             .format("{:.2f}%", subset=['Total Gain 5D (%)']),
                    use_container_width=True,
                    height=500
                )

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
