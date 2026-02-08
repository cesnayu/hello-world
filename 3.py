import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="IHSG Jumbo Scanner", layout="wide")
st.title("🐘 IHSG Jumbo Scanner (900 Saham)")
st.markdown("""
**Strategi Batch (Cicil):**
Karena jumlah saham sangat banyak, kita akan mengambil data per **20 saham**.
1. Masukkan List Saham.
2. Klik **"Mulai / Reset"**.
3. Klik tombol **"Ambil Batch Berikutnya"** berulang kali sampai selesai.
4. Jika error, data yang sudah diambil **TIDAK HILANG**.
""")

# ==========================================
# 2. INISIALISASI SESSION STATE (MEMORY)
# ==========================================
# Ini gudang penyimpanan data sementara agar tidak hilang saat refresh
if 'master_data' not in st.session_state:
    st.session_state['master_data'] = pd.DataFrame()

if 'tickers_queue' not in st.session_state:
    st.session_state['tickers_queue'] = [] # Daftar antrian saham

if 'processed_count' not in st.session_state:
    st.session_state['processed_count'] = 0

if 'is_running' not in st.session_state:
    st.session_state['is_running'] = False

# ==========================================
# 3. FUNGSI AMBIL DATA PER BATCH
# ==========================================
def fetch_batch(tickers_subset):
    data = []
    errors = []
    
    # Setup Session Browser (Anti-Blokir)
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'})

    # Progress bar kecil untuk batch ini
    my_bar = st.progress(0, text="Memproses Batch...")

    for i, t in enumerate(tickers_subset):
        try:
            # Update bar
            my_bar.progress(int((i / len(tickers_subset)) * 100), text=f"Sedang ambil: {t}")
            
            # Wajib Jeda biar Yahoo gak marah
            time.sleep(0.2) 
            
            stock = yf.Ticker(t, session=session)
            
            # Coba ambil info
            try:
                info = stock.info
            except:
                errors.append(t)
                continue
            
            if not info or len(info) < 5:
                errors.append(t)
                continue

            # Ambil Data Penting
            data.append({
                'Kode': t.replace('.JK', ''),
                'Harga': info.get('currentPrice') or info.get('regularMarketPreviousClose'),
                'P/E Ratio': info.get('trailingPE'),
                'PBV': info.get('priceToBook'),
                'ROE (%)': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'Market Cap (T)': info.get('marketCap', 0) / 1_000_000_000_000, # Dalam Triliun
                'Sector': info.get('sector', 'Unknown')
            })
            
        except:
            errors.append(t)
    
    my_bar.empty()
    return pd.DataFrame(data), errors

# ==========================================
# 4. UI: INPUT & KONTROL
# ==========================================

# Area Input Ticker
with st.expander("📝 Masukkan Daftar Saham (900 Ticker)", expanded=not st.session_state['is_running']):
    # Contoh data dummy banyak (bisa diganti user)
    default_txt = "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, UNVR, ICBP, GOTO, ADRO, PTBA, ITMG, BUMI, PGAS, ANTM, INCO, TINS, SMGR, INTP, JPFA, CPIN, MYOR, INDF, UNTR, HEXA, KLBF, MIKA, HEAL, SILO, MAPI, ERAA, ACES, SIDO, KAEF, INAF, WIKA, PTPP, ADHI, WSKT, JSMR, PGEO, BREN, AMMN, MBMA, NCKL, HRUM, BRPT, TPIA, BRIS, ARTO, BBTN, BDMN, BNGA, PNBN, SPTO, AVIA, MARK, SCMA, MNCN, EMTK"
    input_text = st.text_area("Tempel 900 saham di sini (pisahkan koma):", value=default_txt, height=150)
    
    if st.button("SET DAFTAR ANTRIAN"):
        # Bersihkan input
        raw_list = [x.strip().upper() for x in input_text.split(',')]
        clean_list = []
        for x in raw_list:
            t = x.replace(' ', '')
            if t: # Kalau tidak kosong
                if not t.endswith(".JK"): t += ".JK"
                clean_list.append(t)
        
        # Reset Session
        st.session_state['tickers_queue'] = list(set(clean_list)) # Hapus duplikat
        st.session_state['master_data'] = pd.DataFrame()
        st.session_state['processed_count'] = 0
        st.session_state['is_running'] = True
        st.rerun()

# ==========================================
# 5. UI: EKSEKUSI BATCH
# ==========================================
if st.session_state['is_running']:
    total_saham = len(st.session_state['tickers_queue'])
    processed = st.session_state['processed_count']
    remaining = total_saham - processed
    
    st.divider()
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.metric("Total Saham", total_saham)
    with col_info2:
        st.metric("Sudah Selesai", processed)
        
    st.progress(processed / total_saham if total_saham > 0 else 0)
    
    # KONTROL BATCH
    BATCH_SIZE = 20 # Aman: 20 saham per klik
    
    if remaining > 0:
        st.info(f"Siap mengambil **{min(BATCH_SIZE, remaining)}** saham berikutnya.")
        
        if st.button(f"🚀 AMBIL BATCH BERIKUTNYA ({processed+1} - {min(processed+BATCH_SIZE, total_saham)})"):
            # Ambil potongan list
            batch_tickers = st.session_state['tickers_queue'][processed : processed + BATCH_SIZE]
            
            # Panggil fungsi fetch
            df_new, err_new = fetch_batch(batch_tickers)
            
            # Gabungkan dengan data master
            if not df_new.empty:
                st.session_state['master_data'] = pd.concat([st.session_state['master_data'], df_new], ignore_index=True)
            
            # Update counter
            st.session_state['processed_count'] += BATCH_SIZE
            st.rerun() # Refresh halaman untuk update angka
    else:
        st.success("🎉 SEMUA SAHAM SUDAH DIPROSES!")

# ==========================================
# 6. UI: HASIL AKHIR & DOWNLOAD
# ==========================================
st.divider()
st.subheader("📊 Hasil Data Terkumpul")

if not st.session_state['master_data'].empty:
    df_final = st.session_state['master_data']
    
    # Filter Cepat
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        max_pe = st.number_input("Filter Max P/E:", value=100.0)
    with col_f2:
        min_roe = st.number_input("Filter Min ROE (%):", value=0.0)
        
    # Terapkan Filter
    mask = (df_final['P/E Ratio'] <= max_pe) & (df_final['ROE (%)'] >= min_roe)
    df_display = df_final[mask]
    
    st.write(f"Menampilkan {len(df_display)} dari {len(df_final)} saham.")
    
    # Formatting
    st.dataframe(
        df_display.style.format({
            'Harga': "Rp {:,.0f}",
            'P/E Ratio': "{:.2f}x",
            'PBV': "{:.2f}x",
            'ROE (%)': "{:.2f}%",
            'Market Cap (T)': "{:.2f} T"
        }),
        use_container_width=True,
        height=500
    )
    
    # Tombol Download Excel
    # Fungsi convert ke CSV
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df_final)

    st.download_button(
        label="📥 Download Data Lengkap (CSV)",
        data=csv,
        file_name='data_saham_jumbo.csv',
        mime='text/csv',
    )
else:
    st.caption("Belum ada data. Silakan masukkan saham dan mulai proses batch.")
