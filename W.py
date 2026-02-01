import streamlit as st
import yfinance as yf
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Konsistensi Top Gainer", layout="wide")

# --- LIST SAHAM (Harus banyak agar Top 50 valid) ---
# Ini daftar gabungan Kompas100 + Saham Second Liner populer (+/- 150 saham)
TIKCER_LIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'ICBP.JK', 'INDF.JK', 'KLBF.JK',
    'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK', 'ITMG.JK', 'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK',
    'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 'EXCL.JK', 'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK',
    'MNCN.JK', 'SCMA.JK', 'GGRM.JK', 'HMSP.JK', 'WIIM.JK', 'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK',
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK', 'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 'UNTR.JK', 'MEDC.JK',
    'HRUM.JK', 'TPIA.JK', 'INKP.JK', 'TKIM.JK', 'JPFA.JK', 'MYOR.JK', 'BUMI.JK', 'ENRG.JK', 'DEWA.JK', 'BRMS.JK',
    'ARTO.JK', 'BRIS.JK', 'AGRO.JK', 'BBHI.JK', 'BBYB.JK', 'PNBN.JK', 'BDMN.JK', 'BNGA.JK', 'NISP.JK', 'BJBR.JK',
    'SSIA.JK', 'BEST.JK', 'DMAS.JK', 'KIJA.JK', 'AUTO.JK', 'GJTL.JK', 'IMAS.JK', 'SMSM.JK', 'KAEF.JK', 'IRRA.JK',
    'SILO.JK', 'MIKA.JK', 'HEAL.JK', 'SAME.JK', 'FILM.JK', 'MDKA.JK', 'MBMA.JK', 'NCKL.JK', 'TRIM.JK', 'DOID.JK',
    'INDY.JK', 'ABMM.JK', 'KKGI.JK', 'TOBA.JK', 'HILL.JK', 'CUAN.JK', 'BREN.JK', 'AMMN.JK', 'PANI.JK', 'MAPA.JK',
    'ULTJ.JK', 'CMRY.JK', 'STAA.JK', 'TAPG.JK', 'DSNG.JK', 'AALI.JK', 'LSIP.JK', 'SIMP.JK', 'SSMS.JK', 'TBLA.JK',
    'AVIA.JK', 'MARK.JK', 'WOOD.JK', 'FREN.JK', 'TLDN.JK', 'DRMA.JK', 'RAJA.JK', 'APLN.JK', 'ASRI.JK', 'LPKR.JK',
    'LPPF.JK', 'RALS.JK', 'MPPA.JK', 'AMAR.JK', 'BABP.JK', 'BCIC.JK', 'BEKS.JK', 'BGTG.JK', 'BINA.JK', 'BMAS.JK'
]

@st.cache_data(ttl=600)
def analyze_top_gainers(tickers):
    # 1. Download Data (Close Price) untuk 10 hari (biar aman dapet 5 hari bursa)
    data = yf.download(" ".join(tickers), period="1mo", group_by='ticker', threads=True, progress=False)
    
    # Ambil Harga Close saja
    # Struktur yf.download sekarang agak tricky, kita pastikan ambil Close
    close_prices = pd.DataFrame()
    for t in tickers:
        try:
            # Cek struktur multi-index atau single
            if len(tickers) > 1:
                if t in data.columns.levels[0]:
                    close_prices[t] = data[t]['Close']
            else:
                close_prices[t] = data['Close']
        except: continue
        
    # Hapus baris yang kosong semua
    close_prices.dropna(how='all', inplace=True)
    
    # Ambil 6 hari terakhir (untuk menghitung 5 hari perubahan)
    if len(close_prices) < 6:
        return None, "Data pasar tidak cukup (kurang dari 6 hari bursa)."
        
    last_6_days = close_prices.tail(6)
    
    # 2. Hitung Persentase Perubahan Harian
    # pct_change() menghitung perubahan dari baris sebelumnya
    daily_returns = last_6_days.pct_change().dropna() * 100
    # daily_returns sekarang isinya 5 baris terakhir (Hari 1 s/d Hari 5)
    
    # 3. Cari Top 50 Per Hari & Hitung Frekuensi
    top_50_occurrences = []
    
    # List tanggal untuk header
    dates = [d.strftime('%d %b') for d in daily_returns.index]
    
    # Loop setiap hari (baris)
    for date in daily_returns.index:
        # Ambil return hari itu, urutkan descending (tertinggi)
        day_ret = daily_returns.loc[date].sort_values(ascending=False)
        # Ambil Top 50 ticker
        top_50_today = day_ret.head(50).index.tolist()
        # Masukkan ke list besar untuk dihitung nanti
        top_50_occurrences.extend(top_50_today)
        
    # 4. Hitung Berapa Kali Muncul (Frequency)
    counter = Counter(top_50_occurrences)
    
    # 5. Susun Data Akhir
    final_results = []
    
    # Ambil saham yang setidaknya muncul 1x di Top 50
    unique_tickers = list(counter.keys())
    
    for t in unique_tickers:
        freq = counter[t]
        
        # Hitung Total Return 5 Hari (Compounding atau Simple Growth dari H-5 ke H-0)
        # Rumus: (Harga Akhir - Harga Awal) / Harga Awal
        price_end = last_6_days[t].iloc[-1]
        price_start = last_6_days[t].iloc[0] # Harga H-6 (sebelum hari pertama perhitungan)
        
        total_ret_5d = ((price_end - price_start) / price_start) * 100
        
        final_results.append({
            'Ticker': t.replace('.JK', ''),
            'Harga': price_end,
            'Frekuensi Masuk Top 50': freq, # Berapa kali masuk list
            'Total Gainer 5 Hari (%)': total_ret_5d,
            'Avg Daily Return': daily_returns[t].mean() # Rata-rata kenaikan harian
        })
        
    df_res = pd.DataFrame(final_results)
    
    # Urutkan berdasarkan Frekuensi dulu, baru Total Return
    df_res = df_res.sort_values(by=['Frekuensi Masuk Top 50', 'Total Gainer 5 Hari (%)'], ascending=[False, False])
    
    return df_res, dates

# --- UI UTAMA ---
st.title("🏆 Konsistensi Top Gainer (5 Hari Terakhir)")
st.markdown("""
Dashboard ini mencari saham yang **paling sering masuk ke daftar 'Top 50 Gainer Harian'** selama 5 hari perdagangan terakhir.
* **Maksud kolom kanan:** Jika angkanya **5**, berarti saham tersebut **selalu** masuk Top 50 Gainer setiap hari selama seminggu ini (Sangat Strong Uptrend).
* **Saham yang discan:** +/- 150 Saham (Kompas100 + Second Liner Populer).
""")

if st.button("🔄 Scan Market"):
    with st.spinner("Menganalisa data harian..."):
        df_result, info_dates = analyze_top_gainers(TIKCER_LIST)
        
    if df_result is not None:
        st.success(f"Analisa dari tanggal: {info_dates[0]} s/d {info_dates[-1]}")
        
        # Konfigurasi Kolom
        col_config = {
            "Ticker": st.column_config.TextColumn("Saham"),
            "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
            "Frekuensi Masuk Top 50": st.column_config.ProgressColumn(
                "Konsistensi (x)",
                help="Berapa kali saham ini masuk Top 50 Gainer dalam 5 hari terakhir",
                format="%d kali",
                min_value=0,
                max_value=5, # Maksimal 5 hari
            ),
            "Total Gainer 5 Hari (%)": st.column_config.NumberColumn(
                "Total Return 5 Hari",
                format="%.2f%%"
            ),
            "Avg Daily Return": st.column_config.NumberColumn(
                "Rata2 Harian",
                format="%.2f%%"
            )
        }
        
        # Tampilkan Data
        st.dataframe(
            df_result,
            hide_index=True,
            use_container_width=True,
            column_config=col_config,
            height=600
        )
        
        # Highlight Top Picks
        st.divider()
        st.subheader("🔥 Saham Paling Konsisten (Muncul >= 3 kali)")
        top_picks = df_result[df_result['Frekuensi Masuk Top 50'] >= 3]
        if not top_picks.empty:
            st.write(f"Ada {len(top_picks)} saham yang sangat konsisten naik:")
            st.write(", ".join(top_picks['Ticker'].tolist()))
        else:
            st.write("Tidak ada saham yang masuk Top 50 lebih dari 2 kali minggu ini (Pasar mungkin sedang choppy/bergantian).")
            
    else:
        st.error(info_dates)
