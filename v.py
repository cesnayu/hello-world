import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Screening Fundamental & Teknikal", layout="wide")

# --- JUDUL & INPUT ---
st.title("📊 Dashboard Screening Saham (Jan 2025 - Sekarang)")
st.markdown("Menganalisa Harga Tertinggi/Terendah sejak **Januari 2025** serta Valuasi PBV & PER saat ini.")

# Default List Saham (Bluechip + Bank)
default_tickers = "BREN, BBCA, DSSA, BBRI, TPIA, DCII, BYAN, AMMN, BMRI, TLKM, ASII, MORA, SRAJ, CUAN, BRPT, BBNI, PANI, BNLI, BRMS, CDIA, DNET, IMPC, FILM, MPRO, BRIS, ICBP, HMSP, BUMI, EMAS, UNTR, ANTM, NCKL, SMMA, ADMR, CASA, UNVR, RISE, CPIN, MLPT, AMRT, MDKA, ISAT, MBMA, GOTO, INCO, AADI, INDF, PTRO, BELI, ADRO, EXCL, TCPI, KLBF, EMTK, MYOR, PGAS, INKP, PGUN, PGEO, GEMS, MTEL, BNGA, CMRY, ARCI, TBIG, MEGA, SILO, MEDC, GIAA, SOHO, VKTR, CBDK, MIKA, NISP, JPFA, GGRM, TOWR, BBHI, ENRG, TAPG, SUPA, BUVA, PTBA, BINA, COIN, AVIA, JSMR, AKRA, NSSS, PNBN, ITMG, BDMN, ARKO, MDIY, TINS, BSIM, INTP, JARR, BKSL, BTPN, ARTO, FAPA, MKPI, RMKE, SRTG, TKIM, MAPA, MSIN, MAPI, RLCO, HEAL, BSDE, KPIG, CITA, PWON, BNBR, APIC, BBTN, SMGR, RAJA, POLU, LIFE, BNII, INDY, CTRA, SMAR, SCMA, SSMS, CARE, ULTJ, SIDO, DSNG, BBSI, BUKA, AALI, RATU, BBKP, HRUM, CMNT, SGRO, PSAB, JRPT, YUPI, STAA, STTP, GOOD, MCOL, WIFI, AUTO, TSPC, NICL, ALII, SHIP, MLBI, PACK, DEWA, CYBR, PRAY, POWR, ESSA, BMAS, MIDI, EDGE, BIPI, BSSR, SMSM, ADMF, ELPI, BFIN, HRTA, CLEO, BTPS, CMNP, CNMA, BANK, ADES, INPP, BJBR, SIMP, BJTM, PNLF, INET, SINI, TLDN, GMFI, NATO, BBMD, LSIP, TMAS, ABMM, DUTI, BHAT, DAAZ, SGER, DMND, CLAY, IBST, MTDL, BULL, ACES, LPKR, DMAS, SMRA, SSIA, ERAA, EPMT, SMDR, KRAS, JSPT, BOGA, MAYA, AGII, OMED, PALM, ANJT, TOBA, DATA, BESS, INDS, CASS, ELSA, AGRO, SAME, UANG, MNCN, LINK, BPII, YULE, TRIN, BALI, UDNG, PBSA, CTBN, DRMA, NIRO, DKFT, GTSI, MTLA, BBYB, TFCO, ROTI, FISH, TRIM, PYFA, TGKA, GOLF, KIJA, JTPE, MASB, HUMI, FORE, MPMX, RDTX, MSTI, BSWD, IMAS, BIRD, LPCK, ASSA, TUGU, BWPT, WIIM, RONY, LPPF, CENT, SDRA, SURE, VICI, MGLV, NOBU, KEEN, PSGO, AMAR, CPRO, CBRE, SOCI, ARNA, TBLA, STAR, GJTL, VICO, PBID, INPC, GGRP, IRSX, AGRS, HEXA, TOTL, UNIC, SMMT, BUKK, ROCK, SKRN, MDLA, MMLP, MINA, BACA, MAPB, KEJU, BGTG, SOTS, MBSS, SAMF, BHIT, ARGO, CBUT, PNIN, MARK, SMDM, ISSP, FPNI, APLN, MYOH, ASRI, SMIL, DAYA, KAEF, IFSH, BNBA, RALS, JAWA, MCOR, PKPK, HATM, TOTO, BCIC, IATA, MAHA, FOLK, SMBR, SFAN, BISI, BABP, FUTR, PSKT, OASA, ASLI, SSTM, SIPD, MGRO, PORT, DNAR, MKAP, BVIC, BOLT, PNGO, IPCC, BLTZ, ASGR, POLI, DWGL, BMTR, GMTD, WINS, IFII, MSJA, BCAP, OMRE, BEEF, KMTR, NICE, BKSW, PRDA, DOID, TRUE, BLUE, MDIA, WOOD, ACST, IMJS, AMAG, PTPP, MTMH, CSRA, MLIA, ITMA, DGWG, KETR, NRCA, DMMX, SCCO, INDR, PNBS, BRAM, LUCY, MBAP, TPMA, ELTY, IPTV, STRK, TEBE, ADHI, LPGI, SUNI, HILL, PSSI, MINE, FAST, DVLA, ERAL, HERO, KINO, CSAP, UCID, IPCM, MLPL, VISI, PTSN, BBRM, SPTO, FMII, PPRE, MAIN, AYAM, EURO, SKLT, DEPO, BSBK, MKTR, BMHS, NEST, PMJS, BEKS, KKGI, DLTA, AMFG, RAAM, TRGU, ALDO, GWSA, PSAT, GSMF, CARS, PADI, BBLD, DOOH, ABDA, BELL, NETV, MERK, BLOG, DILD, TAMU, CEKA, ATIC, TRST, SONA, BBSS, KBLI, BLES, CFIN, JKON, TIFA, CAMP, RANC, MITI, TCID, WSBP, GZCO, AISA, CITY, JIHD, LTLS, IBOS, ADCP, ARTA, BUAH, INDO, WOMF, BEST, PANS, TBMS, ENAK, RSCH, BLTA, JGLE, MTWI, ARII, BTEK, AREA, BOLA, SHID, ZINC, ASLC, PEVE, LIVE, MMIX, GHON, CHIP, WIRG, GDST, PBRX, GRIA, ATAP, CMPP, NELY, RMKO, NICK, SMGA, SPMA, RELI, HGII, BUDI, SKBM, COCO, LEAD, VOKS, PDPP, MHKI, NFCX, PTPW, PJAA, ZATA, NIKL, FUJI, AMOR, PANR, ADMG, MGNA, TALF, AMAN, BABY, MTFN, WTON, IPOL, SULI, PMUI, KSIX, PADA, LFLO, BPFI, JECC, FORU, HDFA, KOKA, BDKR, DGIK, WMUU, PGJO, RODA, KDSI, AXIO, TIRA, MDLN, MOLI, BEER, HOKI, BRNA, GTBO, BIKE, UNIQ, MPPA, APEX, AHAP, GTRA, SWID, IKBI, HOMI, HOPE, EKAD, VIVA, UNSP, PEGE, PZZA, SOFA, IRRA, ELIT, WEGE, SOSS, AWAN, SMKL, GLVA, TRIS, KOTA, GUNA, HAIS, UNTD, CHEK, LABS, BOAT, PNSE, MREI, FITT, KONI, VTNY, URBN, TRON, IDPR, WINE, DART, PJHB, GPRA, MDKI, KING, CNKO, UFOE, BSML, VERN, HALO, COAL, APLI, CRAB, ESTA, SURI, MDRN, MAXI, KMDS, CLPI, BAYU, VRNA, TIRT, IGAR, LAPD, IKPM, SCNP, MCAS, REAL, RIGS, CCSI, GDYR, GULA, NASA, PDES, CSIS, GOLD, PTPS, CBPE, SOLA, TYRE, ZONE, BIPP, BKDP, ESTI, IOTF, LPLI, VAST, HYGN, ASRM, KREN, SMLE, DYAN, DGNS, EAST, HAJJ, TFAS, SRSN, JATI, KBLM, DADA, BMSR, KOBX, NAIK, KBAG, TARA, SATU, ASPR, ASHA, YOII, UVCR, CRSN, YPAS, TRUS, ATLA, INTA, ERTX, GPSO, PART, MUTU, SAFE, KLAS, AKPI, ITIC, CGAS, EMDE, MICE, VINS, ASMI, HRME, BPTR, AMIN, ASPI, IKAI, BINO, SAGE, TOSK, BTON, OKAS, MPXL, WGSH, ACRO, AGAR, INOV, POLA, LMPI, FIRE, ANDI, PUDP, DOSS, FWCT, AKSI, CASH, KBLV, PRIM, NTBK, DEWI, OBAT, ASJT, ALKA, ECII, RELF, LCKM, PEHA, AKKU, ENZO, AYLS, INPS, BAJA, WINR, ASDM, SDPC, TRJA, SAPX, WAPO, PTMP, BAUT, MEJA, JMAS, LPPS, OBMD, NPGF, NZIA, MANG, LION, TAXI, PTSP, APII, CAKK, NANO, SLIS, DFAM, WOWS, SDMU, CINT, ZYRX, DKHH, MRAT, ABBA, BOBA, DIVA, PURA, MARI, PAMG, BAPI, CANI, KOPI, DSFI, SMKM, WEHA, PURI, LPIN, IBFN, RUIS, NAYZ, LAJU, TRUK, LAND, KARW, HELI, CHEM, SEMA, PSDN, IPAC, SNLK, INTD, MSKY, MBTO, KRYA, ASBI, INCI, TMPO, GEMA, ISAP, YELO, MERI, PTIS, ISEA, FOOD, LABA, MPIX, RGAS, DEFI, KUAS, SBMA, EPAC, RCCC, KIOS, INAI, RBMS, MIRA, NASI, MEDS, CSMI, CTTH, OLIV, JAST, IDEA, OPMS, PTDU, PGLI, FLMC, BCIP, INCF, HDIT, JAYA, AIMS, RUNS, POLY, OILS, BATA, KOIN, ICON, LRNA, MPOW, PICO, IKAN, TAYS, ESIP, KJEN, LUCK, TNCA, KICI, SOUL, ARKA, PLAN, BMBL, BAPA, RICY, WIDI, DIGI, INDX, HADE, TAMA, PCAR, LOPI, GRPH, HBAT, PIPA, KLIN, PPRI, AEGS, SPRE, KAQI, NINE, KOCI, LMAX, BRRC, RAFI, TOOL, BATR, AMMS, KKES, SICO, BAIK, GRPM, KDTN, MSIE"

input_saham = st.text_area("Masukkan Kode Saham (pisahkan koma):", value=default_tickers)

# --- FUNGSI UTAMA ---
@st.cache_data(ttl=3600) # Cache data selama 1 jam biar gak loading terus
def get_stock_data(tickers_input):
    # 1. Cleaning Ticker Input
    # Pastikan formatnya XXXX.JK
    raw_tickers = [x.strip().upper() for x in tickers_input.split(',')]
    formatted_tickers = []
    for t in raw_tickers:
        if not t.endswith(".JK"):
            formatted_tickers.append(f"{t}.JK")
        else:
            formatted_tickers.append(t)
    
    # Hapus duplikat
    formatted_tickers = list(set(formatted_tickers))

    if not formatted_tickers:
        return None, "List saham kosong."

    # 2. Ambil Data Historis (Batch - Cepat)
    # Start Date: 1 Januari 2025
    start_date = "2025-01-01"
    
    progress_text = "Mengambil data harga historis..."
    my_bar = st.progress(0, text=progress_text)

    try:
        # Download data harga sekaligus
        hist_data = yf.download(formatted_tickers, start=start_date, group_by='ticker', progress=False, threads=True)
    except Exception as e:
        return None, f"Gagal download history: {e}"
    
    my_bar.progress(30, text="Mengambil data fundamental (PBV/PER)... Mohon tunggu.")

    # 3. Proses Data & Ambil Fundamental (Looping - Agak Lama)
    results = []
    
    total_stocks = len(formatted_tickers)
    
    for i, ticker in enumerate(formatted_tickers):
        try:
            # Update Progress Bar
            progress_percent = 30 + int((i / total_stocks) * 70)
            my_bar.progress(progress_percent, text=f"Menganalisa fundamental: {ticker}")

            # --- A. PROSES HARGA (TEKNIKAL) ---
            # Handling MultiIndex dataframe dari yfinance
            if len(formatted_tickers) > 1:
                df_ticker = hist_data[ticker]
            else:
                df_ticker = hist_data # Kalau cuma 1 saham
            
            # Skip jika data kosong
            if df_ticker.empty:
                continue
                
            # Drop NaN di kolom Close
            df_ticker = df_ticker.dropna(subset=['Close'])
            
            if df_ticker.empty:
                continue

            # Hitung High, Low, Current sejak Jan 2025
            highest_price = df_ticker['High'].max()
            lowest_price = df_ticker['Low'].min()
            current_price = df_ticker['Close'].iloc[-1]
            
            # Hitung Posisi Harga (0% = di Low, 100% = di High)
            if highest_price != lowest_price:
                position_pct = ((current_price - lowest_price) / (highest_price - lowest_price)) * 100
            else:
                position_pct = 0

            # --- B. PROSES FUNDAMENTAL (VALUASI) ---
            # Kita perlu memanggil .info untuk setiap saham
            stock_info = yf.Ticker(ticker).info
            
            pbv = stock_info.get('priceToBook', None)
            per = stock_info.get('trailingPE', None)
            name = stock_info.get('shortName', ticker)

            results.append({
                'Ticker': ticker.replace('.JK', ''),
                'Nama': name,
                'Harga Saat Ini': current_price,
                'Terendah (Sejak Jan 25)': lowest_price,
                'Tertinggi (Sejak Jan 25)': highest_price,
                'Posisi Harga (%)': position_pct, # Indikator Diskon
                'PBV (x)': pbv,
                'PER (x)': per
            })
            
        except Exception as e:
            print(f"Error {ticker}: {e}")
            continue

    my_bar.empty() # Hapus progress bar setelah selesai
    
    if not results:
        return None, "Gagal mengambil data."

    return pd.DataFrame(results), None

# --- TOMBOL EKSEKUSI ---
# --- TOMBOL EKSEKUSI ---
# Logika: Jika tombol ditekan, ambil data BARU dan simpan ke Session State
if st.button("🚀 Analisa Saham"):
    with st.spinner("Sedang mengambil data..."):
        df_result, error = get_stock_data(input_saham)
        
        if error:
            st.error(error)
        else:
            # SIMPAN KE SESSION STATE (MEMORI)
            st.session_state['data_saham'] = df_result
            st.success("Data berhasil diambil!")

# --- BAGIAN TAMPILAN (DILUAR IF BUTTON) ---
if 'data_saham' in st.session_state:
    # Ambil data dari memori
    df_result = st.session_state['data_saham'].copy() # Pakai .copy() biar aman

    # ==========================================
    # 0. PEMBERSIHAN DATA (FIX TYPE ERROR DISINI)
    # ==========================================
    # Kita paksa kolom ini jadi angka. Kalau ada error/None, ubah jadi NaN (Not a Number)
    cols_to_fix = ['PBV (x)', 'PER (x)', 'Posisi Harga (%)']
    
    for col in cols_to_fix:
        df_result[col] = pd.to_numeric(df_result[col], errors='coerce')

    # ==========================================
    # 1. BAGIAN FILTERING
    # ==========================================
    st.divider()
    st.subheader("🔍 Filter Data")
    
    fil1, fil2, fil3 = st.columns(3)
    
    with fil1:
        pbv_range = st.slider(
            "Rentang PBV (x)", 
            min_value=0.0, max_value=10000.0, value=(0.0, 10.0), step=0.1
        )
        
    with fil2:
        per_range = st.slider(
            "Rentang PER (x)", 
            min_value=0.0, max_value=10000.0, value=(0.0, 30.0), step=0.5
        )
        
    with fil3:
        pos_range = st.slider(
            "Posisi Harga (%)", 
            min_value=0.0, max_value=100.0, value=(0.0, 100.0), step=5.0
        )

    # PROSES PENYARINGAN (LOGIKA LEBIH AMAN)
    # Kita buat masker boolean agar kodenya tidak kepanjangan dan error
    
    # 1. Masker untuk PBV (Harus Angka & Masuk Range)
    mask_pbv = (df_result['PBV (x)'].notna()) & \
               (df_result['PBV (x)'] >= pbv_range[0]) & \
               (df_result['PBV (x)'] <= pbv_range[1])

    # 2. Masker untuk PER (Harus Angka & Masuk Range)
    mask_per = (df_result['PER (x)'].notna()) & \
               (df_result['PER (x)'] >= per_range[0]) & \
               (df_result['PER (x)'] <= per_range[1])

    # 3. Masker untuk Posisi Harga
    mask_pos = (df_result['Posisi Harga (%)'] >= pos_range[0]) & \
               (df_result['Posisi Harga (%)'] <= pos_range[1])

    # Terapkan semua filter sekaligus
    df_filtered = df_result[mask_pbv & mask_per & mask_pos]

    st.caption(f"Menampilkan **{len(df_filtered)}** saham dari total {len(df_result)} saham.")

    # ==========================================
    # 2. TAMPILKAN TABEL
    # ==========================================
    column_config = {
        "Ticker": st.column_config.TextColumn("Kode", width="small"),
        "Harga Saat Ini": st.column_config.NumberColumn("Harga", format="Rp %d"),
        "Terendah (Sejak Jan 25)": st.column_config.NumberColumn("Low (Jan25)", format="Rp %d"),
        "Tertinggi (Sejak Jan 25)": st.column_config.NumberColumn("High (Jan25)", format="Rp %d"),
        "Posisi Harga (%)": st.column_config.ProgressColumn(
            "Posisi",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),
        "PBV (x)": st.column_config.NumberColumn("PBV", format="%.2fx"),
        "PER (x)": st.column_config.NumberColumn("PER", format="%.2fx"),
    }

    if not df_filtered.empty:
        st.dataframe(
            df_filtered,
            column_config=column_config,
            use_container_width=True,
            height=500,
            hide_index=True
        )
    else:
        st.warning("⚠️ Tidak ada saham yang sesuai filter.")
       # --- FORMATTING DATAFRAME (VERSI ANTI ERROR) ---
        st.subheader("📋 Tabel Detail")
        
        # Penjelasan Kolom
        st.info("💡 **Posisi Harga (%)**: 0% = Harga di Titik Terendah (Low), 100% = Harga di Pucuk (High).")

        # Konfigurasi Kolom Streamlit (Ini yang menangani format angka & NaN)
        column_config = {
            "Ticker": st.column_config.TextColumn("Kode", width="small"),
            "Harga Saat Ini": st.column_config.NumberColumn("Harga", format="Rp %d"),
            "Terendah (Sejak Jan 25)": st.column_config.NumberColumn("Low (Jan25)", format="Rp %d"),
            "Tertinggi (Sejak Jan 25)": st.column_config.NumberColumn("High (Jan25)", format="Rp %d"),
            "Posisi Harga (%)": st.column_config.ProgressColumn(
                "Posisi (Low ke High)",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "PBV (x)": st.column_config.NumberColumn("PBV", format="%.2fx"), # Streamlit otomatis handle jika data kosong
            "PER (x)": st.column_config.NumberColumn("PER", format="%.2fx"), # Streamlit otomatis handle jika data kosong
        }

        # Tampilkan DataFrame TANPA style.format yang bikin error
        st.dataframe(
            df_result,
            column_config=column_config,
            use_container_width=True,
            height=600,
            hide_index=True
        )
