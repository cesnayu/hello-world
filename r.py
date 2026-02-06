import yfinance as yf
import pandas as pd

# ==========================================
# 1. ISI DAFTAR SAHAM KAMU DI SINI
# ==========================================
# Pastikan pakai akhiran .JK
daftar_saham = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'BRIS.JK', # Bank
    'ASII.JK', 'TLKM.JK', 'GOTO.JK', 'AMRT.JK',            # Bluechip Lain
    'ADRO.JK', 'PTBA.JK', 'PGEO.JK', 'BREN.JK',            # Energi
    'ANTM.JK', 'MDKA.JK', 'UNVR.JK', 'ICBP.JK'             # Lainnya
]

# ==========================================
# 2. PENGATURAN FILTER VOLUME
# ==========================================
# Hanya tampilkan saham dengan rata-rata volume di atas angka ini
# (Misal: 100000 lembar saham) agar tidak terjebak saham tidak likuid.
MINIMUM_VOLUME = 100000 

# ==========================================
# 3. PROSES PENGAMBILAN DATA
# ==========================================
print(f"Sedang menganalisa {len(daftar_saham)} saham untuk performa 5 hari terakhir...\n")

data_analisa = []

for ticker in daftar_saham:
    try:
        # Ambil data 1 bulan terakhir untuk memastikan kita punya cukup hari bursa
        # (Karena ada libur/sabtu minggu, kita ambil buffer lebih panjang)
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        # Cek apakah data cukup (minimal butuh 6 baris untuk hitung selisih 5 hari)
        if len(hist) >= 6:
            # Harga Sekarang (Close Terakhir)
            price_now = hist['Close'].iloc[-1]
            
            # Harga 5 Hari Bursa yang lalu (Index -6 karena -1 adalah hari ini)
            price_5days_ago = hist['Close'].iloc[-6]
            
            # Volume Rata-rata 5 Hari Terakhir
            avg_volume = hist['Volume'].iloc[-5:].mean()
            
            # Hitung Return (%)
            # Rumus: (Harga Akhir - Harga Awal) / Harga Awal * 100
            total_gain_5d = ((price_now - price_5days_ago) / price_5days_ago) * 100
            
            data_analisa.append({
                'Ticker': ticker.replace('.JK', ''),
                'Harga Awal (H-5)': int(price_5days_ago),
                'Harga Akhir': int(price_now),
                'Avg Volume': int(avg_volume),
                'Total Gain 5D (%)': round(total_gain_5d, 2)
            })
        else:
            print(f"⚠️ {ticker}: Data history kurang dari 5 hari (Mungkin saham baru IPO/Suspensi).")
            
    except Exception as e:
        print(f"❌ Error pada {ticker}: {e}")

# ==========================================
# 4. FILTER & SORTING
# ==========================================
if len(data_analisa) > 0:
    df = pd.DataFrame(data_analisa)
    
    # FILTER: Hapus saham yang volumenya kecil (di bawah settingan kamu)
    df_filtered = df[df['Avg Volume'] >= MINIMUM_VOLUME]
    
    # SORTING: Urutkan berdasarkan 'Total Gain 5D (%)'
    # ascending=False artinya dari BESAR ke KECIL (Gainer di atas)
    # ascending=True artinya dari KECIL ke BESAR (Loser di atas)
    df_sorted = df_filtered.sort_values(by='Total Gain 5D (%)', ascending=False)
    
    # Reset penomoran baris biar rapi 1, 2, 3...
    df_sorted.reset_index(drop=True, inplace=True)

    print("\n" + "="*60)
    print("HASIL ANALISA RETURN 5 HARI TERAKHIR (URUT DARI GAIN TERTINGGI)")
    print("="*60)
    print(df_sorted)
    
    # Export ke Excel (Opsional, hilangkan pagar jika mau pakai)
    # df_sorted.to_excel("Analisa_5Hari.xlsx", index=False)
    # print("\nFile Excel 'Analisa_5Hari.xlsx' berhasil disimpan!")

else:
    print("Tidak ada data yang berhasil diambil.")
