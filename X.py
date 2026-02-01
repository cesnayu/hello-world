import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Kalender Dividen 2025", layout="wide")

# --- LIST SAHAM DEFAULT (Bisa diubah user) ---
DEFAULT_TEXT = "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, UNVR, ITMG, ADRO, PTBA, HEXA"

# --- FUNGSI AMBIL DIVIDEN ---
def get_dividend_schedule(tickers_list, target_year=2025):
    results = []
    
    # Progress Bar UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(tickers_list)
    
    for i, ticker in enumerate(tickers_list):
        # Format ticker ke .JK jika belum ada
        symbol = ticker.upper().strip()
        if not symbol.endswith(".JK"):
            symbol += ".JK"
            
        status_text.text(f"Mengecek dividen: {symbol} ({i+1}/{total})")
        progress_bar.progress((i + 1) / total)
        
        try:
            stock = yf.Ticker(symbol)
            # Ambil histori dividen
            divs = stock.dividends
            
            # Pastikan index adalah datetime
            if not isinstance(divs.index, pd.DatetimeIndex):
                divs.index = pd.to_datetime(divs.index)
            
            # Filter hanya tahun target (2025)
            # Kita perlu handle timezone agar tidak error saat compare
            divs_target = divs[divs.index.year == target_year]
            
            if not divs_target.empty:
                for date, amount in divs_target.items():
                    results.append({
                        'Ticker': symbol.replace('.JK', ''),
                        'Ex-Date': date, # Ini tanggal penting (Ex-Date)
                        'Dividen (Rp)': amount,
                        'Bulan': date.strftime('%B') # Nama Bulan
                    })
                    
        except Exception as e:
            continue
            
    progress_bar.empty()
    status_text.empty()
    
    # Sorting berdasarkan tanggal
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by='Ex-Date', ascending=True)
        return df
    else:
        return pd.DataFrame()

# --- UI UTAMA ---
st.title("📅 Cek Jadwal Dividen Saham 2025")
st.markdown("""
Aplikasi ini mengecek data resmi dari Yahoo Finance untuk jadwal pembagian dividen di tahun 2025.
* **Catatan:** Jika perusahaan belum mengumumkan dividen secara resmi, data tidak akan muncul.
""")

# 1. INPUT SAHAM
with st.expander("📝 Edit Daftar Saham", expanded=True):
    user_input = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=DEFAULT_TEXT)

# 2. TOMBOL CEK
if st.button("🔍 Cek Dividen Sekarang"):
    # Parsing input user menjadi list
    tickers = [x.strip() for x in user_input.split(',') if x.strip()]
    
    if tickers:
        df_result = get_dividend_schedule(tickers, target_year=2025)
        
        if not df_result.empty:
            st.success(f"Ditemukan {len(df_result)} jadwal pembagian dividen di tahun 2025.")
            
            # Format Tanggal agar enak dibaca (dd Month YYYY)
            # Kita copy dulu biar gak ngerusak data asli buat sorting
            df_display = df_result.copy()
            df_display['Ex-Date'] = df_display['Ex-Date'].dt.strftime('%d %B %Y')
            
            # TAMPILKAN TABEL
            st.dataframe(
                df_display[['Ex-Date', 'Ticker', 'Dividen (Rp)', 'Bulan']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Dividen (Rp)": st.column_config.NumberColumn(
                        "Jumlah Dividen",
                        format="Rp %.2f"
                    ),
                    "Ex-Date": st.column_config.TextColumn("Tanggal Ex-Date (Cum Date H-1)"),
                }
            )
            
            # TOTAL DIVIDEN
            st.info("💡 **Tips:** Tanggal yang tertera biasanya adalah **Ex-Date**. Jika kamu ingin mendapatkan dividen, kamu harus membeli saham minimal 1 hari sebelum tanggal tersebut (Cum Date).")
            
        else:
            st.warning("Belum ada data dividen 2025 yang ditemukan untuk daftar saham tersebut (atau belum diumumkan).")
    else:
        st.error("Mohon masukkan kode saham.")
