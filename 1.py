import yfinance as yf
import pandas as pd

# ==========================================
# 1. ISI DAFTAR SAHAM DI SINI (EDIT BAGIAN INI)
# ==========================================
# Ganti kode di bawah sesuai keinginanmu.
# Jangan lupa akhiran .JK untuk saham Indonesia.
daftar_saham = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'BRIS.JK', # Bank
    'ASII.JK', 'TLKM.JK', 'GOTO.JK',                       # Big Caps
    'ADRO.JK', 'PTBA.JK', 'PGEO.JK',                       # Energi
    'ANTM.JK', 'MDKA.JK', 'TINS.JK',                       # Tambang
    'UNVR.JK', 'ICBP.JK', 'MYOR.JK',                       # Consumer
    'SRTG.JK', 'MEDC.JK'                                   # Lainnya
]

print("Sedang mengambil data pasar... Mohon tunggu sebentar.")

# ==========================================
# 2. PROSES PENGAMBILAN DATA
# ==========================================
try:
    # Kita ambil data 1 bulan terakhir untuk memastikan dapat 5 hari perdagangan yang valid
    # (Karena ada hari libur/sabtu minggu)
    df = yf.download(daftar_saham, period="1mo", progress=False)['Close']
    
    # Ambil 6 baris data terakhir (Hari ini + 5 hari ke belakang untuk pembanding)
    df_last_5 = df.tail(6)
    
    # Cek apakah datanya cukup
    if len(df_last_5) < 6:
        print("Data belum cukup (mungkin saham baru IPO atau data belum update).")
    else:
        # ==========================================
        # 3. HITUNG RETURN (GAIN/LOSS)
        # ==========================================
        
        # Harga Hari Ini (Baris Terakhir)
        price_now = df_last_5.iloc[-1]
        
        # Harga 5 Hari Lalu (Baris Pertama dari potongan data)
        price_5days_ago = df_last_5.iloc[0]
        
        # Rumus Return: (Harga Sekarang - Harga 5 Hari Lalu) / Harga 5 Hari Lalu
        total_return_5d = ((price_now - price_5days_ago) / price_5days_ago) * 100
        
        # Buat DataFrame Hasil
        result_df = pd.DataFrame({
            'Harga Terakhir': price_now,
            'Harga 5 Hari Lalu': price_5days_ago,
            'Total Gain 5D (%)': total_return_5d
        })

        # ==========================================
        # 4. SORTING / PENGURUTAN (PENTING)
        # ==========================================
        # Mengurutkan dari Gain Tertinggi ke Terendah (Descending)
        # Jika mau sebaliknya (Loser di atas), ubah ascending=True
        result_df = result_df.sort_values(by='Total Gain 5D (%)', ascending=False)
        
        # ==========================================
        # 5. FORMAT TAMPILAN
        # ==========================================
        # Format angka desimal agar rapi (2 angka di belakang koma)
        pd.options.display.float_format = '{:,.2f}'.format
        
        print("\n" + "="*50)
        print(" LAPORAN RETURN 5 HARI TERAKHIR (SORTED)")
        print("="*50)
        
        # Tampilkan Kolom yang perlu saja
        print(result_df[['Harga Terakhir', 'Total Gain 5D (%)']])
        
        print("\n" + "="*50)
        
        # Highlight Top Gainer & Top Loser
        top_gainer = result_df.index[0]
        top_gainer_val = result_df['Total Gain 5D (%)'].iloc[0]
        
        top_loser = result_df.index[-1]
        top_loser_val = result_df['Total Gain 5D (%)'].iloc[-1]
        
        print(f"🏆 JUARA GAIN : {top_gainer} (+{top_gainer_val:.2f}%)")
        print(f"💀 PALING BONCOS: {top_loser} ({top_loser_val:.2f}%)")
        print("="*50)

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
