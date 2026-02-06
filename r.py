import streamlit as st
import yfinance as yf
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Konsistensi Top Gainer Fix", layout="wide")

# --- LIST SAHAM (Kompas100 + Populer) ---
TIKCER_LIST = [
   'BREN', 'BBCA', 'DSSA', 'BBRI', 'TPIA', 'DCII', 'BYAN', 'AMMN', 'BMRI', 'TLKM', 'ASII', 'MORA', 'SRAJ', 'CUAN', 'BRPT', 'BBNI', 'PANI', 'BNLI', 'BRMS', 'CDIA', 'DNET', 'IMPC', 'FILM', 'MPRO', 'BRIS', 'ICBP', 'HMSP', 'BUMI', 'EMAS', 'UNTR', 'ANTM', 'NCKL', 'SMMA', 'ADMR', 'CASA', 'UNVR', 'RISE', 'CPIN', 'MLPT', 'AMRT', 'MDKA', 'ISAT', 'MBMA', 'GOTO', 'INCO', 'AADI', 'INDF', 'PTRO', 'BELI', 'ADRO', 'EXCL', 'TCPI', 'KLBF', 'EMTK', 'MYOR', 'PGAS', 'INKP', 'PGUN', 'PGEO', 'GEMS', 'MTEL', 'BNGA', 'CMRY', 'ARCI', 'TBIG', 'MEGA', 'SILO', 'MEDC', 'GIAA', 'SOHO', 'VKTR', 'CBDK', 'MIKA', 'NISP', 'JPFA', 'GGRM', 'TOWR', 'BBHI', 'ENRG', 'TAPG', 'SUPA', 'BUVA', 'PTBA', 'BINA', 'COIN', 'AVIA', 'JSMR', 'AKRA', 'NSSS', 'PNBN', 'ITMG', 'BDMN', 'ARKO', 'MDIY', 'TINS', 'BSIM', 'INTP', 'JARR', 'BKSL', 'BTPN', 'ARTO', 'FAPA', 'MKPI', 'RMKE', 'SRTG', 'TKIM', 'MAPA', 'MSIN', 'MAPI', 'RLCO', 'HEAL', 'BSDE', 'KPIG', 'CITA', 'PWON', 'BNBR', 'APIC', 'BBTN', 'SMGR', 'RAJA', 'POLU', 'LIFE', 'BNII', 'INDY', 'CTRA', 'SMAR', 'SCMA', 'SSMS', 'CARE', 'ULTJ', 'SIDO', 'DSNG', 'BBSI', 'BUKA', 'AALI', 'RATU', 'BBKP', 'HRUM', 'CMNT', 'SGRO', 'PSAB', 'JRPT', 'YUPI', 'STAA', 'STTP', 'GOOD', 'MCOL', 'WIFI', 'AUTO', 'TSPC', 'NICL', 'ALII', 'SHIP', 'MLBI', 'PACK', 'DEWA', 'CYBR', 'PRAY', 'POWR', 'ESSA', 'BMAS', 'MIDI', 'EDGE', 'BIPI', 'BSSR', 'SMSM', 'ADMF', 'ELPI', 'BFIN', 'HRTA', 'CLEO', 'BTPS', 'CMNP', 'CNMA', 'BANK', 'ADES', 'INPP', 'BJBR', 'SIMP', 'BJTM', 'PNLF', 'INET', 'SINI', 'TLDN', 'GMFI', 'NATO', 'BBMD', 'LSIP', 'TMAS', 'ABMM', 'DUTI', 'BHAT', 'DAAZ', 'SGER', 'DMND', 'CLAY', 'IBST', 'MTDL', 'BULL', 'ACES', 'LPKR', 'DMAS', 'SMRA', 'SSIA', 'ERAA', 'EPMT', 'SMDR', 'KRAS', 'JSPT', 'BOGA', 'MAYA', 'AGII', 'OMED', 'PALM', 'ANJT', 'TOBA', 'DATA', 'BESS', 'INDS', 'CASS', 'ELSA', 'AGRO', 'SAME', 'UANG', 'MNCN', 'LINK', 'BPII', 'YULE', 'TRIN', 'BALI', 'UDNG', 'PBSA', 'CTBN', 'DRMA', 'NIRO', 'DKFT', 'GTSI', 'MTLA', 'BBYB', 'TFCO', 'ROTI', 'FISH', 'TRIM', 'PYFA', 'TGKA', 'GOLF', 'KIJA', 'JTPE', 'MASB', 'HUMI', 'FORE', 'MPMX', 'RDTX', 'MSTI', 'BSWD', 'IMAS', 'BIRD', 'LPCK', 'ASSA', 'TUGU', 'BWPT', 'WIIM', 'RONY', 'LPPF', 'CENT', 'SDRA', 'SURE', 'VICI', 'MGLV', 'NOBU', 'KEEN', 'PSGO', 'AMAR', 'CPRO', 'CBRE', 'SOCI', 'ARNA', 'TBLA', 'STAR', 'GJTL', 'VICO', 'PBID', 'INPC', 'GGRP', 'IRSX', 'AGRS', 'HEXA', 'TOTL', 'UNIC', 'SMMT', 'BUKK', 'ROCK', 'SKRN', 'MDLA', 'MMLP', 'MINA', 'BACA', 'MAPB', 'KEJU', 'BGTG', 'SOTS', 'MBSS', 'SAMF', 'BHIT', 'ARGO', 'CBUT', 'PNIN', 'MARK', 'SMDM', 'ISSP', 'FPNI', 'APLN', 'MYOH', 'ASRI', 'SMIL', 'DAYA', 'KAEF', 'IFSH', 'BNBA', 'RALS', 'JAWA', 'MCOR', 'PKPK', 'HATM', 'TOTO', 'BCIC', 'IATA', 'MAHA', 'FOLK', 'SMBR', 'SFAN', 'BISI', 'BABP', 'FUTR', 'PSKT', 'OASA', 'ASLI', 'SSTM', 'SIPD', 'MGRO', 'PORT', 'DNAR', 'MKAP', 'BVIC', 'BOLT', 'PNGO', 'IPCC', 'BLTZ', 'ASGR', 'POLI', 'DWGL', 'BMTR', 'GMTD', 'WINS', 'IFII', 'MSJA', 'BCAP', 'OMRE', 'BEEF', 'KMTR', 'NICE', 'BKSW', 'PRDA', 'DOID', 'TRUE', 'BLUE', 'MDIA', 'WOOD', 'ACST', 'IMJS', 'AMAG', 'PTPP', 'MTMH', 'CSRA', 'MLIA', 'ITMA', 'DGWG', 'KETR', 'NRCA', 'DMMX', 'SCCO', 'INDR', 'PNBS', 'BRAM', 'LUCY', 'MBAP', 'TPMA', 'ELTY', 'IPTV', 'STRK', 'TEBE', 'ADHI', 'LPGI', 'SUNI', 'HILL', 'PSSI', 'MINE', 'FAST', 'DVLA', 'ERAL', 'HERO', 'KINO', 'CSAP', 'UCID', 'IPCM', 'MLPL', 'VISI', 'PTSN', 'BBRM', 'SPTO', 'FMII', 'PPRE', 'MAIN', 'AYAM', 'EURO', 'SKLT', 'DEPO', 'BSBK', 'MKTR', 'BMHS', 'NEST', 'PMJS', 'BEKS', 'KKGI', 'DLTA', 'AMFG', 'RAAM', 'TRGU', 'ALDO', 'GWSA', 'PSAT', 'GSMF', 'CARS', 'PADI', 'BBLD', 'DOOH', 'ABDA', 'BELL', 'NETV', 'MERK', 'BLOG', 'DILD', 'TAMU', 'CEKA', 'ATIC', 'TRST', 'SONA', 'BBSS', 'KBLI', 'BLES', 'CFIN', 'JKON', 'TIFA', 'CAMP', 'RANC', 'MITI', 'TCID', 'WSBP', 'GZCO', 'AISA', 'CITY', 'JIHD', 'LTLS', 'IBOS', 'ADCP', 'ARTA', 'BUAH', 'INDO', 'WOMF', 'BEST', 'PANS', 'TBMS', 'ENAK', 'RSCH', 'BLTA', 'JGLE', 'MTWI', 'ARII', 'BTEK', 'AREA', 'BOLA', 'SHID', 'ZINC', 'ASLC', 'PEVE', 'LIVE', 'MMIX', 'GHON', 'CHIP', 'WIRG', 'GDST', 'PBRX', 'GRIA', 'ATAP', 'CMPP', 'NELY', 'RMKO', 'NICK', 'SMGA', 'SPMA', 'RELI', 'HGII', 'BUDI', 'SKBM', 'COCO', 'LEAD', 'VOKS', 'PDPP', 'MHKI', 'NFCX', 'PTPW', 'PJAA', 'ZATA', 'NIKL', 'FUJI', 'AMOR', 'PANR', 'ADMG', 'MGNA', 'TALF', 'AMAN', 'BABY', 'MTFN', 'WTON', 'IPOL', 'SULI', 'PMUI', 'KSIX', 'PADA', 'LFLO', 'BPFI', 'JECC', 'FORU', 'HDFA', 'KOKA', 'BDKR', 'DGIK', 'WMUU', 'PGJO', 'RODA', 'KDSI', 'AXIO', 'TIRA', 'MDLN', 'MOLI', 'BEER', 'HOKI', 'BRNA', 'GTBO', 'BIKE', 'UNIQ', 'MPPA', 'APEX', 'AHAP', 'GTRA', 'SWID', 'IKBI', 'HOMI', 'HOPE', 'EKAD', 'VIVA', 'UNSP', 'PEGE', 'PZZA', 'SOFA', 'IRRA', 'ELIT', 'WEGE', 'SOSS', 'AWAN', 'SMKL', 'GLVA', 'TRIS', 'KOTA', 'GUNA', 'HAIS', 'UNTD', 'CHEK', 'LABS', 'BOAT', 'PNSE', 'MREI', 'FITT', 'KONI', 'VTNY', 'URBN', 'TRON', 'IDPR', 'WINE', 'DART', 'PJHB', 'GPRA', 'MDKI', 'KING', 'CNKO', 'UFOE', 'BSML', 'VERN', 'HALO', 'COAL', 'APLI', 'CRAB', 'ESTA', 'SURI', 'MDRN', 'MAXI', 'KMDS', 'CLPI', 'BAYU', 'VRNA', 'TIRT', 'IGAR', 'LAPD', 'IKPM', 'SCNP', 'MCAS', 'REAL', 'RIGS', 'CCSI', 'GDYR', 'GULA', 'NASA', 'PDES', 'CSIS', 'GOLD', 'PTPS', 'CBPE', 'SOLA', 'TYRE', 'ZONE', 'BIPP', 'BKDP', 'ESTI', 'IOTF', 'LPLI', 'VAST', 'HYGN', 'ASRM', 'KREN', 'SMLE', 'DYAN', 'DGNS', 'EAST', 'HAJJ', 'TFAS', 'SRSN', 'JATI', 'KBLM', 'DADA', 'BMSR', 'KOBX', 'NAIK', 'KBAG', 'TARA', 'SATU', 'ASPR', 'ASHA', 'YOII', 'UVCR', 'CRSN', 'YPAS', 'TRUS', 'ATLA', 'INTA', 'ERTX', 'GPSO', 'PART', 'MUTU', 'SAFE', 'KLAS', 'AKPI', 'ITIC', 'CGAS', 'EMDE', 'MICE', 'VINS', 'ASMI', 'HRME', 'BPTR', 'AMIN', 'ASPI', 'IKAI', 'BINO', 'SAGE', 'TOSK', 'BTON', 'OKAS', 'MPXL', 'WGSH', 'ACRO', 'AGAR', 'INOV', 'POLA', 'LMPI', 'FIRE', 'ANDI', 'PUDP', 'DOSS', 'FWCT', 'AKSI', 'CASH', 'KBLV', 'PRIM', 'NTBK', 'DEWI', 'OBAT', 'ASJT', 'ALKA', 'ECII', 'RELF', 'LCKM', 'PEHA', 'AKKU', 'ENZO', 'AYLS', 'INPS', 'BAJA', 'WINR', 'ASDM', 'SDPC', 'TRJA', 'SAPX', 'WAPO', 'PTMP', 'BAUT', 'MEJA', 'JMAS', 'LPPS', 'OBMD', 'NPGF', 'NZIA', 'MANG', 'LION', 'TAXI', 'PTSP', 'APII', 'CAKK', 'NANO', 'SLIS', 'DFAM', 'WOWS', 'SDMU', 'CINT', 'ZYRX', 'DKHH', 'MRAT', 'ABBA', 'BOBA', 'DIVA', 'PURA', 'MARI', 'PAMG', 'BAPI', 'CANI', 'KOPI', 'DSFI', 'SMKM', 'WEHA', 'PURI', 'LPIN', 'IBFN', 'RUIS', 'NAYZ', 'LAJU', 'TRUK', 'LAND', 'KARW', 'HELI', 'CHEM', 'SEMA', 'PSDN', 'IPAC', 'SNLK', 'INTD', 'MSKY', 'MBTO', 'KRYA', 'ASBI', 'INCI', 'TMPO', 'GEMA', 'ISAP', 'YELO', 'MERI', 'PTIS', 'ISEA', 'FOOD', 'LABA', 'MPIX', 'RGAS', 'DEFI', 'KUAS', 'SBMA', 'EPAC', 'RCCC', 'KIOS', 'INAI', 'RBMS', 'MIRA', 'NASI', 'MEDS', 'CSMI', 'CTTH', 'OLIV', 'JAST', 'IDEA', 'OPMS', 'PTDU', 'PGLI', 'FLMC', 'BCIP', 'INCF', 'HDIT', 'JAYA', 'AIMS', 'RUNS', 'POLY', 'OILS', 'BATA', 'KOIN', 'ICON', 'LRNA', 'MPOW', 'PICO', 'IKAN', 'TAYS', 'ESIP', 'KJEN', 'LUCK', 'TNCA', 'KICI', 'SOUL', 'ARKA', 'PLAN', 'BMBL', 'BAPA', 'RICY', 'WIDI', 'DIGI', 'INDX', 'HADE', 'TAMA', 'PCAR', 'LOPI', 'GRPH', 'HBAT', 'PIPA', 'KLIN', 'PPRI', 'AEGS', 'SPRE', 'KAQI', 'NINE', 'KOCI', 'LMAX', 'BRRC', 'RAFI', 'TOOL', 'BATR', 'AMMS', 'KKES', 'SICO', 'BAIK', 'GRPM', 'KDTN', 'MSIE'
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
