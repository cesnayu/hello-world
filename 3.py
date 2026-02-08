import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dynamic Stock Screener", layout="wide")

st.title("🔍 Search First, Filter Later")
st.markdown("""
**Alur Kerja:**
1. Masukkan list saham & Klik **"Ambil Data"**.
2. Lihat range data (Min/Max) yang muncul.
3. Atur filter di panel bawah untuk menandai mana yang **Lolos (Hijau)** dan **Gagal (Merah)**.
""")

# --- FUNGSI AMBIL DATA (YANG SUDAH DIPERBAIKI) ---
def get_fundamental_data(tickers_raw):
    # Bersihkan input
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = []
    for t in tickers_list:
        # Hapus spasi aneh dan pastikan format .JK
        clean_t = t.replace(' ', '')
        if not clean_t.endswith(".JK"):
            tickers_fixed.append(f"{clean_t}.JK")
        else:
            tickers_fixed.append(clean_t)
    
    data = []
    errors = [] # Untuk menampung pesan error
    
    progress_bar = st.progress(0, text="Mengambil data...")
    
    # Header palsu agar dikira browser manusia (Anti-Blokir Yahoo)
    requests_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menganalisa {ticker}...")
            
            # Trik: Gunakan Session khusus biar lebih kebal blokir
            stock = yf.Ticker(ticker, session=None) 
            
            # Coba ambil info
            info = stock.info
            
            # Cek apakah info kosong (Tanda diblokir atau ticker salah)
            if not info or len(info) < 5:
                errors.append(f"{ticker}: Data kosong/diblokir Yahoo.")
                continue

            # Ambil data point dengan aman
            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': info.get('currentPrice') or info.get('regularMarketPreviousClose'),
                'P/E Ratio (x)': info.get('trailingPE'),
                'P/S Ratio (x)': info.get('priceToSalesTrailing12Months'),
                'ROE (%)': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'DER (%)': info.get('debtToEquity'),
                'EPS (Rp)': info.get('trailingEps')
            })
            
        except Exception as e:
            # Catat errornya biar kita tau kenapa
            errors.append(f"{ticker}: {str(e)}")
            continue

    progress_bar.empty()
    
    # Tampilkan Error di Layar jika ada (Supaya user tau)
    if errors:
        with st.expander("⚠️ Lihat Detail Error (Kenapa ada saham yang hilang?)"):
            for err in errors:
                st.write(err)
                
    return pd.DataFrame(data)

# --- BAGIAN 1: INPUT & SEARCH ---
default_tickers = "BBCA, BBRI, BMRI, BBNI, ASII, TLKM, UNVR, ICBP, ADRO, PTBA, GOTO, SIDO"
input_saham = st.text_area("1️⃣ Masukkan Daftar Saham:", value=default_tickers)

# Tombol Search
if st.button("🚀 Ambil Data Mentah"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        # Ambil data dan simpan ke Session State agar tidak hilang saat filter digeser
        df_raw = get_fundamental_data(input_saham)
        if not df_raw.empty:
            st.session_state['data_saham'] = df_raw
            st.success(f"Berhasil mengambil data {len(df_raw)} saham! Silakan atur filter di bawah.")
        else:
            st.error("Data tidak ditemukan.")

# --- BAGIAN 2: TAMPILAN & FILTER (Hanya muncul jika data sudah ada) ---
if 'data_saham' in st.session_state:
    df = st.session_state['data_saham']
    
    st.divider()
    st.header("2️⃣ Atur Filter & Standar Kamu")
    
    # Hitung Statistik Sederhana untuk Referensi User
    # Agar user tau range datanya dari mana sampai mana
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        min_pe = df['P/E Ratio (x)'].min()
        max_pe = df['P/E Ratio (x)'].max()
        st.info(f"**Range P/E Data Ini:**\n{min_pe:.2f}x s/d {max_pe:.2f}x")
        
        # Input Filter P/E
        filter_pe = st.number_input("Max P/E yg diinginkan:", value=15.0, step=0.5)

    with col_stat2:
        min_roe = df['ROE (%)'].min()
        max_roe = df['ROE (%)'].max()
        st.info(f"**Range ROE Data Ini:**\n{min_roe:.2f}% s/d {max_roe:.2f}%")
        
        # Input Filter ROE
        filter_roe = st.number_input("Min ROE yg diinginkan:", value=10.0, step=0.5)

    with col_stat3:
        min_der = df['DER (%)'].min()
        max_der = df['DER (%)'].max()
        st.info(f"**Range DER Data Ini:**\n{min_der:.2f}% s/d {max_der:.2f}%")
        
        # Input Filter DER
        filter_der = st.number_input("Max DER yg diinginkan:", value=100.0, step=10.0)

    with col_stat4:
        min_ps = df['P/S Ratio (x)'].min()
        max_ps = df['P/S Ratio (x)'].max()
        st.info(f"**Range P/S Data Ini:**\n{min_ps:.2f}x s/d {max_ps:.2f}x")
        
        # Input Filter P/S
        filter_ps = st.number_input("Max P/S yg diinginkan:", value=2.0, step=0.1)

    # --- LOGIKA PEWARNAAN TABEL ---
    # Fungsi ini akan berjalan ulang setiap kali kamu ubah angka di atas
    def style_dataframe(row):
        styles = [''] * len(row)
        
        # Index Kolom (Sesuaikan jika urutan berubah)
        # 0:Kode, 1:Harga, 2:PE, 3:PS, 4:ROE, 5:DER, 6:EPS
        
        # Rule P/E (Kolom index 2) - Makin Rendah Bagus
        pe_val = row['P/E Ratio (x)']
        if pd.notna(pe_val):
            color = '#d4edda' if pe_val <= filter_pe else '#f8d7da' # Hijau jika <= Filter
            styles[2] = f'background-color: {color}; color: black'

        # Rule P/S (Kolom index 3) - Makin Rendah Bagus
        ps_val = row['P/S Ratio (x)']
        if pd.notna(ps_val):
            color = '#d4edda' if ps_val <= filter_ps else '#f8d7da'
            styles[3] = f'background-color: {color}; color: black'

        # Rule ROE (Kolom index 4) - Makin TINGGI Bagus
        roe_val = row['ROE (%)']
        if pd.notna(roe_val):
            color = '#d4edda' if roe_val >= filter_roe else '#f8d7da' # Hijau jika >= Filter
            styles[4] = f'background-color: {color}; color: black'

        # Rule DER (Kolom index 5) - Makin Rendah Bagus
        der_val = row['DER (%)']
        if pd.notna(der_val):
            color = '#d4edda' if der_val <= filter_der else '#f8d7da'
            styles[5] = f'background-color: {color}; color: black'

        return styles

    # Tampilkan Tabel
    st.subheader("📊 Hasil Screening")
    
    # Hitung Skor Kelulusan (Opsional: buat sorting)
    # Kita bikin kolom baru temporary untuk sorting, tapi gak ditampilkan
    df_display = df.copy()
    df_display['Score'] = (
        (df['P/E Ratio (x)'] <= filter_pe).astype(int) + 
        (df['ROE (%)'] >= filter_roe).astype(int) + 
        (df['DER (%)'] <= filter_der).astype(int) +
        (df['P/S Ratio (x)'] <= filter_ps).astype(int)
    )
    
    # Sort biar yang paling hijau ada di atas
    df_display = df_display.sort_values(by=['Score', 'ROE (%)'], ascending=[False, False])
    
    # Hapus kolom score biar tabel bersih (atau tampilkan kalau mau)
    df_final = df_display.drop(columns=['Score'])

    st.dataframe(
        df_final.style.apply(style_dataframe, axis=1)
                  .format("{:.2f}", subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']),
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    st.caption("Baris paling atas adalah yang paling banyak memenuhi kriteria kamu.")
