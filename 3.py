import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Pro Stock Screener", layout="wide")

st.title("🦅 Pro Stock Screener: Search First, Filter Later")
st.markdown("""
**Cara Pakai:**
1. Masukkan kode saham & Klik **"Ambil Data Mentah"**.
2. Tunggu data muncul.
3. Lihat **Range Data** (Min/Max) di panel statistik.
4. Ketik angka filter kamu sendiri untuk melihat mana yang **Lolos (Hijau)**.
""")

# ==========================================
# 2. FUNGSI AMBIL DATA (ROBUST & ANTI-BLOKIR)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_fundamental_data(tickers_raw):
    # Bersihkan input user
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = []
    for t in tickers_list:
        clean_t = t.replace(' ', '')
        # Tambah .JK jika belum ada
        if not clean_t.endswith(".JK"):
            tickers_fixed.append(f"{clean_t}.JK")
        else:
            tickers_fixed.append(clean_t)
    
    data = []
    errors = []
    
    # Progress Bar UI
    progress_text = "Menghubungi Bursa..."
    my_bar = st.progress(0, text=progress_text)
    
    # SETUP SESSION AGAR DIKIRA BROWSER (ANTI-BLOKIR)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    for i, ticker in enumerate(tickers_fixed):
        try:
            # Update Progress
            pct = int((i / len(tickers_fixed)) * 100)
            my_bar.progress(pct, text=f"Menganalisa {ticker}...")
            
            # PENTING: Jeda 0.5 detik per saham agar tidak dianggap SPAM oleh Yahoo
            time.sleep(0.5)
            
            stock = yf.Ticker(ticker, session=session)
            
            # Coba ambil fast_info (lebih cepat & hemat kuota request) untuk harga
            try:
                price = stock.fast_info.last_price
            except:
                price = None

            # Ambil Info Fundamental (Ini yang berat)
            info = stock.info
            
            if not info or len(info) < 5:
                errors.append(f"{ticker}: Data Kosong/Gagal.")
                continue

            # Ambil Data Point
            # Gunakan .get() agar tidak error jika data spesifik hilang
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            
            # Fallback harga jika fast_info gagal
            if price is None:
                price = info.get('currentPrice') or info.get('regularMarketPreviousClose')

            # Konversi ROE desimal ke Persen (0.15 -> 15.0)
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
            
        except Exception as e:
            errors.append(f"{ticker}: Error ({str(e)})")
            continue

    my_bar.empty() # Hapus progress bar setelah selesai
    
    return pd.DataFrame(data), errors

# ==========================================
# 3. UI BAGIAN ATAS: INPUT & SEARCH
# ==========================================
default_tickers = "BBCA, BBRI, BMRI, BBNI, ASII, TLKM, UNVR, ICBP, ADRO, PTBA, ITMG, GOTO, ARTO, SIDO, KLBF, MAPI"
input_saham = st.text_area("1️⃣ Masukkan Daftar Saham (Pisahkan koma):", value=default_tickers)

if st.button("🚀 Ambil Data Mentah"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        # Panggil fungsi
        df_result, err_list = get_fundamental_data(input_saham)
        
        if not df_result.empty:
            # SIMPAN KE SESSION STATE
            # Agar saat kita ubah filter di bawah, data tidak hilang/download ulang
            st.session_state['data_saham_final'] = df_result
            st.session_state['error_log'] = err_list
            st.success(f"Berhasil mengambil {len(df_result)} saham!")
        else:
            st.error("Gagal mengambil data. Cek koneksi atau kode saham.")

# ==========================================
# 4. UI BAGIAN BAWAH: FILTER & DISPLAY
# ==========================================
# Bagian ini hanya muncul jika data sudah ada di memory (Session State)
if 'data_saham_final' in st.session_state:
    df = st.session_state['data_saham_final']
    errors = st.session_state['error_log']
    
    st.divider()
    st.header("2️⃣ Analisa & Filter Nilai")
    
    # --- A. TAMPILKAN STATISTIK RANGE DATA (Min/Max) ---
    # Ini membantu user menentukan angka filter yang wajar
    st.info("ℹ️ **Statistik Data Saat Ini (Referensi untuk Filter):**")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        min_pe = df['P/E Ratio (x)'].min()
        max_pe = df['P/E Ratio (x)'].max()
        st.write(f"**P/E Range:**\n{min_pe:.1f}x - {max_pe:.1f}x")
        # Input Filter User
        filter_pe = st.number_input("Max P/E Target:", value=15.0, step=0.5)

    with col_s2:
        min_roe = df['ROE (%)'].min()
        max_roe = df['ROE (%)'].max()
        st.write(f"**ROE Range:**\n{min_roe:.1f}% - {max_roe:.1f}%")
        # Input Filter User
        filter_roe = st.number_input("Min ROE Target:", value=10.0, step=1.0)

    with col_s3:
        min_der = df['DER (%)'].min()
        max_der = df['DER (%)'].max()
        st.write(f"**DER Range:**\n{min_der:.1f}% - {max_der:.1f}%")
        # Input Filter User
        filter_der = st.number_input("Max DER Target:", value=100.0, step=10.0)

    with col_s4:
        min_ps = df['P/S Ratio (x)'].min()
        max_ps = df['P/S Ratio (x)'].max()
        st.write(f"**P/S Range:**\n{min_ps:.1f}x - {max_ps:.1f}x")
        # Input Filter User
        filter_ps = st.number_input("Max P/S Target:", value=2.0, step=0.1)

    # --- B. HITUNG SKOR & SORTING ---
    # Kita beri skor: Semakin banyak kriteria terpenuhi, semakin tinggi skornya
    # Kriteria: PE <= Target, ROE >= Target, DER <= Target, PS <= Target
    
    # Copy dataframe biar aman
    df_scored = df.copy()
    
    # Fungsi hitung skor per baris
    def calculate_score(row):
        score = 0
        if pd.notna(row['P/E Ratio (x)']) and row['P/E Ratio (x)'] <= filter_pe: score += 1
        if pd.notna(row['ROE (%)']) and row['ROE (%)'] >= filter_roe: score += 1
        if pd.notna(row['DER (%)']) and row['DER (%)'] <= filter_der: score += 1
        if pd.notna(row['P/S Ratio (x)']) and row['P/S Ratio (x)'] <= filter_ps: score += 1
        return score

    df_scored['Skor'] = df_scored.apply(calculate_score, axis=1)
    
    # Urutkan: Skor Tertinggi -> ROE Tertinggi
    df_sorted = df_scored.sort_values(by=['Skor', 'ROE (%)'], ascending=[False, False])

    # --- C. STYLING (WARNA-WARNI) ---
    # Fungsi ini menentukan warna background sel
    def style_table(row):
        # Siapkan list warna default (putih/transparan) untuk setiap kolom
        # Urutan Kolom: Kode, Harga, PE, PS, ROE, DER, EPS, Skor
        styles = [''] * len(row)
        
        # Helper warna
        green = 'background-color: #d4edda; color: black' # Hijau Muda
        red   = 'background-color: #f8d7da; color: black' # Merah Muda
        
        # Logika Warna P/E (Kolom Index 2)
        pe_val = row['P/E Ratio (x)']
        if pd.notna(pe_val):
            styles[2] = green if pe_val <= filter_pe else red
            
        # Logika Warna P/S (Kolom Index 3)
        ps_val = row['P/S Ratio (x)']
        if pd.notna(ps_val):
            styles[3] = green if ps_val <= filter_ps else red
            
        # Logika Warna ROE (Kolom Index 4) - Ingat ROE harus LEBIH BESAR
        roe_val = row['ROE (%)']
        if pd.notna(roe_val):
            styles[4] = green if roe_val >= filter_roe else red
            
        # Logika Warna DER (Kolom Index 5)
        der_val = row['DER (%)']
        if pd.notna(der_val):
            styles[5] = green if der_val <= filter_der else red

        # Logika Warna Skor (Kolom Terakhir) - Hijau pekat jika 4/4
        score_val = row['Skor']
        if score_val == 4:
            styles[-1] = 'background-color: #28a745; color: white; font-weight: bold' # Hijau Tua
            
        return styles

    # --- D. TAMPILKAN TABEL AKHIR ---
    st.subheader("📊 Hasil Screening")
    
    # Konfigurasi Tampilan Angka (Supaya ada Rp, %, x)
    col_config = {
        "Kode": st.column_config.TextColumn("Ticker", width="small"),
        "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
        "P/E Ratio (x)": st.column_config.NumberColumn("P/E Ratio", format="%.2fx"),
        "P/S Ratio (x)": st.column_config.NumberColumn("P/S Ratio", format="%.2fx"),
        "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
        "DER (%)": st.column_config.NumberColumn("DER", format="%.2f%%"),
        "EPS (Rp)": st.column_config.NumberColumn("EPS", format="Rp %.2f"),
        "Skor": st.column_config.ProgressColumn(
            "Match Score", 
            min_value=0, 
            max_value=4, 
            format="%d/4",
            help="Berapa banyak kriteria yang lolos?"
        )
    }

    # Apply Style & Tampilkan
    st.dataframe(
        df_sorted.style.apply(style_table, axis=1),
        column_config=col_config,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Tampilkan Error Log di bawah jika ada
    if errors:
        with st.expander(f"⚠️ Ada {len(errors)} Saham Gagal Diambil"):
            st.write(errors)
            st.caption("Tips: Jika error 'Too Many Requests', coba kurangi jumlah saham.")
