import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Stock Comparison Dashboard", layout="wide")

st.title("⚖️ Stock Perbandingan Fundamental")
st.markdown("Bandingkan **P/E, P/S, ROE, DER, dan EPS** dari banyak saham sekaligus.")

# --- INPUT SAHAM ---
default_tickers = "BREN, BBCA, DSSA, BBRI, TPIA, DCII, BYAN, AMMN, BMRI, TLKM, ASII, MORA, SRAJ, CUAN, BRPT, BBNI, PANI, BNLI, BRMS, CDIA, DNET, IMPC, FILM, MPRO, BRIS, ICBP, HMSP, BUMI, EMAS, UNTR, ANTM, NCKL, SMMA, ADMR, CASA, UNVR, RISE, CPIN, MLPT, AMRT, MDKA, ISAT, MBMA, GOTO, INCO, AADI, INDF, PTRO, BELI, ADRO, EXCL, TCPI, KLBF, EMTK, MYOR, PGAS, INKP, PGUN, PGEO, GEMS, MTEL, BNGA, CMRY, ARCI, TBIG, MEGA, SILO, MEDC, GIAA, SOHO, VKTR, CBDK, MIKA, NISP, JPFA, GGRM, TOWR, BBHI, ENRG, TAPG, SUPA, BUVA, PTBA, BINA, COIN, AVIA, JSMR, AKRA, NSSS, PNBN, ITMG, BDMN, ARKO, MDIY, TINS, BSIM, INTP, JARR, BKSL, BTPN, ARTO, FAPA, MKPI, RMKE, SRTG, TKIM, MAPA, MSIN, MAPI, RLCO, HEAL, BSDE, KPIG, CITA, PWON, BNBR, APIC, BBTN, SMGR, RAJA, POLU, LIFE, BNII, INDY, CTRA, SMAR, SCMA, SSMS, CARE, ULTJ, SIDO, DSNG, BBSI, BUKA, AALI, RATU, BBKP, HRUM, CMNT, SGRO, PSAB, JRPT, YUPI, STAA, STTP, GOOD, MCOL, WIFI, AUTO, TSPC, NICL, ALII, SHIP, MLBI, PACK, DEWA, CYBR, PRAY, POWR, ESSA, BMAS, MIDI, EDGE, BIPI, BSSR, SMSM, ADMF, ELPI, BFIN, HRTA, CLEO, BTPS, CMNP, CNMA, BANK, ADES, INPP, BJBR, SIMP, BJTM, PNLF, INET, SINI, TLDN, GMFI, NATO, BBMD, LSIP, TMAS, ABMM, DUTI, BHAT, DAAZ, SGER, DMND, CLAY, IBST, MTDL, BULL, ACES, LPKR, DMAS, SMRA, SSIA, ERAA, EPMT, SMDR, KRAS, JSPT, BOGA, MAYA, AGII, OMED, PALM, ANJT, TOBA, DATA, BESS, INDS, CASS, ELSA, AGRO, SAME, UANG, MNCN, LINK, BPII, YULE, TRIN, BALI, UDNG, PBSA, CTBN, DRMA, NIRO, DKFT, GTSI, MTLA, BBYB, TFCO, ROTI, FISH, TRIM, PYFA, TGKA, GOLF, KIJA, JTPE, MASB, HUMI, FORE, MPMX, RDTX, MSTI, BSWD, IMAS, BIRD, LPCK, ASSA, TUGU, BWPT, WIIM, RONY, LPPF, CENT, SDRA, SURE, VICI, MGLV, NOBU, KEEN, PSGO, AMAR, CPRO, CBRE, SOCI, ARNA, TBLA, STAR, GJTL, VICO, PBID, INPC, GGRP, IRSX, AGRS, HEXA, TOTL, UNIC, SMMT, BUKK, ROCK, SKRN, MDLA, MMLP, MINA, BACA, MAPB, KEJU, BGTG, SOTS, MBSS, SAMF, BHIT, ARGO, CBUT, PNIN, MARK, SMDM, ISSP, FPNI, APLN, MYOH, ASRI, SMIL, DAYA, KAEF, IFSH, BNBA, RALS, JAWA, MCOR, PKPK, HATM, TOTO, BCIC, IATA, MAHA, FOLK, SMBR, SFAN, BISI, BABP, FUTR, PSKT, OASA, ASLI, SSTM, SIPD, MGRO, PORT, DNAR, MKAP, BVIC, BOLT, PNGO, IPCC, BLTZ, ASGR, POLI, DWGL, BMTR, GMTD, WINS, IFII, MSJA, BCAP, OMRE, BEEF"
input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=default_tickers)

# --- FUNGSI AMBIL DATA ---
def get_fundamental_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Mengambil data fundamental...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menganalisa {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            name = info.get('shortName', ticker)
            price = info.get('currentPrice', 0)
            
            # Ambil data (Default None jika gagal)
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            
            # Konversi ROE ke Persen jika ada
            if roe is not None: roe = roe * 100

            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': price,
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except Exception:
            continue

    progress_bar.empty()
    return pd.DataFrame(data)

# --- TOMBOL PROSES ---
if st.button("🚀 Bandingkan Sekarang"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        df = get_fundamental_data(input_saham)
        
        if not df.empty:
            st.success(f"Berhasil membandingkan {len(df)} saham.")
            
            # --- PENTING: BERSIHKAN DATA SEBELUM DITAMPILKAN ---
            # 1. Pastikan semua kolom angka terbaca sebagai float (bukan object/string)
            cols_to_numeric = ['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']
            for col in cols_to_numeric:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Ubah error jadi NaN (Not a Number)

            # --- TAMPILAN TABEL ---
            st.subheader("📋 Tabel Perbandingan (Heatmap)")

            # Konfigurasi Tampilan (Streamlit yang menangani format angka)
            column_config = {
                "Kode": st.column_config.TextColumn("Ticker", width="small"),
                "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
                "P/E Ratio (x)": st.column_config.NumberColumn("P/E Ratio", format="%.2fx"),
                "P/S Ratio (x)": st.column_config.NumberColumn("P/S Ratio", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "DER (%)": st.column_config.NumberColumn("Debt/Eq", format="%.2f%%"),
                "EPS (Rp)": st.column_config.NumberColumn("EPS", format="Rp %.2f"),
            }

            # --- STYLING (Hanya Warna, Tanpa Format Angka) ---
            # Kita hapus .format() dari sini agar tidak bentrok dengan NoneType
            # background_gradient akan otomatis mengabaikan NaN (tetap putih)
            styled_df = df.style\
                .background_gradient(subset=['ROE (%)', 'EPS (Rp)'], cmap='RdYlGn')\
                .background_gradient(subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'DER (%)'], cmap='RdYlGn_r')

            st.dataframe(
                styled_df,
                column_config=column_config,
                use_container_width=True,
                height=500,
                hide_index=True
            )
            
            # --- GRAFIK ---
            st.divider()
            st.subheader("📊 Visualisasi Grafik")
            metric_choice = st.selectbox("Pilih Metrik:", ['P/E Ratio (x)', 'ROE (%)', 'DER (%)', 'P/S Ratio (x)'])
            
            # Drop NaN sebelum plot grafik agar bar chart tidak error
            chart_df = df[['Kode', metric_choice]].dropna().set_index('Kode')
            st.bar_chart(chart_df)
                
        else:
            st.error("Data tidak ditemukan atau koneksi bermasalah.")
