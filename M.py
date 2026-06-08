pip install yfinance pandas tqdm openpyxl
import yfinance as yf
import pandas as pd
from tqdm import tqdm
import time

# Daftar ticker 100 saham dengan market cap terbesar/teraktif di IHSG (menggunakan suffix .JK)
tickers = [
    "BBCA.JK", "BREN.JK", "BBRI.JK", "BMRI.JK", "BYAN.JK", "TLKM.JK", "AMMN.JK", "ASII.JK", "TPIA.JK", "BBNI.JK",
    "PANI.JK", "UNVR.JK", "ICBP.JK", "HMSP.JK", "GOTO.JK", "AMRT.JK", "UNTR.JK", "ADRO.JK", "KLBF.JK", "CPIN.JK",
    "BRPT.JK", "SMMA.JK", "INDF.JK", "SMGR.JK", "PGAS.JK", "PTBA.JK", "ITMG.JK", "INCO.JK", "ANTM.JK", "EXCL.JK",
    "ISAT.JK", "TOWR.JK", "TBIG.JK", "JSMR.JK", "AKRA.JK", "BRIS.JK", "BSDE.JK", "PWON.JK", "CTRA.JK", "SMRA.JK",
    "MYOR.JK", "GGRM.JK", "ACES.JK", "ERAA.JK", "MEDC.JK", "ENRG.JK", "BRMS.JK", "FILM.JK", "BDMN.JK", "BBTN.JK",
    "PNBN.JK", "BNGA.JK", "BTPS.JK", "BFIN.JK", "SCMA.JK", "MNCN.JK", "EMTK.JK", "BUKA.JK", "GEMS.JK", "MBMA.JK",
    "NCKL.JK", "ADMR.JK", "HRUM.JK", "TINS.JK", "PTRO.JK", "CUAN.JK", "HEAL.JK", "MIKA.JK", "SILO.JK", "SAME.JK",
    "MAPA.JK", "MAPI.JK", "RALS.JK", "LPPF.JK", "MIDI.JK", "AVIA.JK", "CMRY.JK", "SSMS.JK", "SIMP.JK", "AALI.JK",
    "LSIP.JK", "TAPG.JK", "DSNG.JK", "BWPT.JK", "SMDR.JK", "MAIN.JK", "EAST.JK", "AUTO.JK", "GJTL.JK", "SMSM.JK",
    "MTDL.JK", "BNLI.JK", "MPRO.JK", "DNET.JK", "SRAJ.JK", "MORA.JK", "DSSA.JK", "DCII.JK", "MASA.JK", "BBHI.JK"
]

saham_data = []

print("Sedang mengambil data dari Yahoo Finance (Mohon tunggu)...")

# Menggunakan loop dengan progress bar tqdm agar terlihat prosesnya
for ticker in tqdm(tickers):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Ekstrak data faktual dengan fallback nilai 0 jika data kosong
        market_cap = info.get('marketCap', 0)
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
        high_52week = info.get('fiftyTwoWeekHigh', 0)
        nama_perusahaan = info.get('longName', ticker)
        
        # Hitung selisih harga nominal dan persentase jarak ke harga tertinggi 52-week
        if current_price and high_52week:
            selisih_harga = high_52week - current_price
            selisih_persen = (selisih_harga / high_52week) * 100
        else:
            selisih_harga = 0
            selisih_persen = 0
            
        saham_data.append({
            "Ticker": ticker.replace(".JK", ""),
            "Nama Perusahaan": nama_perusahaan,
            "Market Cap (IDR)": market_cap,
            "Harga Terkini": current_price,
            "52-Week High": high_52week,
            "Selisih (IDR)": selisih_harga,
            "Selisih (%)": round(selisih_persen, 2)
        })
        
        # Jeda singkat 0.1 detik untuk menghindari request terlalu agresif ke server
        time.sleep(0.1)
        
    except Exception as e:
        # Jika ada ticker bermasalah, otomatis dilewati
        continue

# Mengubah list data menjadi Pandas DataFrame
df = pd.DataFrame(saham_data)

# Mengurutkan ulang berdasarkan Market Cap terbesar (memastikan urutan top 100 mutakhir)
df = df.sort_values(by="Market Cap (IDR)", ascending=False).reset_index(drop=True)

# Format visualisasi tabel di terminal agar tidak terpotong
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Menampilkan hasil data ke layar konsol
print("\n=== DATA TOP 100 SAHAM IHSG BY MARKET CAP ===")
print(df.to_string())

# PILIHAN: Hilangkan tanda pagar (#) di bawah ini jika ingin langsung disimpan ke Excel
# df.to_excel("top_100_saham_ihsg.xlsx", index=False)
# print("\nData berhasil disimpan ke 'top_100_saham_ihsg.xlsx'!")
