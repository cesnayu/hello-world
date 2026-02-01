import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Screening 5 Hari", layout="wide")

# --- LIST SAHAM (Bisa diedit) ---
ALL_TICKERS = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'ICBP.JK', 
    'INDF.JK', 'KLBF.JK', 'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK', 'ITMG.JK', 
    'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK', 'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 
    'EXCL.JK', 'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK', 'MNCN.JK', 'SCMA.JK', 
    'GGRM.JK', 'HMSP.JK', 'WIIM.JK', 'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK', 
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK', 'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 
    'UNTR.JK', 'MEDC.JK', 'HRUM.JK', 'TPIA.JK', 'INKP.JK', 'TKIM.JK', 'JPFA.JK', 'MYOR.JK'
]

# --- FUNGSI AMBIL RETURN 5 HARI TERAKHIR ---
@st.cache_data(ttl=600)
def get_5_day_returns(tickers):
    # Ambil data agak panjang (1 bulan) biar aman kepotong libur
    data = yf.download(" ".join(tickers), period="1mo", group_by='ticker', threads=True, progress=False)
    
    results = []
    
    for ticker in tickers:
        try:
            # Handling struktur data
            if len(tickers) > 1:
                if ticker not in data.columns.levels[0]: continue
                hist = data[ticker]['Close'].dropna()
            else:
                hist = data['Close'].dropna()
            
            if len(hist) >= 6: # Butuh minimal 6 data untuk hitung 5 return
                # Hitung Persentase Perubahan Harian
                pct_change = hist.pct_change() * 100
                
                # Ambil 5 hari terakhir
                last_5 = pct_change.tail(5)
                # Balik urutan biar hari terbaru di kiri (opsional, tapi saya buat urut tanggal)
                
                # Buat Dictionary row
                row = {
                    'Pilih': False, # Kolom Checkbox
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga Terakhir': hist.iloc[-1]
                }
                
                # Masukkan return per tanggal ke kolom dinamis
                # Contoh: "30 Jan", "29 Jan"
                total_return_5d = 0
                for date, val in last_5.items():
                    date_col = date.strftime('%d %b') # Format tgl: 30 Jan
                    row[date_col] = val
                    total_return_5d += val # Simple sum (bisa diganti compounding)
                
                row['Total 5 Hari (%)'] = total_return_5d
                results.append(row)
        except:
            continue
            
    return pd.DataFrame(results)

# --- UI UTAMA ---
st.title("📋 Screening Return 5 Hari Terakhir")
st.write("Centang saham di kolom kiri (**Pilih**) untuk menganalisis portfolio pilihanmu.")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# 1. LOAD DATA
with st.spinner("Mengambil data return saham..."):
    df = get_5_day_returns(ALL_TICKERS)

if not df.empty:
    # Siapkan Kolom Konfigurasi agar Tampilannya Persen tapi Datanya Angka
    # Kita harus mendeteksi nama kolom tanggal secara dinamis
    date_columns = [col for col in df.columns if col not in ['Pilih', 'Ticker', 'Harga Terakhir', 'Total 5 Hari (%)']]
    
    # Config untuk st.data_editor
    column_config = {
        "Pilih": st.column_config.CheckboxColumn(
            "Pilih",
            help="Centang untuk analisa detail",
            default=False,
        ),
        "Ticker": st.column_config.TextColumn("Saham", disabled=True),
        "Harga Terakhir": st.column_config.NumberColumn("Harga", format="Rp %d"),
        "Total 5 Hari (%)": st.column_config.NumberColumn(
            "Total 5D", 
            format="%.2f%%", 
            help="Total kenaikan/penurunan 5 hari terakhir"
        )
    }
    
    # Tambahkan config untuk kolom tanggal (agar formatnya %)
    for col in date_columns:
        column_config[col] = st.column_config.NumberColumn(
            col,
            format="%.2f%%" # INI KUNCINYA: Tampil %, tapi aslinya angka (bisa disort)
        )

    # 2. TAMPILKAN TABEL EDITOR
    # st.data_editor memungkinkan user mencentang baris
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        height=500,
        disabled=["Ticker", "Harga Terakhir"] + date_columns # Kunci kolom data biar gak keedit, cuma checkbox yg bisa
    )

    # 3. LOGIKA SETELAH KLIK ENTER / PILIH
    # Filter baris yang dicentang
    selected_stocks = edited_df[edited_df['Pilih'] == True]
    
    st.divider()
    
    # Tampilkan Hasil Seleksi
    if not selected_stocks.empty:
        st.subheader(f"✅ Terpilih: {len(selected_stocks)} Saham")
        
        # Hitung Rata-rata Return Portfolio Pilihan
        avg_return = selected_stocks['Total 5 Hari (%)'].mean()
        color_avg = "green" if avg_return > 0 else "red"
        
        st.metric("Rata-rata Return Pilihan (5 Hari)", f"{avg_return:.2f}%")
        
        st.write("Detail Pilihan:")
        st.dataframe(
            selected_stocks[['Ticker', 'Harga Terakhir', 'Total 5 Hari (%)'] + date_columns],
            hide_index=True,
            column_config=column_config
        )
    else:
        st.info("Belum ada saham yang dipilih. Silakan centang kotak di tabel atas.")

else:
    st.error("Gagal mengambil data. Coba refresh.")
