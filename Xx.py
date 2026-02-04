import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Top 100 IHSG Chart")
st.title("📈 Top IHSG Chart Generator (Pagination Mode)")

# --- 1. DAFTAR SAHAM (Raw List) ---
raw_tickers = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# PERBAIKAN 1: Tambahkan .JK otomatis
tickers = [t + ".JK" for t in raw_tickers]

# --- 2. KONFIGURASI ---
PERIOD = "3mo"
MA_WINDOW = 20
STOCKS_PER_PAGE = 24  # Tampilkan 24 saham per halaman agar cepat (6 baris x 4 kolom)
COLS = 4

# --- 3. PAGINATION (SISTEM HALAMAN) ---
total_stocks = len(tickers)
total_pages = math.ceil(total_stocks / STOCKS_PER_PAGE)

# Widget Pilih Halaman
page = st.number_input('Pilih Halaman', min_value=1, max_value=total_pages, value=1)
start_idx = (page - 1) * STOCKS_PER_PAGE
end_idx = start_idx + STOCKS_PER_PAGE

# Ambil saham hanya untuk halaman ini
current_batch = tickers[start_idx:end_idx]

st.write(f"Menampilkan saham {start_idx+1} sampai {min(end_idx, total_stocks)} dari {total_stocks}")

# --- 4. DOWNLOAD DATA (BATCH) ---
# PERBAIKAN 2: Download sekaligus untuk batch ini saja, jauh lebih cepat daripada loop
if current_batch:
    with st.spinner("Sedang mengambil data..."):
        try:
            # group_by='ticker' penting agar struktur data rapi
            data = yf.download(current_batch, period=PERIOD, group_by='ticker', threads=True)
        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")
            data = pd.DataFrame()

    # --- 5. PLOTTING ---
    if not data.empty:
        rows_needed = math.ceil(len(current_batch) / COLS)
        fig, axes = plt.subplots(rows_needed, COLS, figsize=(20, 4 * rows_needed))
        
        # Jika cuma 1 baris, axes bukan array 2D, perlu diratakan
        if rows_needed == 1:
            axes = [axes] if COLS == 1 else axes
        else:
            axes = axes.flatten()

        for i, ticker in enumerate(current_batch):
            ax = axes[i]
            
            try:
                # PERBAIKAN 3: Handling MultiIndex Dataframe
                # Data yf.download batch formatnya: data[Ticker][Close]
                df_stock = data[ticker]
                
                # Cek jika data kosong
                if df_stock.empty or df_stock['Close'].isnull().all():
                    ax.text(0.5, 0.5, "No Data", ha='center', va='center')
                    ax.set_title(ticker, fontsize=10, fontweight='bold')
                    continue

                close = df_stock['Close']
                ma20 = close.rolling(window=MA_WINDOW).mean()

                ax.plot(close.index, close, color='black', linewidth=1, label='Price')
                ax.plot(close.index, ma20, color='orange', linewidth=1, label='MA20')

                ax.set_title(ticker, fontsize=10, fontweight='bold')
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # Hapus label X axis biar rapi kecuali baris terbawah
                if i < len(current_batch) - COLS:
                    ax.set_xticklabels([])
                else:
                    ax.tick_params(axis='x', rotation=45, labelsize=8)

            except Exception as e:
                ax.text(0.5, 0.5, "Error", ha='center', va='center')
                ax.set_title(ticker)

        # Hapus axes kosong jika ada sisa di grid terakhir
        for j in range(len(current_batch), len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error("Data tidak ditemukan atau koneksi bermasalah.")
