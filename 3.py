import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dynamic Stock Screener", layout="wide")

st.title("🔍 Search First, Filter Later")
st.markdown("""
**Alur Kerja:**
1. Masukkan list saham & Klik **"Ambil Data"**.
2. Lihat range data (Min/Max) yang muncul.
3. Atur filter di panel bawah untuk menandai mana yang **Lolos (Hijau)** dan **Gagal (Merah)**.
""")

# --- FUNGSI AMBIL DATA ---
def get_fundamental_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Mengambil data...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Cek {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Ambil data point
            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': info.get('currentPrice'),
                'P/E Ratio (x)': info.get('trailingPE'),
                'P/S Ratio (x)': info.get('priceToSalesTrailing12Months'),
                'ROE (%)': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'DER (%)': info.get('debtToEquity'),
                'EPS (Rp)': info.get('trailingEps')
            })
        except:
            continue

    progress_bar.empty()
    return pd.DataFrame(data)

# --- BAGIAN 1: INPUT & SEARCH ---
default_tickers = BREN, BBCA, DSSA, BBRI, TPIA, DCII, BYAN, AMMN, BMRI, TLKM, ASII, MORA, SRAJ, CUAN, BRPT, BBNI, PANI, BNLI, BRMS, CDIA, DNET, IMPC, FILM, MPRO, BRIS, ICBP, HMSP, BUMI, EMAS, UNTR, ANTM, NCKL, SMMA, ADMR, CASA, UNVR, RISE, CPIN, MLPT, AMRT, MDKA, ISAT, MBMA, GOTO, INCO, AADI, INDF, PTRO, BELI, ADRO, EXCL, TCPI, KLBF, EMTK, MYOR, PGAS, INKP, PGUN, PGEO, GEMS, MTEL, BNGA, CMRY, ARCI, TBIG, MEGA, SILO, MEDC, GIAA, SOHO, VKTR, CBDK, MIKA, NISP, JPFA, GGRM, TOWR, BBHI, ENRG, TAPG, SUPA, BUVA, PTBA, BINA, COIN, AVIA, JSMR, AKRA, NSSS, PNBN, ITMG, BDMN, ARKO, MDIY, TINS, BSIM, INTP, JARR, BKSL, BTPN, ARTO, FAPA, MKPI, RMKE, SRTG, TKIM, MAPA, MSIN, MAPI, RLCO, HEAL, BSDE, KPIG, CITA, PWON, BNBR, APIC, BBTN, SMGR, RAJA, POLU, LIFE, BNII, INDY, CTRA, SMAR, SCMA, SSMS, CARE, ULTJ, SIDO, DSNG, BBSI, BUKA, AALI, RATU, BBKP, HRUM, CMNT, SGRO, PSAB, JRPT, YUPI, STAA, STTP, GOOD, MCOL, WIFI, AUTO, TSPC, NICL, ALII, SHIP, MLBI, PACK, DEWA, CYBR, PRAY, POWR, ESSA, BMAS, MIDI, EDGE, BIPI, BSSR, SMSM, ADMF, ELPI, BFIN, HRTA, CLEO, BTPS, CMNP, CNMA, BANK, ADES, INPP, BJBR, SIMP, BJTM, PNLF, INET, SINI, TLDN, GMFI, NATO, BBMD, LSIP, TMAS, ABMM, DUTI, BHAT, DAAZ, SGER, DMND, CLAY, IBST, MTDL, BULL, ACES, LPKR, DMAS, SMRA, SSIA, ERAA, EPMT, SMDR, KRAS, JSPT, BOGA, MAYA, AGII, OMED, PALM, ANJT, TOBA, DATA, BESS, INDS, CASS, ELSA, AGRO, SAME, UANG, MNCN, LINK, BPII, YULE, TRIN, BALI, UDNG, PBSA, CTBN, DRMA, NIRO, DKFT, GTSI, MTLA, BBYB, TFCO, ROTI, FISH, TRIM, PYFA, TGKA, GOLF, KIJA, JTPE, MASB, HUMI, FORE, MPMX, RDTX, MSTI, BSWD, IMAS, BIRD, LPCK, ASSA, TUGU, BWPT, WIIM, RONY, LPPF, CENT, SDRA, SURE, VICI, MGLV, NOBU, KEEN, PSGO, AMAR, CPRO, CBRE, SOCI, ARNA, TBLA, STAR, GJTL, VICO, PBID, INPC, GGRP, IRSX, AGRS, HEXA, TOTL, UNIC, SMMT, BUKK, ROCK, SKRN, MDLA, MMLP, MINA, BACA, MAPB, KEJU, BGTG, SOTS, MBSS, SAMF, BHIT, ARGO, CBUT, PNIN, MARK, SMDM, ISSP, FPNI, APLN, MYOH, ASRI, SMIL, DAYA, KAEF, IFSH, BNBA, RALS, JAWA, MCOR, PKPK, HATM, TOTO, BCIC, IATA, MAHA, FOLK, SMBR, SFAN, BISI, BABP, FUTR, PSKT, OASA, ASLI, SSTM, SIPD, MGRO, PORT, DNAR, MKAP, BVIC, BOLT, PNGO, IPCC, BLTZ, ASGR, POLI, DWGL, BMTR, GMTD, WINS, IFII, MSJA, BCAP, OMRE, BEEF, KMTR, NICE, BKSW, PRDA, DOID, TRUE, BLUE, MDIA, WOOD, ACST, IMJS, AMAG, PTPP, MTMH, CSRA, MLIA, ITMA, DGWG, KETR, NRCA, DMMX, SCCO, INDR, PNBS, BRAM, LUCY, MBAP, TPMA, ELTY, IPTV, STRK, TEBE, ADHI, LPGI, SUNI, HILL, PSSI, MINE, FAST, DVLA, ERAL, HERO, KINO, CSAP, UCID, IPCM, MLPL, VISI, PTSN, BBRM, SPTO, FMII, PPRE, MAIN, AYAM, EURO, SKLT, DEPO, BSBK, MKTR, BMHS, NEST, PMJS, BEKS, KKGI, DLTA, AMFG, RAAM, TRGU, ALDO, GWSA, PSAT, GSMF, CARS, PADI, BBLD, DOOH, ABDA, BELL, NETV, MERK, BLOG, DILD, TAMU, CEKA, ATIC, TRST, SONA, BBSS, KBLI, BLES, CFIN, JKON, TIFA, CAMP, RANC, MITI, TCID, WSBP, GZCO, AISA, CITY, JIHD, LTLS, IBOS, ADCP, ARTA, BUAH, INDO, WOMF, BEST, PANS, TBMS, ENAK, RSCH, BLTA, JGLE, MTWI, ARII, BTEK, AREA, BOLA, SHID, ZINC, ASLC, PEVE, LIVE, MMIX, GHON, CHIP, WIRG, GDST, PBRX, GRIA, ATAP, CMPP, NELY, RMKO, NICK, SMGA, SPMA, RELI, HGII, BUDI, SKBM, COCO, LEAD, VOKS, PDPP, MHKI, NFCX, PTPW, PJAA, ZATA, NIKL, FUJI, AMOR, PANR, ADMG, MGNA, TALF, AMAN, BABY, MTFN, WTON, IPOL, SULI, PMUI, KSIX, PADA, LFLO, BPFI, JECC, FORU, HDFA, KOKA, BDKR, DGIK, WMUU, PGJO, RODA, KDSI, AXIO, TIRA, MDLN, MOLI, BEER, HOKI, BRNA, GTBO, BIKE, UNIQ, MPPA, APEX, AHAP, GTRA, SWID, IKBI, HOMI, HOPE, EKAD, VIVA, UNSP, PEGE, PZZA, SOFA, IRRA, ELIT, WEGE, SOSS, AWAN, SMKL, GLVA, TRIS, KOTA, GUNA, HAIS, UNTD, CHEK, LABS, BOAT, PNSE, MREI, FITT, KONI, VTNY, URBN, TRON, IDPR, WINE, DART, PJHB, GPRA, MDKI, KING, CNKO, UFOE, BSML, VERN, HALO, COAL, APLI, CRAB, ESTA, SURI, MDRN, MAXI, KMDS, CLPI, BAYU, VRNA, TIRT, IGAR, LAPD, IKPM, SCNP, MCAS, REAL, RIGS, CCSI, GDYR, GULA, NASA, PDES, CSIS, GOLD, PTPS, CBPE, SOLA, TYRE, ZONE, BIPP, BKDP, ESTI, IOTF, LPLI, VAST, HYGN, ASRM, KREN, SMLE, DYAN, DGNS, EAST, HAJJ, TFAS, SRSN, JATI, KBLM, DADA, BMSR, KOBX, NAIK, KBAG, TARA, SATU, ASPR, ASHA, YOII, UVCR, CRSN, YPAS, TRUS, ATLA, INTA, ERTX, GPSO, PART, MUTU, SAFE, KLAS, AKPI, ITIC, CGAS, EMDE, MICE, VINS, ASMI, HRME, BPTR, AMIN, ASPI, IKAI, BINO, SAGE, TOSK, BTON, OKAS, MPXL, WGSH, ACRO, AGAR, INOV, POLA, LMPI, FIRE, ANDI, PUDP, DOSS, FWCT, AKSI, CASH, KBLV, PRIM, NTBK, DEWI, OBAT, ASJT, ALKA, ECII, RELF, LCKM, PEHA, AKKU, ENZO, AYLS, INPS, BAJA, WINR, ASDM, SDPC, TRJA, SAPX, WAPO, PTMP, BAUT, MEJA, JMAS, LPPS, OBMD, NPGF, NZIA, MANG, LION, TAXI, PTSP, APII, CAKK, NANO, SLIS, DFAM, WOWS, SDMU, CINT, ZYRX, DKHH, MRAT, ABBA, BOBA, DIVA, PURA, MARI, PAMG, BAPI, CANI, KOPI, DSFI, SMKM, WEHA, PURI, LPIN, IBFN, RUIS, NAYZ, LAJU, TRUK, LAND, KARW, HELI, CHEM, SEMA, PSDN, IPAC, SNLK, INTD, MSKY, MBTO, KRYA, ASBI, INCI, TMPO, GEMA, ISAP, YELO, MERI, PTIS, ISEA, FOOD, LABA, MPIX, RGAS, DEFI, KUAS, SBMA, EPAC, RCCC, KIOS, INAI, RBMS, MIRA, NASI, MEDS, CSMI, CTTH, OLIV, JAST, IDEA, OPMS, PTDU, PGLI, FLMC, BCIP, INCF, HDIT, JAYA, AIMS, RUNS, POLY, OILS, BATA, KOIN, ICON, LRNA, MPOW, PICO, IKAN, TAYS, ESIP, KJEN, LUCK, TNCA, KICI, SOUL, ARKA, PLAN, BMBL, BAPA, RICY, WIDI, DIGI, INDX, HADE, TAMA, PCAR, LOPI, GRPH, HBAT, PIPA, KLIN, PPRI, AEGS, SPRE, KAQI, NINE, KOCI, LMAX, BRRC, RAFI, TOOL, BATR, AMMS, KKES, SICO, BAIK, GRPM, KDTN, MSIE"
input_saham = st.text_area("1️⃣ Masukkan Daftar Saham:", value=default_tickers)

# Tombol Search
if st.button("🚀 Ambil Data Mentah"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        # Ambil data dan simpan ke Session State agar tidak hilang saat filter digeser
        df_raw = get_fundamental_data(input_saham)
        if not df_raw.empty:
            st.session_state['data_saham'] = df_raw
            st.success(f"Berhasil mengambil data {len(df_raw)} saham! Silakan atur filter di bawah.")
        else:
            st.error("Data tidak ditemukan.")

# --- BAGIAN 2: TAMPILAN & FILTER (Hanya muncul jika data sudah ada) ---
if 'data_saham' in st.session_state:
    df = st.session_state['data_saham']
    
    st.divider()
    st.header("2️⃣ Atur Filter & Standar Kamu")
    
    # Hitung Statistik Sederhana untuk Referensi User
    # Agar user tau range datanya dari mana sampai mana
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        min_pe = df['P/E Ratio (x)'].min()
        max_pe = df['P/E Ratio (x)'].max()
        st.info(f"**Range P/E Data Ini:**\n{min_pe:.2f}x s/d {max_pe:.2f}x")
        
        # Input Filter P/E
        filter_pe = st.number_input("Max P/E yg diinginkan:", value=15.0, step=0.5)

    with col_stat2:
        min_roe = df['ROE (%)'].min()
        max_roe = df['ROE (%)'].max()
        st.info(f"**Range ROE Data Ini:**\n{min_roe:.2f}% s/d {max_roe:.2f}%")
        
        # Input Filter ROE
        filter_roe = st.number_input("Min ROE yg diinginkan:", value=10.0, step=0.5)

    with col_stat3:
        min_der = df['DER (%)'].min()
        max_der = df['DER (%)'].max()
        st.info(f"**Range DER Data Ini:**\n{min_der:.2f}% s/d {max_der:.2f}%")
        
        # Input Filter DER
        filter_der = st.number_input("Max DER yg diinginkan:", value=100.0, step=10.0)

    with col_stat4:
        min_ps = df['P/S Ratio (x)'].min()
        max_ps = df['P/S Ratio (x)'].max()
        st.info(f"**Range P/S Data Ini:**\n{min_ps:.2f}x s/d {max_ps:.2f}x")
        
        # Input Filter P/S
        filter_ps = st.number_input("Max P/S yg diinginkan:", value=2.0, step=0.1)

    # --- LOGIKA PEWARNAAN TABEL ---
    # Fungsi ini akan berjalan ulang setiap kali kamu ubah angka di atas
    def style_dataframe(row):
        styles = [''] * len(row)
        
        # Index Kolom (Sesuaikan jika urutan berubah)
        # 0:Kode, 1:Harga, 2:PE, 3:PS, 4:ROE, 5:DER, 6:EPS
        
        # Rule P/E (Kolom index 2) - Makin Rendah Bagus
        pe_val = row['P/E Ratio (x)']
        if pd.notna(pe_val):
            color = '#d4edda' if pe_val <= filter_pe else '#f8d7da' # Hijau jika <= Filter
            styles[2] = f'background-color: {color}; color: black'

        # Rule P/S (Kolom index 3) - Makin Rendah Bagus
        ps_val = row['P/S Ratio (x)']
        if pd.notna(ps_val):
            color = '#d4edda' if ps_val <= filter_ps else '#f8d7da'
            styles[3] = f'background-color: {color}; color: black'

        # Rule ROE (Kolom index 4) - Makin TINGGI Bagus
        roe_val = row['ROE (%)']
        if pd.notna(roe_val):
            color = '#d4edda' if roe_val >= filter_roe else '#f8d7da' # Hijau jika >= Filter
            styles[4] = f'background-color: {color}; color: black'

        # Rule DER (Kolom index 5) - Makin Rendah Bagus
        der_val = row['DER (%)']
        if pd.notna(der_val):
            color = '#d4edda' if der_val <= filter_der else '#f8d7da'
            styles[5] = f'background-color: {color}; color: black'

        return styles

    # Tampilkan Tabel
    st.subheader("📊 Hasil Screening")
    
    # Hitung Skor Kelulusan (Opsional: buat sorting)
    # Kita bikin kolom baru temporary untuk sorting, tapi gak ditampilkan
    df_display = df.copy()
    df_display['Score'] = (
        (df['P/E Ratio (x)'] <= filter_pe).astype(int) + 
        (df['ROE (%)'] >= filter_roe).astype(int) + 
        (df['DER (%)'] <= filter_der).astype(int) +
        (df['P/S Ratio (x)'] <= filter_ps).astype(int)
    )
    
    # Sort biar yang paling hijau ada di atas
    df_display = df_display.sort_values(by=['Score', 'ROE (%)'], ascending=[False, False])
    
    # Hapus kolom score biar tabel bersih (atau tampilkan kalau mau)
    df_final = df_display.drop(columns=['Score'])

    st.dataframe(
        df_final.style.apply(style_dataframe, axis=1)
                  .format("{:.2f}", subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']),
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    st.caption("Baris paling atas adalah yang paling banyak memenuhi kriteria kamu.")
