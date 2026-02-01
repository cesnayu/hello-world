import streamlit as st
import yfinance as yf
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Konsistensi Top Gainer Fix", layout="wide")

# --- LIST SAHAM (Kompas100 + Populer) ---
TIKCER_LIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'ICBP.JK', 'INDF.JK', 'KLBF.JK',
    'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK', 'ITMG.JK', 'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK',
    'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 'EXCL.JK', 'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK',
    'MNCN.JK', 'SCMA.JK', 'GGRM.JK', 'HMSP.JK', 'WIIM.JK', 'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK',
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK', 'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 'UNTR.JK', 'MEDC.JK',
    'HRUM.JK', 'TPIA.JK', 'INKP.JK', 'TKIM.JK', 'JPFA.JK', 'MYOR.JK', 'BUMI.JK', 'ENRG.JK', 'DEWA.JK', 'BRMS.JK',
    'ARTO.JK', 'BRIS.JK', 'AGRO.JK', 'BBHI.JK', 'BBYB.JK', 'PNBN.JK', 'BDMN.JK', 'BNGA.JK', 'NISP.JK', 'BJBR.JK',
    'SSIA.JK', 'BEST.JK', 'DMAS.JK', 'KIJA.JK', 'AUTO.JK', 'GJTL.JK', 'IMAS.JK', 'SMSM.JK', 'KAEF.JK', 'IRRA.JK',
    'SILO.JK', 'MIKA.JK', 'HEAL.JK', 'SAME.JK', 'FILM.JK', 'MBMA.JK', 'NCKL.JK', 'TRIM.JK', 'DOID.JK',
    'INDY.JK', 'ABMM.JK', 'KKGI.JK', 'TOBA.JK', 'HILL.JK', 'CUAN.JK', 'BREN.JK', 'AMMN.JK', 'PANI.JK', 'MAPA.JK',
    'ULTJ.JK', 'CMRY.JK', 'STAA.JK', 'TAPG.JK', 'DSNG.JK', 'AALI.JK', 'LSIP.JK', 'SIMP.JK', 'SSMS.JK', 'TBLA.JK',
    'AVIA.JK', 'MARK.JK', 'WOOD.JK', 'FREN.JK', 'TLDN.JK', 'DRMA.JK', 'RAJA.JK', 'APLN.JK', 'ASRI.JK', 'LPKR.JK',
    'LPPF.JK', 'RALS.JK', 'MPPA.JK', 'AMAR.JK', 'BABP.JK', 'BCIC.JK', 'BEKS.JK', 'BGTG.JK', 'BINA.JK', 'BMAS.JK'
]

@st.cache_data(ttl=600)
def analyze_top_gainers(tickers):
    # 1. Download Data
    # Kita gunakan threads=False kadang lebih stabil di cloud gratisan untuk batch besar
    try:
        data = yf.download(" ".join(tickers), period="1mo", group_by='ticker', threads=True, progress=False)
    except Exception as e:
        return None, f"Gagal download data: {str(e)}"

    if data.empty:
        return None, "Data kosong dari Yahoo Finance. Coba refresh."
    
    # 2. Parsing Struktur Data (MultiIndex Handling)
    close_prices = pd.DataFrame()
    
    # Ambil kolom Close dengan aman
    for t in tickers:
        try:
            # Cek apakah ticker ada di kolom level atas
            if isinstance(data.columns, pd.MultiIndex) and t in data.columns.levels[0]:
                series = data[t]['Close']
            elif not isinstance(data.columns, pd.MultiIndex):
                # Kasus jika cuma 1 saham (jarang terjadi di sini tapi buat jaga2)
                series = data['Close']
            else:
                continue
                
            # Bersihkan data kosong
            series = series.dropna()
            if not series.empty:
                close_prices[t] = series
        except: 
            continue
            
    # Hapus baris (tanggal) yang kosong semua
    close_prices.dropna(how='all', inplace=True)
    
    # Cek kecukupan data
    if close_prices.empty or len(close_prices) < 6:
        return None, "Data pasar tidak cukup (kurang dari 6 hari bursa) atau gagal parsing."
        
    last_6_days = close_prices.tail(6)
    
    # 3. Hitung Persentase
    daily_returns = last_6_days.pct_change().dropna() * 100
    
    if daily_returns.empty:
        return None, "Gagal menghitung return harian."

    # 4. Cari Top 50 Per Hari
    top_50_occurrences = []
    dates = [d.strftime('%d %b') for d in daily_returns.index]
    
    for date in daily_returns.index:
        day_ret = daily_returns.loc[date].sort_values(ascending=False)
        top_50_today = day_ret.head(50).index.tolist()
        top_50_occurrences.extend(top_50_today)
        
    # 5. Hitung Frekuensi & Return Akhir
    counter = Counter(top_50_occurrences)
    final_results = []
    unique_tickers = list(counter.keys())
    
    for t in unique_tickers:
        try:
            freq = counter[t]
            price_end = last_6_days[t].iloc[-1]
            price_start = last_6_days[t].iloc[0]
            total_ret_5d = ((price_end - price_start) / price_start) * 100
            
            final_results.append({
                'Ticker': t.replace('.JK', ''),
                'Harga': price_end,
                'Frekuensi Masuk Top 50': freq,
                'Total Gainer 5 Hari (%)': total_ret_5d,
                'Avg Daily Return': daily_returns[t].mean()
            })
        except: continue
        
    # --- BAGIAN PERBAIKAN ERROR KEYERROR ---
    if not final_results:
        return None, "Tidak ada saham yang memenuhi kriteria (List kosong)."

    df_res = pd.DataFrame(final_results)
    
    # Pastikan kolom ada sebelum sort
    required_cols = ['Frekuensi Masuk Top 50', 'Total Gainer 5 Hari (%)']
    if all(col in df_res.columns for col in required_cols):
        df_res = df_res.sort_values(by=required_cols, ascending=[False, False])
    
    return df_res, dates

# --- UI UTAMA ---
st.title("🏆 Konsistensi Top Gainer (5 Hari Terakhir)")
st.markdown("""
Dashboard ini mencari saham yang **paling sering masuk ke daftar 'Top 50 Gainer Harian'** selama 5 hari perdagangan terakhir.
""")

if st.button("🔄 Scan Market"):
    with st.spinner("Menganalisa data harian (ini mungkin butuh waktu 10-20 detik)..."):
        # Reset cache manual jika mau fresh (opsional)
        # st.cache_data.clear()
        
        df_result, info = analyze_top_gainers(TIKCER_LIST)
        
    if df_result is not None:
        if isinstance(info, list):
            st.success(f"Analisa Periode: {info[0]} s/d {info[-1]}")
        else:
            st.success("Data berhasil diambil.")
        
        col_config = {
            "Ticker": st.column_config.TextColumn("Saham"),
            "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
            "Frekuensi Masuk Top 50": st.column_config.ProgressColumn(
                "Konsistensi (x)",
                format="%d kali",
                min_value=0,
                max_value=5,
            ),
            "Total Gainer 5 Hari (%)": st.column_config.NumberColumn("Total Return 5 Hari", format="%.2f%%"),
            "Avg Daily Return": st.column_config.NumberColumn("Rata2 Harian", format="%.2f%%")
        }
        
        st.dataframe(
            df_result,
            hide_index=True,
            use_container_width=True,
            column_config=col_config,
            height=600
        )
        
        st.divider()
        st.subheader("🔥 Saham Paling Konsisten (Muncul >= 3 kali)")
        top_picks = df_result[df_result['Frekuensi Masuk Top 50'] >= 3]
        if not top_picks.empty:
            st.write(f"Ditemukan {len(top_picks)} saham konsisten:")
            st.write(", ".join(top_picks['Ticker'].tolist()))
        else:
            st.write("Pasar sedang fluktuatif, tidak ada saham yang mendominasi top gainer > 2 hari berturut-turut.")
            
    else:
        st.error(f"Terjadi kesalahan: {info}")
