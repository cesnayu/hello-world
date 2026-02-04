
# @title 1. Install Library (Jalankan ini dulu jika belum install)
!
pip install yfinance matplotlib pandas

# @title 2. Run Chart Generator (Top 100 IHSG)
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math

# --- 1. DAFTAR SAHAM (TOP 100 Estimasi) ---
tickers = [
    "BREN.JK", "BBCA.JK", "DSSA.JK", "BBRI.JK", "TPIA.JK", "BYAN.JK", "DCII.JK", "AMMN.JK", "BMRI.JK", "TLKM.JK",
    "ASII.JK", "MORA.JK", "SRAJ.JK", "CUAN.JK", "BRPT.JK", "BBNI.JK", "PANI.JK", "BNLI.JK", "BRMS.JK", "CDIA.JK",
    "MDKA.JK", "UNTR.JK", "KLBF.JK", "GOTO.JK", "ICBP.JK", "ADMR.JK", "MBMA.JK", "INKP.JK", "MTEL.JK", "PGEO.JK",
    "TOWR.JK", "TBIG.JK", "INCO.JK", "MASA.JK", "JSMR.JK", "SMGR.JK", "MIKA.JK", "CMRY.JK", "MYOR.JK", "INDF.JK",
    "UNVR.JK", "CPIN.JK", "BRIS.JK", "BNGA.JK", "ANTM.JK", "MEDC.JK", "ISAT.JK", "EXCL.JK", "PGAS.JK", "PTBA.JK",
    "HMSP.JK", "GGRM.JK", "AMRT.JK", "MAPI.JK", "ACES.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "SMRA.JK", "AKRA.JK",
    "HEAL.JK", "SILO.JK", "MAPA.JK", "AUTO.JK", "BJBR.JK", "BJTM.JK", "PNBN.JK", "BDMN.JK", "NISP.JK", "BBTN.JK",
    "TKIM.JK", "INTP.JK", "EMTK.JK", "AADI.JK", "ADRO.JK", "BUMI.JK", "ENRG.JK", "FILM.JK", "VKTR.JK", "NCKL.JK",
    "MAHA.JK", "SIDO.JK", "ULTJ.JK", "JPFA.JK", "TINS.JK", "HRUM.JK", "ITMG.JK", "ELSA.JK", "RAJA.JK", "MIDI.JK",
    "ERAA.JK", "ASSA.JK", "DSNG.JK", "TAPG.JK", "STAA.JK", "SSIA.JK", "MNCN.JK", "SCMA.JK", "AVIA.JK", "ARTO.JK"
]

# --- 2. KONFIGURASI ---
PERIOD = "3mo"       # Durasi data: 3 bulan
MA_WINDOW = 20       # Moving Average 20
COLS = 4             # Jumlah kolom (berjajar 4)
ROWS = math.ceil(len(tickers) / COLS)

# Setup ukuran gambar (Lebar tetap, Tinggi menyesuaikan jumlah baris)
fig, axes = plt.subplots(ROWS, COLS, figsize=(20, 4 * ROWS))
axes = axes.flatten() # Meratakan array axes agar mudah di-loop

print("Sedang mengambil data dan membuat grafik... Mohon tunggu sebentar.")

# --- 3. LOOPING & PLOTTING ---
for i, ticker in enumerate(tickers):
    ax = axes[i]
    try:
        # Ambil data
        df = yf.download(ticker, period=PERIOD, progress=False)
        
        if df.empty:
            ax.text(0.5, 0.5, "Data Tidak Ditemukan", ha='center', va='center')
            ax.set_title(ticker)
            continue

        # Hitung MA20
        # Menggunakan 'Close' untuk perhitungan. 
        # yfinance terbaru kadang return MultiIndex, kita pastikan ambil kolom Close saja.
        if isinstance(df.columns, pd.MultiIndex):
            close_price = df['Close'].iloc[:, 0]
        else:
            close_price = df['Close']
            
        ma20 = close_price.rolling(window=MA_WINDOW).mean()

        # Plot Harga
        ax.plot(df.index, close_price, label='Price', color='black', linewidth=1.5)
        
        # Plot MA20
        ax.plot(df.index, ma20, label='MA20', color='orange', linewidth=1.5)

        # Kosmetik Grafik
        ax.set_title(f"{ticker}", fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        
        # Hilangkan label axis yang berlebihan agar rapi
        if i < len(tickers) - COLS: 
            ax.set_xticklabels([]) # Hanya tampilkan tanggal di baris paling bawah

    except Exception as e:
        ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', fontsize=8)
        ax.set_title(ticker)

# --- 4. RAPIKAN SISA SLOT KOSONG ---
# Jika jumlah saham tidak pas kelipatan 4, sembunyikan grafik kosong sisanya
for j in range(len(tickers), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.subplots_adjust(hspace=0.4) # Jarak antar baris
plt.show()

