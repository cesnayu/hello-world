import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os
import pytz 

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

DB_FILE = "stock_database.json"

# List Saham Lengkap (Sesuai permintaan user)
LIST_SAHAM_FULL = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# --- 2. FUNGSI DATABASE (JSON) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "picked_stocks": st.session_state.get("picked_stocks", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 3. INISIALISASI SESSION STATE ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]
if 'picked_stocks' not in st.session_state:
    st.session_state.picked_stocks = saved_data["picked_stocks"] if (saved_data and "picked_stocks" in saved_data) else []

# Variabel Waktu Global untuk Dashboard
today = datetime.now()
end_date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d") # Untuk yfinance end date

# --- 4. FUNGSI LOGIKA (BACKEND) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo", interval="1d"):
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=False)
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def get_weekly_recap_data(tickers):
    start_of_week = today - timedelta(days=today.weekday())
    days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_date = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
    
    data = yf.download(tickers, start=start_date, group_by="ticker", progress=False)
    
    all_rows = []
    for t in tickers:
        try:
            df = data[t].dropna().copy() if len(tickers) > 1 else data.dropna().copy()
            if df.empty: continue
            
            df["Return"] = df["Close"].pct_change() * 100
            df.index = df.index.date
            
            row = {"Ticker": t, "Price": round(df["Close"].iloc[-1], 0), "Today (%)": round(df["Return"].iloc[-1], 2)}
            
            weekly_vals = []
            gain_count = 0
            for i in range(5):
                target = (start_of_week + timedelta(days=i)).date()
                if target in df.index:
                    val = df.loc[target, "Return"]
                    if isinstance(val, pd.Series): val = val.iloc[0]
                    row[days_names[i]] = round(val, 2)
                    weekly_vals.append(val)
                    if val > 0: gain_count += 1
                else: row[days_names[i]] = 0.0
            
            row["Weekly Acc (%)"] = round(sum(weekly_vals), 2)
            row["Win Rate"] = f"{gain_count}/5"
            all_rows.append(row)
        except: continue
    return pd.DataFrame(all_rows)

@st.cache_data(ttl=600)
def get_win_loss_details(raw_input):
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = [t.strip().upper() for t in clean_input.split(',') if t.strip()]
    tickers = [t + ".JK" if not t.endswith(".JK") else t for t in tickers]
    data = yf.download(tickers, period="3mo", group_by='ticker', progress=False)
    
    summary = []
    details = {}
    for t in tickers:
        try:
            df = data[t].dropna().copy() if len(tickers) > 1 else data.dropna().copy()
            df['Change'] = df['Close'].pct_change() * 100
            df_30 = df.tail(30).dropna()
            
            green = df_30[df_30['Change'] > 0]
            red = df_30[df_30['Change'] < 0]
            
            summary.append({
                "Ticker": t, "Win Rate": f"{(len(green)/len(df_30))*100:.1f}%",
                "Avg Gain": round(green['Change'].mean(), 2), "Avg Loss": round(red['Change'].mean(), 2),
                "Total Return": round(((df_30['Close'].iloc[-1]-df_30['Close'].iloc[0])/df_30['Close'].iloc[0])*100, 2)
            })
            details[t] = df_30[['Change']]
        except: continue
    return pd.DataFrame(summary), details

# --- 5. MAIN UI ---
st.title("📈 Super Stock Dashboard")

tabs = st.tabs(["📅 Weekly Recap", "📊 Grid Overview", "⚖️ Bandingkan", "🎲 Win/Loss", "🎯 Simulator"])

# === TAB 1: WEEKLY RECAP ===
with tabs[0]:
    st.header("📅 Weekly Performance Overview")
    with st.spinner("Fetching weekly market data..."):
        df_weekly = get_weekly_recap_data(LIST_SAHAM_FULL)
        if not df_weekly.empty:
            def color_returns(val):
                if isinstance(val, (int, float)):
                    color = '#00ff00' if val > 0 else '#ff4b4b' if val < 0 else 'white'
                    return f'color: {color}'
                return ''

            st.dataframe(
                df_weekly.style.applymap(color_returns, subset=['Today (%)', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Weekly Acc (%)']),
                use_container_width=True, hide_index=True
            )

    st.divider()
    # FITUR BARU: Chart Explorer (Memperbaiki NameError)
    st.subheader("📈 Stock Price Chart Explorer")
    selected_stocks = st.multiselect("Pilih Saham untuk Grafik:", options=LIST_SAHAM_FULL, placeholder="Ketik kode saham...")
    
    if selected_stocks:
        chart_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        # Menggunakan end_date_str yang sudah didefinisikan di awal kode
        chart_data = yf.download(selected_stocks, start=chart_start, end=end_date_str, progress=False)
        if not chart_data.empty:
            st.line_chart(chart_data['Close'])

# === TAB 4: WIN/LOSS (Dengan Tabel 30 Hari Terakhir) ===
with tabs[3]:
    st.header("🎲 Win/Loss Statistics")
    wl_input = st.text_area("Input Tickers (contoh: BBCA, GOTO):", value="BBCA.JK, GOTO.JK")
    if st.button("Hitung Statistik"):
        summ, det = get_win_loss_details(wl_input)
        st.subheader("Ringkasan Performa")
        st.dataframe(summ, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("📊 Histori 30 Hari Terakhir (Gain/Loss %)")
        for ticker, df_hist in det.items():
            with st.expander(f"Detail Harian {ticker}"):
                df_show = df_hist.copy()
                df_show.index = pd.to_datetime(df_show.index).strftime('%Y-%m-%d')
                df_show = df_show.sort_index(ascending=False)
                
                def bg_logic(val):
                    c = '#90ee90' if val > 0 else '#ffcccb' if val < 0 else 'transparent'
                    return f'background-color: {c}'
                
                st.dataframe(df_show.style.applymap(bg_logic).format("{:.2f}%"), use_container_width=True)

# (Tab Grid, Bandingkan, dan Simulator tetap ada dengan logika standar)
