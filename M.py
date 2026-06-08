import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Mengatur judul halaman web Streamlit
st.set_page_config(page_title="IHSG Top 100 Dashboard", layout="wide")
st.title("📊 IHSG Top 100 - Harga, Finansial & Dividend Yield")
st.write("Aplikasi melacak Harga terkini, 52-Week High, Pertumbuhan Laba, dan Persentase Dividen.")

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

def konversi_ke_kuartal(timestamp_mentah):
    if not timestamp_mentah:
        return "N/A"
    try:
        if isinstance(timestamp_mentah, (int, float)):
            if timestamp_mentah > 1e11:
                timestamp_mentah = timestamp_mentah / 1000
            dt = pd.to_datetime(timestamp_mentah, unit='s')
        else:
            dt = pd.to_datetime(timestamp_mentah)
        kuartal = (dt.month - 1) // 3 + 1
        return f"Q{kuartal} {dt.year}"
    except:
        return "N/A"

@st.cache_data(ttl=3600)
def ambil_data_saham_super_lengkap():
    saham_data = []
    
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
            
            # 1. Net Profit Growth YoY
            net_profit_yoy = info.get('earningsQuarterlyGrowth')
            if net_profit_yoy is not None:
                net_profit_yoy = round(net_profit_yoy * 100, 2)
            
            # 2. Periode Laporan Keuangan
            periode_raw = info.get('mostRecentQuarter')
            periode_laporan = konversi_ke_kuartal(periode_raw)
            
            # 3. Dividend Yield (Dikali 100 karena data mentah berupa desimal, contoh 0.05 -> 5%)
            div_yield = info.get('dividendYield')
            if div_yield is not None:
                div_yield = round(div_yield * 100, 2)
            else:
                div_yield = 0.0  # Jika tidak ada riwayat dividen terbaru
            
            # Hitung Jarak/Selisih ke 52-Week High
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
                "Diskon dr High (%)": round(selisih_persen, 2),
                "Net Profit Growth YoY (%)": net_profit_yoy,
                "Dividend Yield (%)": div_yield,
                "Periode Laporan": periode_laporan
            })
            
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

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

df_saham = ambil_data_saham_super_lengkap()

if not df_saham.empty:
    st.success("Data berhasil diperbarui!")
    
    # Menampilkan tabel interaktif dengan format yang rapi
    st.dataframe(
        df_saham.style.format({
            "Market Cap (IDR)": "{:,.0f}",
            "Harga Terkini": "{:,.0f}",
            "52-Week High": "{:,.0f}",
            "Selisih (IDR)": "{:,.0f}",
            "Diskon dr High (%)": "{:.2f}%",
            "Net Profit Growth YoY (%)": lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A",
            "Dividend Yield (%)": "{:.2f}%"
        }),
        use_container_width=True
    )
    
    # Tombol Download data
    csv = df_saham.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Laporan Lengkap (CSV)", data=csv, file_name="ihsg_top100_lengkap.csv", mime="text/csv")
else:
    st.warning("Gagal mengambil data. Coba klik tombol Refresh.")
