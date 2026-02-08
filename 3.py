import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Custom Stock Screener", layout="wide")

st.title("🎯 Dashboard Screening Fundamental (Kriteria Sendiri)")
st.markdown("Masukkan standar angka yang kamu mau (ketik manual), sistem akan mencari saham yang lolos kriteria tersebut.")

# --- SIDEBAR: INPUT KRITERIA (ANGKA MANUAL) ---
st.sidebar.header("⚙️ Tentukan Standar Kamu")
st.sidebar.caption("Ketik angka batas yang kamu inginkan.")

# 1. Target P/E Ratio (Maksimal)
target_pe = st.sidebar.number_input(
    "Maksimal P/E Ratio (x)", 
    min_value=0.0, max_value=100.0, value=15.0, step=0.1,
    help="Saham dianggap murah jika P/E di bawah angka ini."
)

# 2. Target P/S Ratio (Maksimal)
target_ps = st.sidebar.number_input(
    "Maksimal P/S Ratio (x)", 
    min_value=0.0, max_value=50.0, value=2.0, step=0.1,
    help="Saham dianggap murah jika P/S di bawah angka ini."
)

# 3. Target ROE (Minimal)
target_roe = st.sidebar.number_input(
    "Minimal ROE (%)", 
    min_value=0.0, max_value=100.0, value=10.0, step=0.5,
    help="Perusahaan dianggap profitabel jika ROE di atas angka ini."
)

# 4. Target DER (Maksimal)
target_der = st.sidebar.number_input(
    "Maksimal DER / Utang (%)", 
    min_value=0.0, max_value=500.0, value=100.0, step=10.0,
    help="Perusahaan dianggap aman jika Utang di bawah angka ini."
)

# --- FUNGSI AMBIL DATA ---
def get_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Sedang mengambil data...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Cek {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Ambil data (Handle jika kosong)
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            price = info.get('currentPrice')
            
            # Konversi ROE ke Persen
            if roe is not None: roe = roe * 100

            # Hitung Skor Kelulusan (Berapa kriteria yang lolos?)
            score = 0
            status_pe = "❌"
            status_roe = "❌"
            
            # Cek P/E
            if pe and pe <= target_pe: 
                score += 1
                status_pe = "✅"
                
            # Cek P/S
            if ps and ps <= target_ps: 
                score += 1
                
            # Cek ROE
            if roe and roe >= target_roe: 
                score += 1
                status_roe = "✅"
                
            # Cek DER
            if der and der <= target_der: 
                score += 1

            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': price,
                'Skor (Max 4)': score, # Total kriteria yang terpenuhi
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except:
            continue
            
    progress_bar.empty()
    return pd.DataFrame(data)

# --- UI UTAMA ---
default_tickers = "BREN, BBCA, DSSA, BBRI, TPIA, DCII, BYAN, AMMN, BMRI, TLKM, ASII, MORA, SRAJ, CUAN, BRPT, BBNI, PANI, BNLI, BRMS, CDIA, DNET, IMPC, FILM, MPRO, BRIS, ICBP, HMSP, BUMI, EMAS, UNTR, ANTM, NCKL, SMMA, ADMR, CASA, UNVR, RISE, CPIN, MLPT, AMRT, MDKA, ISAT, MBMA, GOTO, INCO, AADI, INDF, PTRO, BELI, ADRO, EXCL, TCPI, KLBF, EMTK, MYOR, PGAS, INKP, PGUN, PGEO, GEMS, MTEL, BNGA, CMRY, ARCI, TBIG, MEGA, SILO, MEDC, GIAA, SOHO, VKTR, CBDK, MIKA, NISP, JPFA, GGRM, TOWR, BBHI, ENRG, TAPG, SUPA, BUVA, PTBA, BINA, COIN, AVIA, JSMR, AKRA, NSSS, PNBN, ITMG, BDMN, ARKO, MDIY, TINS, BSIM, INTP, JARR, BKSL, BTPN, ARTO, FAPA, MKPI, RMKE, SRTG, TKIM, MAPA, MSIN, MAPI, RLCO, HEAL, BSDE, KPIG, CITA, PWON, BNBR, APIC, BBTN, SMGR, RAJA, POLU, LIFE, BNII, INDY, CTRA, SMAR, SCMA, SSMS, CARE, ULTJ, SIDO, DSNG, BBSI, BUKA, AALI, RATU, BBKP, HRUM, CMNT, SGRO, PSAB, JRPT, YUPI, STAA, STTP, GOOD, MCOL, WIFI, AUTO, TSPC, NICL, ALII, SHIP, MLBI, PACK, DEWA, CYBR, PRAY, POWR, ESSA, BMAS, MIDI, EDGE, BIPI, BSSR, SMSM, ADMF, ELPI, BFIN, HRTA, CLEO, BTPS, CMNP, CNMA, BANK, ADES, INPP, BJBR, SIMP, BJTM, PNLF, INET, SINI, TLDN, GMFI, NATO, BBMD, LSIP, TMAS, ABMM, DUTI, BHAT, DAAZ, SGER, DMND, CLAY, IBST, MTDL, BULL, ACES, LPKR, DMAS, SMRA, SSIA, ERAA, EPMT, SMDR, KRAS, JSPT, BOGA, MAYA, AGII, OMED, PALM, ANJT, TOBA, DATA, BESS, INDS, CASS, ELSA, AGRO, SAME, UANG, MNCN, LINK, BPII, YULE, TRIN, BALI, UDNG, PBSA, CTBN, DRMA, NIRO, DKFT, GTSI, MTLA, BBYB, TFCO, ROTI, FISH, TRIM, PYFA, TGKA, GOLF, KIJA, JTPE, MASB, HUMI, FORE, MPMX, RDTX, MSTI, BSWD, IMAS, BIRD, LPCK, ASSA, TUGU, BWPT, WIIM, RONY, LPPF, CENT, SDRA, SURE, VICI, MGLV, NOBU, KEEN, PSGO, AMAR, CPRO, CBRE, SOCI, ARNA, TBLA, STAR, GJTL, VICO, PBID, INPC, GGRP, IRSX, AGRS, HEXA, TOTL, UNIC, SMMT, BUKK, ROCK, SKRN, MDLA, MMLP, MINA, BACA, MAPB, KEJU, BGTG, SOTS, MBSS, SAMF, BHIT, ARGO, CBUT, PNIN, MARK, SMDM, ISSP, FPNI, APLN, MYOH, ASRI, SMIL, DAYA, KAEF, IFSH, BNBA, RALS, JAWA, MCOR, PKPK, HATM, TOTO, BCIC, IATA, MAHA, FOLK, SMBR, SFAN, BISI, BABP, FUTR, PSKT, OASA, ASLI, SSTM, SIPD, MGRO, PORT, DNAR, MKAP, BVIC, BOLT, PNGO, IPCC, BLTZ, ASGR, POLI, DWGL, BMTR, GMTD, WINS, IFII, MSJA, BCAP, OMRE, BEEF, KMTR, NICE, BKSW, PRDA, DOID, TRUE, BLUE, MDIA, WOOD, ACST, IMJS, AMAG, PTPP, MTMH, CSRA, MLIA, ITMA, DGWG, KETR, NRCA, DMMX, SCCO, INDR, PNBS, BRAM, LUCY, MBAP, TPMA, ELTY, IPTV, STRK, TEBE, ADHI, LPGI, SUNI, HILL, PSSI, MINE, FAST, DVLA, ERAL, HERO, KINO, CSAP, UCID, IPCM, MLPL, VISI, PTSN, BBRM, SPTO, FMII, PPRE, MAIN, AYAM, EURO, SKLT, DEPO, BSBK, MKTR, BMHS, NEST, PMJS, BEKS, KKGI, DLTA, AMFG, RAAM, TRGU, ALDO, GWSA, PSAT, GSMF, CARS, PADI, BBLD, DOOH, ABDA, BELL, NETV, MERK, BLOG, DILD, TAMU, CEKA, ATIC, TRST, SONA, BBSS, KBLI, BLES, CFIN, JKON, TIFA, CAMP, RANC, MITI, TCID, WSBP, GZCO, AISA, CITY, JIHD, LTLS, IBOS, ADCP, ARTA, BUAH, INDO, WOMF, BEST, PANS, TBMS, ENAK, RSCH, BLTA, JGLE, MTWI, ARII, BTEK, AREA, BOLA, SHID, ZINC, ASLC, PEVE, LIVE, MMIX, GHON, CHIP, WIRG, GDST, PBRX, GRIA, ATAP, CMPP, NELY, RMKO, NICK, SMGA, SPMA, RELI, HGII, BUDI, SKBM, COCO, LEAD, VOKS, PDPP, MHKI, NFCX, PTPW, PJAA, ZATA, NIKL, FUJI, AMOR, PANR, ADMG, MGNA, TALF, AMAN, BABY, MTFN, WTON, IPOL, SULI, PMUI, KSIX, PADA, LFLO, BPFI, JECC, FORU, HDFA, KOKA, BDKR, DGIK, WMUU, PGJO, RODA, KDSI, AXIO, TIRA, MDLN, MOLI, BEER, HOKI, BRNA, GTBO, BIKE, UNIQ, MPPA, APEX, AHAP, GTRA, SWID, IKBI, HOMI, HOPE, EKAD, VIVA, UNSP, PEGE, PZZA, SOFA, IRRA, ELIT, WEGE, SOSS, AWAN, SMKL, GLVA, TRIS, KOTA, GUNA, HAIS, UNTD, CHEK, LABS, BOAT, PNSE, MREI, FITT, KONI, VTNY, URBN, TRON, IDPR, WINE, DART, PJHB, GPRA, MDKI, KING, CNKO, UFOE, BSML, VERN, HALO, COAL, APLI, CRAB, ESTA, SURI, MDRN, MAXI, KMDS, CLPI, BAYU, VRNA, TIRT, IGAR, LAPD, IKPM, SCNP, MCAS, REAL, RIGS, CCSI, GDYR, GULA, NASA, PDES, CSIS, GOLD, PTPS, CBPE, SOLA, TYRE, ZONE, BIPP, BKDP, ESTI, IOTF, LPLI, VAST, HYGN, ASRM, KREN, SMLE, DYAN, DGNS, EAST, HAJJ, TFAS, SRSN, JATI, KBLM, DADA, BMSR, KOBX, NAIK, KBAG, TARA, SATU, ASPR, ASHA, YOII, UVCR, CRSN, YPAS, TRUS, ATLA, INTA, ERTX, GPSO, PART, MUTU, SAFE, KLAS, AKPI, ITIC, CGAS, EMDE, MICE, VINS, ASMI, HRME, BPTR, AMIN, ASPI, IKAI, BINO, SAGE, TOSK, BTON, OKAS, MPXL, WGSH, ACRO, AGAR, INOV, POLA, LMPI, FIRE, ANDI, PUDP, DOSS, FWCT, AKSI, CASH, KBLV, PRIM, NTBK, DEWI, OBAT, ASJT, ALKA, ECII, RELF, LCKM, PEHA, AKKU, ENZO, AYLS, INPS, BAJA, WINR, ASDM, SDPC, TRJA, SAPX, WAPO, PTMP, BAUT, MEJA, JMAS, LPPS, OBMD, NPGF, NZIA, MANG, LION, TAXI, PTSP, APII, CAKK, NANO, SLIS, DFAM, WOWS, SDMU, CINT, ZYRX, DKHH, MRAT, ABBA, BOBA, DIVA, PURA, MARI, PAMG, BAPI, CANI, KOPI, DSFI, SMKM, WEHA, PURI, LPIN, IBFN, RUIS, NAYZ, LAJU, TRUK, LAND, KARW, HELI, CHEM, SEMA, PSDN, IPAC, SNLK, INTD, MSKY, MBTO, KRYA, ASBI, INCI, TMPO, GEMA, ISAP, YELO, MERI, PTIS, ISEA, FOOD, LABA, MPIX, RGAS, DEFI, KUAS, SBMA, EPAC, RCCC, KIOS, INAI, RBMS, MIRA, NASI, MEDS, CSMI, CTTH, OLIV, JAST, IDEA, OPMS, PTDU, PGLI, FLMC, BCIP, INCF, HDIT, JAYA, AIMS, RUNS, POLY, OILS, BATA, KOIN, ICON, LRNA, MPOW, PICO, IKAN, TAYS, ESIP, KJEN, LUCK, TNCA, KICI, SOUL, ARKA, PLAN, BMBL, BAPA, RICY, WIDI, DIGI, INDX, HADE, TAMA, PCAR, LOPI, GRPH, HBAT, PIPA, KLIN, PPRI, AEGS, SPRE, KAQI, NINE, KOCI, LMAX, BRRC, RAFI, TOOL, BATR, AMMS, KKES, SICO, BAIK, GRPM, KDTN, MSIE"
input_saham = st.text_area("Masukkan Kode Saham:", value=default_tickers)

if st.button("🔍 Cek Kriteria Saya"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        df = get_data(input_saham)
        
        if not df.empty:
            # Urutkan berdasarkan SKOR TERTINGGI (Paling sesuai kriteria kamu)
            df = df.sort_values(by=['Skor (Max 4)', 'ROE (%)'], ascending=[False, False])
            
            st.success(f"Berhasil menganalisa {len(df)} saham berdasarkan kriteria kamu.")
            
            # --- 1. TAMPILAN SCORE CARD ---
            st.subheader("🏆 Saham Paling Lolos Kriteria")
            st.caption(f"Kriteria Kamu: P/E < {target_pe}, ROE > {target_roe}%, DER < {target_der}%, P/S < {target_ps}")
            
            # Highlight Warna Warni berdasarkan Kriteria User
            def highlight_custom_rules(row):
                styles = [''] * len(row)
                
                # Index kolom di DataFrame (sesuaikan manual atau pakai nama kolom)
                # Kita pakai logika sederhana: Buat styler function terpisah per kolom
                return styles

            # Konfigurasi Kolom
            column_config = {
                "Kode": st.column_config.TextColumn("Ticker", width="small"),
                "Skor (Max 4)": st.column_config.ProgressColumn(
                    "Kecocokan", 
                    format="%d/4", 
                    min_value=0, 
                    max_value=4,
                    help="Berapa banyak kriteria kamu yang terpenuhi?"
                ),
                "P/E Ratio (x)": st.column_config.NumberColumn("P/E", format="%.2fx"),
                "P/S Ratio (x)": st.column_config.NumberColumn("P/S", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "DER (%)": st.column_config.NumberColumn("DER", format="%.2f%%"),
            }

            # --- LOGIC WARNA BARIS ---
            # Kita warnai background cell Hijau jika lolos kriteria user, Merah jika gagal
            
            def color_pe(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_pe else 'background-color: #f8d7da; color: black'

            def color_ps(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_ps else 'background-color: #f8d7da; color: black'

            def color_roe(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val >= target_roe else 'background-color: #f8d7da; color: black'

            def color_der(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_der else 'background-color: #f8d7da; color: black'

            # Apply Style
            styled_df = df.style.applymap(color_pe, subset=['P/E Ratio (x)']) \
                                .applymap(color_ps, subset=['P/S Ratio (x)']) \
                                .applymap(color_roe, subset=['ROE (%)']) \
                                .applymap(color_der, subset=['DER (%)']) \
                                .format("{:.2f}", subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)'])

            st.dataframe(
                styled_df,
                column_config=column_config,
                use_container_width=True,
                height=600,
                hide_index=True
            )
            
            # Penjelasan Warna
            st.info("""
            **Cara Baca Tabel:**
            * 🟩 **Hijau:** Angka masuk dalam kriteria yang kamu ketik di sidebar.
            * 🟥 **Merah:** Angka tidak lolos kriteria kamu.
            * **Skor 4/4:** Artinya saham ini sempurna sesuai keinginanmu.
            """)
            
        else:
            st.error("Data tidak ditemukan.")
