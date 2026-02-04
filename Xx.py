import streamlit as st  # Wajib import ini
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math

# Judul Web
st.title("Top 100 IHSG Chart Generator")

# --- 1. DAFTAR SAHAM ---
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

# --- 2. CONFIG ---
PERIOD = "3mo"
MA_WINDOW = 20
COLS = 4
ROWS = math.ceil(len(tickers) / COLS)

st.write("Sedang mengambil data... Mohon tunggu.")

# Setup Plot
fig, axes = plt.subplots(ROWS, COLS, figsize=(20, 4 * ROWS))
axes = axes.flatten()

# --- 3. LOOPING ---
# Kita gunakan st.progress bar karena loadingnya agak lama
progress_bar = st.progress(0)

for i, ticker in enumerate(tickers):
    ax = axes[i]
    try:
        df = yf.download(ticker, period=PERIOD, progress=False)
        
        if df.empty:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center')
        else:
            # Fix MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                close = df['Close'].iloc[:, 0]
            else:
                close = df['Close']
            
            ma20 = close.rolling(window=MA_WINDOW).mean()
            ax.plot(df.index, close, color='black', linewidth=1)
            ax.plot(df.index, ma20, color='orange', linewidth=1)

        ax.set_title(ticker, fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        if i < len(tickers) - COLS: ax.set_xticklabels([])

    except Exception as e:
        ax.text(0.5, 0.5, "Error", ha='center', va='center')

    # Update progress bar
    progress_bar.progress((i + 1) / len(tickers))

# Bersihkan sisa
for j in range(len(tickers), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()

# --- TAMPILKAN DI WEB ---
st.pyplot(fig)  # Ganti plt.show() dengan ini
