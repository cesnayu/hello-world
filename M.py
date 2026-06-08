import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Mengatur judul halaman web Streamlit
st.set_page_config(page_title="IHSG Top 100 Market Cap", layout="wide")
st.title("📊 Data Saham IHSG Top 100 by Market Cap")
st.write("Mengambil data harga terkini, 52-Week High, dan selisihnya secara langsung.")

# Daftar 100 Ticker Saham
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

# Menggunakan cache Streamlit agar data tidak ditarik ulang dari internet setiap kali web diklik
@st.cache_data(ttl=3600)  # Data disimpan di cache selama 1 jam (3600 detik)
def ambil_data_saham():
    saham_data = []
    
    # Progress bar di Streamlit
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers):
        try:
            status_text.text(f"Mengambil data: {ticker} ({idx+1}/{len(tickers)})")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            market_cap = info.get('marketCap', 0)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
            high_52week = info.get('fiftyTwoWeekHigh', 0)
            nama_perusahaan = info.get('longName', ticker)
            
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
            
            # Update progress bar
            progress_bar.progress((idx + 1) / len(tickers))
            time.sleep(0.05)
            
        except Exception:
            continue
            
    status_text.empty()
    progress_bar.empty()
    
    df = pd.DataFrame(saham_data)
    if not df.empty:
        df = df.sort_values(by="Market Cap (IDR)", ascending=False).reset_index(drop=True)
    return df

# Tombol untuk memicu penarikan data
if st.button("🔄 Ambil / Refresh Data Saham"):
    st.cache_data.clear()  # Hapus cache lama jika tombol ditekan

df_saham = ambil_data_saham()

if not df_saham.empty:
    # Menampilkan data dalam bentuk tabel interaktif di Streamlit
    st.success("Data berhasil dimuat!")
    
    # Format tampilan kolom agar lebih rapi membaca angka besar
    st.dataframe(
        df_saham.style.format({
            "Market Cap (IDR)": "{:,.0f}",
            "Harga Terkini": "{:,.0f}",
            "52-Week High": "{:,.0f}",
            "Selisih (IDR)": "{:,.0f}",
            "Selisih (%)": "{:.2f}%"
        }),
        use_container_width=True
    )
    
    # Fitur download data ke CSV langsung dari web
    csv = df_saham.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data ke CSV/Excel",
        data=csv,
        file_name="top_100_saham_ihsg.csv",
        mime="text/csv"
    )
else:
    st.warning("Gagal mengambil data atau data kosong. Coba klik tombol Refresh di atas.")
