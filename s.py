import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

DB_FILE = "stock_database.json"

# --- 2. FUNGSI DATABASE (PERSISTENCE) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        # Kita simpan list Tab 2 di sini agar tidak hilang
        "vol_saved_tickers": st.session_state.get("vol_saved_tickers", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 3. INISIALISASI SESSION ---
saved_data = load_data()

# Load Main Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else ["BBCA.JK", "GOTO.JK", "BBRI.JK"]

# Load Volume Watchlist (Tab 2 Persistence)
if 'vol_saved_tickers' not in st.session_state:
    st.session_state.vol_saved_tickers = saved_data["vol_saved_tickers"] if (saved_data and "vol_saved_tickers" in saved_data) else []

if 'picked_stocks' not in st.session_state:
    st.session_state.picked_stocks = []

# --- 4. DATA STATIC (DAFTAR SAHAM) ---
GRID_TICKERS = [
    "AALI.JK","ABBA.JK","ABDA.JK","ABMM.JK","ACES.JK","ACST.JK","ADES.JK","ADHI.JK","ADMF.JK","ADMG.JK","ADRO.JK","AGII.JK","AGRO.JK","AGRS.JK","AHAP.JK","AIMS.JK","AISA.JK","AKKU.JK","AKPI.JK","AKRA.JK","AKSI.JK","ALDO.JK","ALKA.JK","ALMI.JK","ALTO.JK","AMAG.JK","AMFG.JK","AMIN.JK","AMRT.JK","ANJT.JK","ANTM.JK","APEX.JK","APIC.JK","APII.JK","APLI.JK","APLN.JK","ARGO.JK","ARII.JK","ARNA.JK","ARTA.JK","ARTI.JK","ARTO.JK","ASBI.JK","ASDM.JK","ASGR.JK","ASII.JK","ASJT.JK","ASMI.JK","ASRI.JK","ASRM.JK","ASSA.JK","ATIC.JK","AUTO.JK","BABP.JK","BACA.JK","BAJA.JK","BALI.JK","BAPA.JK","BATA.JK","BAYU.JK","BBCA.JK","BBHI.JK","BBKP.JK","BBLD.JK","BBMD.JK","BBNI.JK","BBRI.JK","BBRM.JK","BBTN.JK","BBYB.JK","BCAP.JK","BCIC.JK","BCIP.JK","BDMN.JK","BEKS.JK","BEST.JK","BFIN.JK","BGTG.JK","BHIT.JK","BIKA.JK","BIMA.JK","BINA.JK","BIPI.JK","BIPP.JK","BIRD.JK","BISI.JK","BJBR.JK","BJTM.JK","BKDP.JK","BKSL.JK","BKSW.JK","BLTA.JK","BLTZ.JK","BMAS.JK","BMRI.JK","BMSR.JK","BMTR.JK","BNBA.JK","BNBR.JK","BNGA.JK","BNII.JK","BNLI.JK","BOLT.JK","BPFI.JK","BPII.JK","BRAM.JK","BRMS.JK","BRNA.JK","BRPT.JK","BSDE.JK","BSIM.JK","BSSR.JK","BSWD.JK","BTEK.JK","BTEL.JK","BTON.JK","BTPN.JK","BUDI.JK","BUKK.JK","BULL.JK","BUMI.JK","BUVA.JK","BVIC.JK","BWPT.JK","BYAN.JK","CANI.JK","CASS.JK","CEKA.JK","CENT.JK","CFIN.JK","CINT.JK","CITA.JK","CLPI.JK","CMNP.JK","CMPP.JK","CNKO.JK","CNTX.JK","COWL.JK","CPIN.JK","CPRO.JK","CSAP.JK","CTBN.JK","CTRA.JK","CTTH.JK","DART.JK","DEFI.JK","DEWA.JK","DGIK.JK","DILD.JK","DKFT.JK","DLTA.JK","DMAS.JK","DNAR.JK","DNET.JK","DOID.JK","DPNS.JK","DSFI.JK","DSNG.JK","DSSA.JK","DUTI.JK","DVLA.JK","DYAN.JK","ECII.JK","EKAD.JK","ELSA.JK","ELTY.JK","EMDE.JK","EMTK.JK","ENRG.JK","EPMT.JK","ERAA.JK","ERTX.JK","ESSA.JK","ESTI.JK","ETWA.JK","EXCL.JK","FAST.JK","FASW.JK","FISH.JK","FMII.JK","FORU.JK","FPNI.JK","GAMA.JK","GDST.JK","GDYR.JK","GEMA.JK","GEMS.JK","GGRM.JK","GIAA.JK","GJTL.JK","GLOB.JK","GMTD.JK","GOLD.JK","GOLL.JK","GPRA.JK","GSMF.JK","GTBO.JK","GWSA.JK","GZCO.JK","HADE.JK","HDFA.JK","HERO.JK","HEXA.JK","HITS.JK","HMSP.JK","HOME.JK","HOTL.JK","HRUM.JK","IATA.JK","IBFN.JK","IBST.JK","ICBP.JK","ICON.JK","IGAR.JK","IIKP.JK","IKAI.JK","IKBI.JK","IMAS.JK","IMJS.JK","IMPC.JK","INAF.JK","INAI.JK","INCI.JK","INCO.JK","INDF.JK","INDR.JK","INDS.JK","INDX.JK","INDY.JK","INKP.JK","INPC.JK","INPP.JK","INRU.JK","INTA.JK","INTD.JK","INTP.JK","IPOL.JK","ISAT.JK","ISSP.JK","ITMA.JK","ITMG.JK","JAWA.JK","JECC.JK","JIHD.JK","JKON.JK","JPFA.JK","JRPT.JK","JSMR.JK","JSPT.JK","JTPE.JK","KAEF.JK","KARW.JK","KBLI.JK","KBLM.JK","KBLV.JK","KBRI.JK","KDSI.JK","KIAS.JK","KICI.JK","KIJA.JK","KKGI.JK","KLBF.JK","KOBX.JK","KOIN.JK","KONI.JK","KOPI.JK","KPIG.JK","KRAS.JK","KREN.JK","LAPD.JK","LCGP.JK","LEAD.JK","LINK.JK","LION.JK","LMAS.JK","LMPI.JK","LMSH.JK","LPCK.JK","LPGI.JK","LPIN.JK","LPKR.JK","LPLI.JK","LPPF.JK","LPPS.JK","LRNA.JK","LSIP.JK","LTLS.JK","MAGP.JK","MAIN.JK","MAPI.JK","MAYA.JK","MBAP.JK","MBSS.JK","MBTO.JK","MCOR.JK","MDIA.JK","MDKA.JK","MDLN.JK","MDRN.JK","MEDC.JK","MEGA.JK","MERK.JK","META.JK","MFMI.JK","MGNA.JK","MICE.JK","MIDI.JK","MIKA.JK","MIRA.JK","MITI.JK","MKPI.JK","MLBI.JK","MLIA.JK","MLPL.JK","MLPT.JK","MMLP.JK","MNCN.JK","MPMX.JK","MPPA.JK","MRAT.JK","MREI.JK","MSKY.JK","MTDL.JK","MTFN.JK","MTLA.JK","MTSM.JK","MYOH.JK","MYOR.JK","MYTX.JK","NELY.JK","NIKL.JK","NIRO.JK","NISP.JK","NOBU.JK","NRCA.JK","OCAP.JK","OKAS.JK","OMRE.JK","PADI.JK","PALM.JK","PANR.JK","PANS.JK","PBRX.JK","PDES.JK","PEGE.JK","PGAS.JK","PGLI.JK","PICO.JK","PJAA.JK","PKPK.JK","PLAS.JK","PLIN.JK","PNBN.JK","PNBS.JK","PNIN.JK","PNLF.JK","PNSE.JK","POLY.JK","POOL.JK","PPRO.JK","PSAB.JK","PSDN.JK","PSKT.JK","PTBA.JK","PTIS.JK","PTPP.JK","PTRO.JK","PTSN.JK","PTSP.JK","PUDP.JK","PWON.JK","PYFA.JK","RAJA.JK","RALS.JK","RANC.JK","RBMS.JK","RDTX.JK","RELI.JK","RICY.JK","RIGS.JK","RIMO.JK","RODA.JK","ROTI.JK","RUIS.JK","SAFE.JK","SAME.JK","SCCO.JK","SCMA.JK","SCPI.JK","SDMU.JK","SDPC.JK","SDRA.JK","SGRO.JK","SHID.JK","SIDO.JK","SILO.JK","SIMA.JK","SIMP.JK","SIPD.JK","SKBM.JK","SKLT.JK","SKYB.JK","SMAR.JK","SMBR.JK","SMCB.JK","SMDM.JK","SMDR.JK","SMGR.JK","SMMA.JK","SMMT.JK","SMRA.JK","SMRU.JK","SMSM.JK","SOCI.JK","SONA.JK","SPMA.JK","SQMI.JK","SRAJ.JK","SRIL.JK","SRSN.JK","SRTG.JK","SSIA.JK","SSMS.JK","SSTM.JK","STAR.JK","STTP.JK","SUGI.JK","SULI.JK","SUPR.JK","TALF.JK","TARA.JK","TAXI.JK","TBIG.JK","TBLA.JK","TBMS.JK","TCID.JK","TELE.JK","TFCO.JK","TGKA.JK","TIFA.JK","TINS.JK","TIRA.JK","TIRT.JK","TKIM.JK","TLKM.JK","TMAS.JK","TMPO.JK","TOBA.JK","TOTL.JK","TOTO.JK","TOWR.JK","TPIA.JK","TPMA.JK","TRAM.JK","TRIL.JK","TRIM.JK","TRIO.JK","TRIS.JK","TRST.JK","TRUS.JK","TSPC.JK","ULTJ.JK","UNIC.JK","UNIT.JK","UNSP.JK","UNTR.JK","UNVR.JK","VICO.JK","VINS.JK","VIVA.JK","VOKS.JK","VRNA.JK","WAPO.JK","WEHA.JK","WICO.JK","WIIM.JK","WIKA.JK","WINS.JK","WOMF.JK","WSKT.JK","WTON.JK","YPAS.JK","YULE.JK","ZBRA.JK","SHIP.JK","CASA.JK","DAYA.JK","DPUM.JK","IDPR.JK","JGLE.JK","KINO.JK","MARI.JK","MKNT.JK","MTRA.JK","OASA.JK","POWR.JK","INCF.JK","WSBP.JK","PBSA.JK","PRDA.JK","BOGA.JK","BRIS.JK","PORT.JK","CARS.JK","MINA.JK","CLEO.JK","TAMU.JK","CSIS.JK","TGRA.JK","FIRE.JK","TOPS.JK","KMTR.JK","ARMY.JK","MAPB.JK","WOOD.JK","HRTA.JK","MABA.JK","HOKI.JK","MPOW.JK","MARK.JK","NASA.JK","MDKI.JK","BELL.JK","KIOS.JK","GMFI.JK","MTWI.JK","ZINC.JK","MCAS.JK","PPRE.JK","WEGE.JK","PSSI.JK","MORA.JK","DWGL.JK","PBID.JK","JMAS.JK","CAMP.JK","IPCM.JK","PCAR.JK","LCKM.JK","BOSS.JK","HELI.JK","JSKY.JK","INPS.JK","GHON.JK","TDPM.JK","DFAM.JK","NICK.JK","BTPS.JK","SPTO.JK","PRIM.JK","HEAL.JK","TRUK.JK","PZZA.JK","TUGU.JK","MSIN.JK","SWAT.JK","TNCA.JK","MAPA.JK","TCPI.JK","IPCC.JK","RISE.JK","BPTR.JK","POLL.JK","NFCX.JK","MGRO.JK","NUSA.JK","FILM.JK","ANDI.JK","LAND.JK","MOLI.JK","PANI.JK","DIGI.JK","CITY.JK","SAPX.JK","SURE.JK","HKMU.JK","MPRO.JK","DUCK.JK","GOOD.JK","SKRN.JK","YELO.JK","CAKK.JK","SATU.JK","SOSS.JK","DEAL.JK","POLA.JK","DIVA.JK","LUCK.JK","URBN.JK","SOTS.JK","ZONE.JK","PEHA.JK","FOOD.JK","BEEF.JK","POLI.JK","CLAY.JK","NATO.JK","JAYA.JK","COCO.JK","MTPS.JK","CPRI.JK","HRME.JK","POSA.JK","JAST.JK","FITT.JK","BOLA.JK","CCSI.JK","SFAN.JK","POLU.JK","KJEN.JK","KAYU.JK","ITIC.JK","PAMG.JK","IPTV.JK","BLUE.JK","ENVY.JK","EAST.JK","LIFE.JK","FUJI.JK","KOTA.JK","INOV.JK","ARKA.JK","SMKL.JK","HDIT.JK","KEEN.JK","BAPI.JK","TFAS.JK","GGRP.JK","OPMS.JK","NZIA.JK","SLIS.JK","PURE.JK","IRRA.JK","DMMX.JK","SINI.JK","WOWS.JK","ESIP.JK","TEBE.JK","KEJU.JK","PSGO.JK","AGAR.JK","IFSH.JK","REAL.JK","IFII.JK","PMJS.JK","UCID.JK","GLVA.JK","PGJO.JK","AMAR.JK","CSRA.JK","INDO.JK","AMOR.JK","TRIN.JK","DMND.JK","PURA.JK","PTPW.JK","TAMA.JK","IKAN.JK","SAMF.JK","SBAT.JK","KBAG.JK","CBMF.JK","RONY.JK","CSMI.JK","BBSS.JK","BHAT.JK","CASH.JK","TECH.JK","EPAC.JK","UANG.JK","PGUN.JK","SOFA.JK","PPGL.JK","TOYS.JK","SGER.JK","TRJA.JK","PNGO.JK","SCNP.JK","BBSI.JK","KMDS.JK","PURI.JK","SOHO.JK","HOMI.JK","ROCK.JK","ENZO.JK","PLAN.JK","PTDU.JK","ATAP.JK","VICI.JK","PMMP.JK","BANK.JK","WMUU.JK","EDGE.JK","UNIQ.JK","BEBS.JK","SNLK.JK","ZYRX.JK","LFLO.JK","FIMP.JK","TAPG.JK","NPGF.JK","LUCY.JK","ADCP.JK","HOPE.JK","MGLV.JK","TRUE.JK","LABA.JK","ARCI.JK","IPAC.JK","MASB.JK","BMHS.JK","FLMC.JK","NICL.JK","UVCR.JK","BUKA.JK","HAIS.JK","OILS.JK","GPSO.JK","MCOL.JK","RSGK.JK","RUNS.JK","SBMA.JK","CMNT.JK","GTSI.JK","IDEA.JK","KUAS.JK","BOBA.JK","MTEL.JK","DEPO.JK","BINO.JK","CMRY.JK","WGSH.JK","TAYS.JK","WMPP.JK","RMKE.JK","OBMD.JK","AVIA.JK","IPPE.JK","NASI.JK","BSML.JK","DRMA.JK","ADMR.JK","SEMA.JK","ASLC.JK","NETV.JK","BAUT.JK","ENAK.JK","NTBK.JK","SMKM.JK","STAA.JK","NANO.JK","BIKE.JK","WIRG.JK","SICO.JK","GOTO.JK","TLDN.JK","MTMH.JK","WINR.JK","IBOS.JK","OLIV.JK","ASHA.JK","SWID.JK","TRGU.JK","ARKO.JK","CHEM.JK","DEWI.JK","AXIO.JK","KRYA.JK","HATM.JK","RCCC.JK","GULA.JK","JARR.JK","AMMS.JK","RAFI.JK","KKES.JK","ELPI.JK","EURO.JK","KLIN.JK","TOOL.JK","BUAH.JK","CRAB.JK","MEDS.JK","COAL.JK","PRAY.JK","CBUT.JK","BELI.JK","MKTR.JK","OMED.JK","BSBK.JK","PDPP.JK","KDTN.JK","ZATA.JK","NINE.JK","MMIX.JK","PADA.JK","ISAP.JK","VTNY.JK","SOUL.JK","ELIT.JK","BEER.JK","CBPE.JK","SUNI.JK","CBRE.JK","WINE.JK","BMBL.JK","PEVE.JK","LAJU.JK","FWCT.JK","NAYZ.JK","IRSX.JK","PACK.JK","VAST.JK","CHIP.JK","HALO.JK","KING.JK","PGEO.JK","FUTR.JK","HILL.JK","BDKR.JK","PTMP.JK","SAGE.JK","TRON.JK","CUAN.JK","NSSS.JK","GTRA.JK","HAJJ.JK","JATI.JK","TYRE.JK","MPXL.JK","SMIL.JK","KLAS.JK","MAXI.JK","VKTR.JK","RELF.JK","AMMN.JK","CRSN.JK","GRPM.JK","WIDI.JK","TGUK.JK","INET.JK","MAHA.JK","RMKO.JK","CNMA.JK","FOLK.JK","HBAT.JK","GRIA.JK","PPRI.JK","ERAL.JK","CYBR.JK","MUTU.JK","LMAX.JK","HUMI.JK","MSIE.JK","RSCH.JK","BABY.JK","AEGS.JK","IOTF.JK","KOCI.JK","PTPS.JK","BREN.JK","STRK.JK","KOKA.JK","LOPI.JK","UDNG.JK","RGAS.JK","MSTI.JK","IKPM.JK","AYAM.JK","SURI.JK","ASLI.JK","GRPH.JK","SMGA.JK","UNTD.JK","TOSK.JK","MPIX.JK","ALII.JK","MKAP.JK","MEJA.JK","LIVE.JK","HYGN.JK","BAIK.JK","VISI.JK","AREA.JK","MHKI.JK","ATLA.JK","DATA.JK","SOLA.JK","BATR.JK","SPRE.JK","PART.JK","GOLF.JK","ISEA.JK","BLES.JK","GUNA.JK","LABS.JK","DOSS.JK","NEST.JK","PTMR.JK","VERN.JK","DAAZ.JK","BOAT.JK","NAIK.JK","AADI.JK","MDIY.JK","KSIX.JK","RATU.JK","YOII.JK","HGII.JK","BRRC.JK","DGWG.JK","CBDK.JK","OBAT.JK","MINE.JK","ASPR.JK","PSAT.JK","COIN.JK","CDIA.JK","BLOG.JK","MERI.JK","CHEK.JK","PMUI.JK","EMAS.JK","PJHB.JK","KAQI.JK","YUPI.JK","FORE.JK","MDLA.JK","DKHH.JK","AYLS.JK","DADA.JK","ASPI.JK","ESTA.JK","BESS.JK","AMAN.JK","CARE.JK","PIPA.JK","NCKL.JK","MENN.JK","AWAN.JK","MBMA.JK","RAAM.JK","DOOH.JK","CGAS.JK","NICE.JK","MSJA.JK","SMLE.JK","ACRO.JK","MANG.JK","WIFI.JK","FAPA.JK","DCII.JK","KETR.JK","DGNS.JK","UFOE.JK",
    # Tambah sampai 100 ticker
]

SAMPLE_SCREENER_TICKERS = GRID_TICKERS

# --- 5. FUNGSI LOGIKA (BACKEND) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    if not tickers: return pd.DataFrame()
    # Logic 1 Hari: Pakai 5m interval
    interv = "5m" if period == "1d" else "1d"
    try:
        data = yf.download(tickers, period=period, interval=interv, group_by='ticker', progress=False, auto_adjust=False)
        return data
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_single_stock_detail(ticker, period):
    if not ticker: return None
    interv = "5m" if period == "1d" else "1d"
    try:
        df = yf.download(ticker, period=period, interval=interv, progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()] 
        if 'Close' not in df.columns and 'Adj Close' in df.columns:
            df = df.rename(columns={'Adj Close': 'Close'})
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df
    except: return None

@st.cache_data(ttl=3600)
def get_fundamental_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "pbv": info.get('priceToBook'),
            "per": info.get('trailingPE'),
            "eps": info.get('trailingEps'),
            "mkt_cap": info.get('marketCap'),
            "sector": info.get('industry', '-')
        }
    except: return None

@st.cache_data(ttl=3600)
def get_financials_history(ticker):
    try:
        stock = yf.Ticker(ticker)
        q_fin = stock.quarterly_financials.T
        if not q_fin.empty:
            q_fin.index = pd.to_datetime(q_fin.index).tz_localize(None)
            q_fin = q_fin.sort_index()
        a_fin = stock.financials.T
        if not a_fin.empty:
            a_fin.index = pd.to_datetime(a_fin.index).tz_localize(None)
            a_fin = a_fin.sort_index()
        return q_fin, a_fin
    except: return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=600)
def get_seasonal_details(tickers_str, start_month, end_month, lookback_years=5):
    if not tickers_str: return None
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    start_date = datetime.now() - timedelta(days=(lookback_years + 2) * 365)
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=False)
    results = {} 
    for ticker in ticker_list:
        try:
            if len(ticker_list) == 1: df = data; symbol = ticker_list[0]
            else: df = data[ticker]; symbol = ticker
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'Date'})
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            stock_years_data = {}
            current_year = datetime.now().year
            for i in range(0, lookback_years + 1):
                y_end = current_year - i
                if int(start_month) > int(end_month): y_start = y_end - 1 
                else: y_start = y_end
                try:
                    d_start = datetime(y_start, int(start_month), 1)
                    if d_start > datetime.now(): continue
                    d_end = datetime(y_end, int(end_month), 28) 
                    label = f"{y_start}/{y_end}" if int(start_month) > int(end_month) else f"{y_end}"
                except: continue
                mask = (df['Date'] >= d_start) & (df['Date'] <= d_end)
                df_period = df.loc[mask].copy()
                if df_period.empty: continue
                first_price = df_period['Close'].iloc[0]
                df_period['Rel_Change'] = ((df_period['Close'] - first_price) / first_price) * 100
                stock_years_data[label] = df_period['Rel_Change'].reset_index(drop=True)
            if stock_years_data: results[symbol] = stock_years_data
        except: continue
    return results

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_list, period_code="1mo"):
    if not tickers_list: return None
    
    # Logic: Jika user minta 1d, kita tetap butuh history (misal 5d) untuk hitung Avg Volume
    # Tapi Change % nya kita ambil dari data 1d
    download_period = "5d" if period_code == "1d" else "1mo"
    if period_code == "ytd": download_period = "ytd"
    elif period_code == "1y": download_period = "1y"
    
    try:
        data = yf.download(tickers_list, period=download_period, group_by='ticker', progress=False, auto_adjust=False)
    except: return None

    stats = []
    for t in tickers_list:
        try:
            if len(tickers_list) == 1: df = data; symbol = tickers_list[0]
            else: 
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Data Terakhir
            last_vol = df['Volume'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            
            # Hitung Avg Vol (selalu 5 hari terakhir utk referensi)
            avg_vol = df['Volume'].tail(5).mean()
            
            # Hitung Change % Sesuai Periode Pilihan
            if period_code == "1d":
                # Intraday Change (Close - Open) / Open
                # Atau Close hari ini vs Close Kemarin? Biasanya vs Kemarin.
                if len(df) >= 2:
                    prev_close = df['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                else: change_pct = 0.0
            else:
                # Change dari awal periode download
                first_close = df['Close'].iloc[0]
                change_pct = ((last_close - first_close) / first_close) * 100

            stats.append({
                "Ticker": symbol, 
                "Price": last_close,
                "Change %": change_pct,
                "Volume": last_vol, 
                "Avg Vol (5D)": avg_vol, 
                "Est. Value": last_close * last_vol,
                "Vol vs Avg": (last_vol / avg_vol) if avg_vol > 0 else 0
            })
        except: continue
    return pd.DataFrame(stats)

@st.cache_data(ttl=300)
def get_latest_prices(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False, auto_adjust=False)
        prices = {}
        for t in tickers:
            try:
                if len(tickers) == 1: df = data
                else: 
                    if isinstance(data.columns, pd.MultiIndex):
                        if t in data.columns.levels[0]: df = data[t]
                        else: continue
                    else:
                        if len(tickers) == 1: df = data 
                        else: continue
                if not df.empty:
                    col = 'Close' if 'Close' in df.columns else 'Adj Close'
                    last_price = df[col].iloc[-1]
                    prices[t] = float(last_price)
            except: continue
        return prices
    except: return {}

@st.cache_data(ttl=3600)
def get_fundamental_screener(tickers_list):
    screener_data = []
    progress_bar = st.progress(0)
    total = len(tickers_list)
    for i, ticker in enumerate(tickers_list):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info 
            industry = info.get('industry', 'Others/Unknown')
            curr_price = info.get('currentPrice', info.get('previousClose', 0))
            high_52 = info.get('fiftyTwoWeekHigh', 0)
            low_52 = info.get('fiftyTwoWeekLow', 0)
            pbv = info.get('priceToBook', None)
            per = info.get('trailingPE', None)
            eps_ttm = info.get('trailingEps', None)
            screener_data.append({
                "Ticker": ticker, "Industry": industry,
                "Price": float(curr_price) if curr_price else 0,
                "52W High": float(high_52) if high_52 else 0,
                "52W Low": float(low_52) if low_52 else 0,
                "PBV": float(pbv) if pbv else None, "PER": float(per) if per else None, "EPS": float(eps_ttm) if eps_ttm else None
            })
        except Exception: pass
        progress_bar.progress((i + 1) / total)
    progress_bar.empty()
    return pd.DataFrame(screener_data)

@st.cache_data(ttl=600) 
def get_performance_matrix(raw_input):
    if not raw_input: return pd.DataFrame()
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            if len(item) == 4 and item.isalpha(): item += ".JK"
            tickers.append(item)
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame()

    try:
        data = yf.download(tickers, period="5y", group_by='ticker', progress=False, auto_adjust=False)
    except Exception: return pd.DataFrame()
    
    results = []
    for t in tickers:
        try:
            try: industry = yf.Ticker(t).info.get('industry', '-')
            except: industry = '-'

            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: price_col = 'Close'
            elif 'Adj Close' in df.columns: price_col = 'Adj Close'
            else: continue
            
            df = df[[price_col]].rename(columns={price_col: 'Close'})
            df = df.dropna()
            df.index = df.index.tz_localize(None)
            df = df.sort_index()
            if len(df) < 2: continue
            
            curr_price = float(df['Close'].iloc[-1])
            curr_date = df.index[-1]

            def get_pct_change(days_ago):
                target_date = curr_date - timedelta(days=days_ago)
                past_data = df.loc[df.index <= target_date]
                if past_data.empty: return None
                past_price = float(past_data['Close'].iloc[-1])
                if past_price == 0: return 0.0
                return ((curr_price - past_price) / past_price) * 100

            last_year = curr_date.year - 1
            last_year_end = datetime(last_year, 12, 31)
            ytd_data = df.loc[df.index <= last_year_end]
            if not ytd_data.empty:
                last_year_close = float(ytd_data['Close'].iloc[-1])
                ytd_change = ((curr_price - last_year_close) / last_year_close) * 100
            else: ytd_change = None

            results.append({
                "Ticker": symbol, "Industri": industry, "Harga": curr_price,
                "1 Hari": ((curr_price - df['Close'].iloc[-2])/df['Close'].iloc[-2]) * 100,
                "1 Minggu": get_pct_change(7), "1 Bulan": get_pct_change(30),
                "6 Bulan": get_pct_change(180), "YTD": ytd_change,
                "1 Tahun": get_pct_change(365), "3 Tahun": get_pct_change(365 * 3)
            })
        except Exception: continue
    return pd.DataFrame(results)

@st.cache_data(ttl=600)
def get_win_loss_details(raw_input):
    clean_input = raw_input.replace('\n', ',').replace(' ', ',')
    tickers = []
    for t in clean_input.split(','):
        item = t.strip().upper()
        if item:
            if len(item) == 4 and item.isalpha(): item += ".JK"
            tickers.append(item)
    tickers = list(set(tickers))
    if not tickers: return pd.DataFrame(), {}

    try:
        data = yf.download(tickers, period="3mo", group_by='ticker', progress=False, auto_adjust=False)
    except: return pd.DataFrame(), {}

    summary_results = []
    detail_data = {} 

    for t in tickers:
        try:
            if len(tickers) == 1: df = data; symbol = tickers[0]
            else:
                if isinstance(data.columns, pd.MultiIndex):
                     if t not in data.columns.levels[0]: continue
                df = data[t]; symbol = t
            
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if 'Close' in df.columns: col = 'Close'
            elif 'Adj Close' in df.columns: col = 'Adj Close'
            else: continue

            df['Change'] = df[col].pct_change() * 100
            df = df.dropna()

            df_30 = df.tail(30)
            if len(df_30) < 5: continue 

            detail_data[symbol] = df_30

            green_days = df_30[df_30['Change'] > 0]
            red_days = df_30[df_30['Change'] < 0]

            count_green = len(green_days)
            count_red = len(red_days)
            win_rate = (count_green / len(df_30)) * 100

            avg_gain = green_days['Change'].mean() if not green_days.empty else 0
            avg_loss = red_days['Change'].mean() if not red_days.empty else 0
            total_return_30d = ((df_30[col].iloc[-1] - df_30[col].iloc[0]) / df_30[col].iloc[0]) * 100

            summary_results.append({
                "Ticker": symbol, "Total Candle": len(df_30), "Hari Hijau": count_green, "Hari Merah": count_red,
                "Win Rate": win_rate, "Rata2 Naik": avg_gain, "Rata2 Turun": avg_loss, "Total Return (30 Candle)": total_return_30d
            })
        except: continue
    
    return pd.DataFrame(summary_results), detail_data

# --- 6. VISUALISASI ---

def create_mini_chart(df, ticker, period_code, show_ma=True):
    fig = go.Figure()
    if len(df) < 5 and period_code != "1d": return fig

    ma20 = df['Close'].rolling(window=20).mean()
    last_p = df['Close'].iloc[-1]
    prev_p = df['Close'].iloc[-2]
    color = '#00C805' if float(last_p) >= float(prev_p) else '#FF333A'
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=color, width=1.5)))
    if show_ma and period_code != "1d":
        fig.add_trace(go.Scatter(x=df.index, y=ma20, mode='lines', line=dict(color='#FF9800', width=1)))
    
    if period_code == "3mo":
        one_month_ago = datetime.now() - timedelta(days=30)
        fig.add_vline(x=one_month_ago.timestamp() * 1000, line_width=1, line_dash="dot", line_color="blue")
    
    fig.update_layout(
        title=dict(text=ticker, font=dict(size=12), x=0.5, xanchor='center'),
        margin=dict(l=0, r=0, t=30, b=0),
        height=150,
        showlegend=False,
        xaxis=dict(showticklabels=False, fixedrange=True),
        yaxis=dict(showticklabels=False, fixedrange=True)
    )
    return fig

def create_detail_chart(df, ticker, df_fin_filtered):
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        row_heights=[0.5, 0.2, 0.3],
        subplot_titles=(f"Price Action: {ticker}", "Volume", "Revenue & Net Income")
    )
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", showlegend=False), row=1, col=1)
    if len(df) > 20: fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), name="MA 20"), row=1, col=1)
    colors = ['#00C805' if c >= o else '#FF333A' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
    if not df_fin_filtered.empty:
        rev_col = next((c for c in df_fin_filtered.columns if 'Revenue' in c or 'revenue' in c), None)
        inc_col = next((c for c in df_fin_filtered.columns if 'Net Income' in c or 'netIncome' in c), None)
        if rev_col: fig.add_trace(go.Bar(x=df_fin_filtered.index, y=df_fin_filtered[rev_col], name="Revenue", marker_color='blue', opacity=0.6), row=3, col=1)
        if inc_col: fig.add_trace(go.Bar(x=df_fin_filtered.index, y=df_fin_filtered[inc_col], name="Net Income", marker_color='green', opacity=0.8), row=3, col=1)
    fig.update_layout(height=800, xaxis_rangeslider_visible=False, hovermode="x unified")
    return fig

# --- 7. MAIN UI ---
st.title("📈 Super Stock Dashboard")

tab_grid, tab_compare, tab_vol, tab_watch, tab_detail, tab_cycle, tab_fund, tab_perf, tab_win = st.tabs([
    "📊 Grid", "⚖️ Bandingkan", "🔊 Volume", "⭐ Watchlist", "🔎 Detail", "🔄 Cycle", "💎 Fundamental", "🚀 Performa", "🎲 Win/Loss Stats"
])

# === TAB 1: GRID (FILTERED + 1 DAY OPTION) ===
with tab_grid:
    st.write("Grid Overview - **Pilih saham untuk dimasukkan ke tab 'Bandingkan'**")
    
    with st.expander("🔍 Filter Grid (Harga)", expanded=False):
        c_min, c_max = st.columns(2)
        with c_min: min_p = st.number_input("Harga Minimum (Rp)", value=0, step=50)
        with c_max: max_p = st.number_input("Harga Maksimum (Rp)", value=100000, step=50)
    
    final_tickers = GRID_TICKERS
    
    if max_p < 100000 or min_p > 0:
        with st.spinner("Memfilter saham..."):
            prices = get_latest_prices(GRID_TICKERS)
            filtered_list = []
            for t, p in prices.items():
                if min_p <= p <= max_p:
                    filtered_list.append(t)
            final_tickers = filtered_list
            st.success(f"Ditemukan {len(final_tickers)} saham sesuai filter.")

    c_opt, c_pg = st.columns([2, 4])
    with c_opt:
        period_label = st.selectbox("Rentang Waktu:", ["1 Hari", "3 Bulan", "6 Bulan", "1 Tahun", "YTD"], index=1)
        period_map = {"1 Hari": "1d", "3 Bulan": "3mo", "6 Bulan": "6mo", "1 Tahun": "1y", "YTD": "ytd"}
        selected_code = period_map[period_label]
        
    with c_pg:
        if 'page' not in st.session_state: st.session_state.page = 1
        items_per_page = 16 
        if not final_tickers:
            st.warning("Tidak ada saham yang sesuai filter.")
            total_pages = 1
        else:
            total_pages = math.ceil(len(final_tickers)/items_per_page)
        curr_page = st.number_input("Halaman", 1, total_pages, key="grid_page")
        
    if final_tickers:
        start, end = (curr_page - 1) * items_per_page, (curr_page - 1) * items_per_page + items_per_page
        batch = final_tickers[start:end]
        
        def toggle_pick(ticker):
            if ticker in st.session_state.picked_stocks:
                st.session_state.picked_stocks.remove(ticker)
            else:
                st.session_state.picked_stocks.append(ticker)

        with st.spinner("Memuat grafik..."):
            data_grid = get_stock_history_bulk(batch, period=selected_code)
            
            if not data_grid.empty:
                cols = st.columns(4)
                for i, ticker in enumerate(batch):
                    col_idx = i % 4
                    with cols[col_idx]:
                        try:
                            df_target = pd.DataFrame()
                            if isinstance(data_grid.columns, pd.MultiIndex):
                                if ticker in data_grid.columns.levels[0]: df_target = data_grid[ticker].copy()
                            else:
                                if len(batch) == 1: df_target = data_grid.copy()
                            
                            if df_target.empty:
                                st.caption(f"❌ {ticker}")
                                continue
                                
                            if 'Close' not in df_target.columns and 'Adj Close' in df_target.columns:
                                df_target = df_target.rename(columns={'Adj Close': 'Close'})
                                
                            df_target = df_target.dropna()
                            min_len = 5 if selected_code != "1d" else 2
                            
                            if len(df_target) >= min_len:
                                fig = create_mini_chart(df_target, ticker, selected_code)
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                                is_checked = ticker in st.session_state.picked_stocks
                                st.checkbox(f"✅ Pilih {ticker}", value=is_checked, key=f"chk_{ticker}_{curr_page}", on_change=toggle_pick, args=(ticker,))
                            else: st.caption(f"⚠️ {ticker}")
                        except Exception as e: st.caption(f"⚠️ {ticker} Error")

    st.info(f"🛒 Keranjang Pilihan: {len(st.session_state.picked_stocks)} saham terpilih. Buka Tab '⚖️ Bandingkan' untuk seleksi.")

# === TAB 10: BANDINGKAN ===
with tab_compare:
    st.header("⚖️ Bandingkan & Eliminasi")
    picked = st.session_state.picked_stocks
    if not picked:
        st.warning("Belum ada saham yang dipilih dari Tab '📊 Grid'.")
    else:
        st.write(f"Membandingkan **{len(picked)}** saham pilihanmu.")
        if st.button("🗑️ Hapus Semua Pilihan"):
            st.session_state.picked_stocks = []
            st.rerun()
        with st.spinner("Mengambil data detail..."):
            comp_data = get_stock_history_bulk(picked, period="6mo")
            comp_cols = st.columns(3) 
            for i, ticker in enumerate(picked):
                c_idx = i % 3
                with comp_cols[c_idx]:
                    st.divider()
                    try:
                        df_c = pd.DataFrame()
                        if isinstance(comp_data.columns, pd.MultiIndex):
                            if ticker in comp_data.columns.levels[0]: df_c = comp_data[ticker].copy()
                        else:
                            if len(picked) == 1: df_c = comp_data.copy()
                        
                        if not df_c.empty:
                            df_c = df_c.dropna()
                            fig = create_mini_chart(df_c, ticker, "6mo") 
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            if st.button(f"❌ Hapus {ticker}", key=f"del_{ticker}"):
                                st.session_state.picked_stocks.remove(ticker)
                                st.rerun()
                    except: st.error(f"Gagal load {ticker}")

# === TAB 2: VOLUME (FIXED PERSISTENCE & 1 DAY OPTION) ===
with tab_vol:
    st.header("Analisis Volume")
    st.write("Cari volume saham spesifik atau lihat Top 20 dari saham-saham populer.")
    
    # Init text area dengan data dari DB (Persistent)
    default_text = ", ".join(st.session_state.vol_saved_tickers)
    
    # 1. INPUTS
    c1, c2 = st.columns([3, 1])
    with c1:
        vol_input = st.text_area("Input Saham (Pisahkan koma/spasi/enter):", value=default_text, height=70, placeholder="Misal: BBCA, GOTO", key="vol_in_multi")
    with c2:
        st.write("")
        # Add Period Selector for Volume Tab
        vol_period = st.selectbox("Rentang Waktu:", ["1 Hari", "1 Minggu", "1 Bulan", "YTD"], index=2)
        vol_period_map = {"1 Hari": "1d", "1 Minggu": "5d", "1 Bulan": "1mo", "YTD": "ytd"}
        selected_vol_period = vol_period_map[vol_period]
        
    c3, c4, c5 = st.columns([1, 1, 1])
    with c3:
        btn_custom = st.button("🔍 Analisa Input", use_container_width=True)
    with c4:
        btn_top20 = st.button("🔥 Top 20 Volume", use_container_width=True)
    with c5:
        # Tombol Clear (Hapus) yang sekaligus mereset DB
        if st.button("🗑️ Hapus List", use_container_width=True):
            st.session_state.vol_saved_tickers = []
            save_data()
            st.rerun() # RERUN AGAR LANGSUNG HILANG (Fix Double Click)

    df_vol_result = pd.DataFrame()

    # 2. LOGIC
    if btn_custom and vol_input:
        raw_list = vol_input.replace('\n', ',').replace(' ', ',').split(',')
        clean_list = []
        for t in raw_list:
            item = t.strip().upper()
            if item:
                if len(item) == 4 and item.isalpha(): item += ".JK"
                clean_list.append(item)
        if clean_list:
            # SAVE TO DB (Persistence)
            st.session_state.vol_saved_tickers = list(set(clean_list))
            save_data()
            
            with st.spinner("Menganalisa input..."):
                df_vol_result = get_stock_volume_stats(list(set(clean_list)), period_code=selected_vol_period)
                st.session_state['vol_result'] = df_vol_result 
                st.rerun() # RERUN AGAR UPDATE UI

    elif btn_top20:
        with st.spinner("Scanning Top 20 Volume..."):
            df_all = get_stock_volume_stats(GRID_TICKERS, period_code=selected_vol_period)
            if df_all is not None and not df_all.empty:
                df_vol_result = df_all.sort_values(by="Volume", ascending=False).head(20)
                st.session_state['vol_result'] = df_vol_result

    # 3. DISPLAY
    if 'vol_result' in st.session_state and not st.session_state['vol_result'].empty:
        df_show = st.session_state['vol_result']
        st.divider()
        st.subheader(f"Hasil Analisa Volume ({vol_period})")
        
        sort_col = st.radio("Urutkan berdasarkan:", ["Volume", "Est. Value", "Vol vs Avg"], horizontal=True)
        if sort_col == "Volume": df_show = df_show.sort_values(by="Volume", ascending=False)
        elif sort_col == "Est. Value": df_show = df_show.sort_values(by="Est. Value", ascending=False)
        elif sort_col == "Vol vs Avg": df_show = df_show.sort_values(by="Vol vs Avg", ascending=False)
        
        def highlight_vol_spike(val):
            color = '#d4f7d4' if val >= 1.5 else ''
            return f'background-color: {color}'
            
        st.dataframe(df_show.style.format({
                "Price": "{:,.0f}",
                "Change %": "{:+.2f}%",
                "Volume": "{:,.0f}", 
                "Avg Vol (5D)": "{:,.0f}", 
                "Est. Value": "Rp {:,.0f}", 
                "Vol vs Avg": "{:.2f}x"
            }).applymap(highlight_vol_spike, subset=['Vol vs Avg']), use_container_width=True, hide_index=True)

with tab_watch:
    st.header("Watchlist Saya")
    ci, cb = st.columns([3, 1])
    with ci: nt = st.text_input("Kode:", key="sb").strip().upper()
    with cb: 
        st.write(""); st.write("")
        if st.button("➕ Tambah"): 
            if nt and nt not in st.session_state.watchlist: st.session_state.watchlist.append(nt); save_data(); st.rerun()
    cw = st.session_state.watchlist
    if cw:
        if st.button("🗑️ Hapus Semua"): st.session_state.watchlist = []; save_data(); st.rerun()
        ew = st.multiselect("Edit:", options=cw, default=cw)
        if len(ew) != len(cw): st.session_state.watchlist = ew; save_data(); st.rerun()
        with st.spinner("Load..."):
            dw = get_stock_history_bulk(cw)
            if not dw.empty: 
                w_cols = st.columns(4)
                for i, ticker in enumerate(cw):
                    with w_cols[i % 4]:
                        try:
                            df = pd.DataFrame()
                            if isinstance(dw.columns, pd.MultiIndex):
                                if ticker in dw.columns.levels[0]: df = dw[ticker].copy()
                            else:
                                if len(cw) == 1: df = dw.copy()
                            
                            if not df.empty:
                                df = df.dropna()
                                fig = create_mini_chart(df, ticker, "3mo")
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        except: pass

with tab_detail:
    st.header("🔎 Analisa Saham Mendalam")
    col_search, col_period = st.columns([2, 3])
    with col_search:
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input("Ketik Kode Saham:", value=default_ticker, key="detail_input").strip().upper()
    with col_period:
        period_options = ["1d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        period_labels = {"1d": "1 Hari", "1mo": "1 Bulan", "3mo": "3 Bulan", "6mo": "6 Bulan", "1y": "1 Tahun", "2y": "2 Tahun", "5y": "5 Tahun", "max": "Sejak IPO"}
        selected_period_code = st.select_slider("Pilih Rentang Waktu:", options=period_options, value="1y", format_func=lambda x: period_labels[x])
    st.divider()
    if detail_ticker:
        with st.spinner(f"Mengambil data {detail_ticker}..."):
            df_detail = get_single_stock_detail(detail_ticker, selected_period_code)
            fund_info = get_fundamental_info(detail_ticker)
            if df_detail is not None and not df_detail.empty:
                last_row = df_detail.iloc[-1]
                prev_row = df_detail.iloc[-2] if len(df_detail) > 1 else last_row
                change = last_row['Close'] - prev_row['Close']
                pct_change = (change / prev_row['Close']) * 100
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Harga", f"{last_row['Close']:,.0f}", f"{pct_change:.2f}%")
                m2.metric("Volume", f"{last_row['Volume']:,.0f}")
                m3.metric("High", f"{df_detail['High'].max():,.0f}")
                if fund_info:
                    m4.metric("Market Cap", f"{fund_info['mkt_cap']:,.0f}" if fund_info['mkt_cap'] else "-")
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("PER (TTM)", f"{fund_info['per']:.2f}x" if fund_info['per'] else "-")
                    f2.metric("PBV", f"{fund_info['pbv']:.2f}x" if fund_info['pbv'] else "-")
                    f3.metric("EPS (TTM)", f"{fund_info['eps']:.2f}" if fund_info['eps'] else "-")
                    f4.metric("Industri", fund_info['sector'])
                q_fin, a_fin = get_financials_history(detail_ticker)
                is_long_term = selected_period_code in ["2y", "5y", "max"]
                df_fin_use = a_fin if is_long_term and not a_fin.empty else q_fin
                if df_fin_use.empty: df_fin_use = q_fin if not q_fin.empty else a_fin
                start_date_chart = df_detail['Date'].min()
                if not df_fin_use.empty: df_fin_filtered = df_fin_use[df_fin_use.index >= start_date_chart]
                else: df_fin_filtered = pd.DataFrame()
                st.plotly_chart(create_detail_chart(df_detail, detail_ticker, df_fin_filtered), use_container_width=True)
            else: st.error("Data tidak ditemukan.")

with tab_cycle:
    st.header("🔄 Cycle Analysis")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        def_t = ", ".join(st.session_state.watchlist[:2]) if st.session_state.watchlist else "GOTO.JK, BBCA.JK"
        cycle_tickers = st.text_input("Saham:", value=def_t, key="cycle_in").strip().upper()
    with c2:
        month_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"Mei", 6:"Jun", 7:"Jul", 8:"Agust", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Des"}
        start_m = st.selectbox("Dari:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=10) 
        end_m = st.selectbox("Sampai:", options=list(month_map.keys()), format_func=lambda x: month_map[x], index=3)
    with c3:
        years_lookback = st.slider("Tahun:", 3, 10, 5)
        st.write(""); 
        if st.button("🚀 Bandingkan", key="btn_cycle"):
            with st.spinner("Menganalisa..."):
                st.session_state['cycle_data'] = get_seasonal_details(cycle_tickers, start_m, end_m, years_lookback)
    st.divider()
    if 'cycle_data' in st.session_state and st.session_state['cycle_data']:
        results_dict = st.session_state['cycle_data']
        if results_dict:
            cols = st.columns(2)
            for idx, (ticker, years_data) in enumerate(results_dict.items()):
                with cols[idx % 2]:
                    fig = go.Figure()
                    sorted_years = sorted(years_data.keys(), reverse=True)
                    my_colors = ['black', 'blue', 'red', 'green'] 
                    for i, year_label in enumerate(sorted_years):
                        series = years_data[year_label]
                        chosen_color = my_colors[i % len(my_colors)]
                        is_current = str(datetime.now().year) in year_label
                        width = 3 if is_current else 1.5
                        fig.add_trace(go.Scatter(y=series, mode='lines', name=year_label, line=dict(width=width, color=chosen_color)))
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                    fig.update_layout(title=f"<b>{ticker}</b>", xaxis_title="Hari", yaxis_title="Gain/Loss (%)", hovermode="x unified", height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else: st.warning("Data tidak cukup.")

with tab_fund:
    st.header("💎 Fundamental & Classification Screener")
    default_txt = ", ".join(SAMPLE_SCREENER_TICKERS)
    user_screener_input = st.text_area("Input Saham (Pisahkan koma):", value=default_txt, height=100)
    col_run, col_export = st.columns([1, 5])
    with col_run: 
        if st.button("🔍 Scan Fundamental", key="btn_fund"):
            tickers_to_scan = [t.strip().upper() for t in user_screener_input.split(',') if t.strip()]
            st.write(f"Sedang mengambil data fundamental untuk {len(tickers_to_scan)} saham...")
            st.session_state['fund_data'] = get_fundamental_screener(tickers_to_scan)
    st.divider()
    if 'fund_data' in st.session_state and not st.session_state['fund_data'].empty:
        df_fund = st.session_state['fund_data']
        unique_industries = df_fund["Industry"].unique()
        for industry in sorted(unique_industries):
            df_sub = df_fund[df_fund["Industry"] == industry].copy().drop(columns=["Industry"])
            st.subheader(f"🏭 {industry}")
            st.dataframe(df_sub, use_container_width=True, hide_index=True, column_config={
                    "Price": st.column_config.NumberColumn("Price", format="Rp %.0f"),
                    "52W High": st.column_config.NumberColumn("52W High", format="Rp %.0f"),
                    "52W Low": st.column_config.NumberColumn("52W Low", format="Rp %.0f"),
                    "PBV": st.column_config.NumberColumn("PBV", format="%.2fx"),
                    "PER": st.column_config.NumberColumn("PER", format="%.2fx"),
                    "EPS": st.column_config.NumberColumn("EPS", format="%.2f")})
            st.write("")

with tab_perf:
    st.header("🚀 Tabel Performa Saham")
    st.write("Data menggunakan **Raw Price** & **Calendar Slicing**. Menampilkan Industri.")
    def_perf = ", ".join(st.session_state.watchlist) if st.session_state.watchlist else "ADRO.JK\nBBCA.JK\nBBRI.JK\nGOTO.JK"
    perf_tickers_input = st.text_area("Input Saham:", value=def_perf, height=100, key="perf_in_main")
    if st.button("Hitung Performa", key="btn_perf"):
        with st.spinner("Mengambil Data & Metadata..."):
            st.session_state['perf_data'] = get_performance_matrix(perf_tickers_input)
    if 'perf_data' in st.session_state and not st.session_state['perf_data'].empty:
        df_perf = st.session_state['perf_data']
        pct_fmt = st.column_config.NumberColumn(format="%.2f%%")
        def color_negative_red(val):
            if val is None or pd.isna(val): return 'color: gray'
            color = '#00C805' if val > 0 else '#FF333A' if val < 0 else 'black'
            return f'color: {color}; font-weight: bold'
        styled_df = df_perf.style.format({
            "1 Hari": "{:.2f}", "1 Minggu": "{:.2f}", "1 Bulan": "{:.2f}",
            "6 Bulan": "{:.2f}", "YTD": "{:.2f}", "1 Tahun": "{:.2f}", "3 Tahun": "{:.2f}"
        }).applymap(color_negative_red, subset=["1 Hari", "1 Minggu", "1 Bulan", "6 Bulan", "YTD", "1 Tahun", "3 Tahun"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config={
                "Ticker": st.column_config.TextColumn("Kode"),
                "Industri": st.column_config.TextColumn("Industri"), 
                "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                "1 Hari": pct_fmt, "1 Minggu": pct_fmt, "1 Bulan": pct_fmt,
                "6 Bulan": pct_fmt, "YTD": pct_fmt, "1 Tahun": pct_fmt, "3 Tahun": pct_fmt})

with tab_win:
    st.header("🎲 Probabilitas Harian (30 Hari Terakhir)")
    st.write("Analisis jumlah hari Hijau vs Merah untuk menentukan tren dan probabilitas.")
    win_input = st.text_area("Input Saham:", value=def_perf, height=100, key="win_in")
    
    if st.button("Hitung Probabilitas", key="btn_win"):
        with st.spinner("Menganalisis data harian..."):
            summary_df, detail_dict = get_win_loss_details(win_input)
            st.session_state['win_summary'] = summary_df
            st.session_state['win_details'] = detail_dict
            
    if 'win_summary' in st.session_state and not st.session_state['win_summary'].empty:
        st.subheader("Rangkuman Statistik")
        df_win = st.session_state['win_summary']
        def highlight_win(val):
            color = '#d4f7d4' if val >= 60 else '#f7d4d4' if val <= 40 else ''
            return f'background-color: {color}'
        st.dataframe(df_win.style.format({
                "Win Rate": "{:.1f}%", "Rata2 Naik": "+{:.2f}%", "Rata2 Turun": "{:.2f}%", "Total Return (30 Candle)": "{:.2f}%"
            }).applymap(highlight_win, subset=['Win Rate']), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🗓️ Detail Pergerakan Harian (Grid 30 Hari)")
        
        detail_data = st.session_state['win_details']
        
        st.markdown("""
        <style>
        .day-box {
            display: inline-block; width: 70px; height: 70px; margin: 4px; padding: 8px 2px;
            border-radius: 8px; text-align: center; color: white; font-family: sans-serif;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }
        .day-date { font-size: 10px; margin-bottom: 4px; opacity: 0.9; font-weight: bold; }
        .day-val { font-size: 13px; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

        for ticker, df_30 in detail_data.items():
            with st.expander(f"📊 {ticker} - Detail 30 Hari", expanded=True):
                html_code = "<div style='display: flex; flex-wrap: wrap;'>"
                for date, row in df_30.iterrows():
                    val = row['Change']
                    color = "#00C805" if val >= 0 else "#FF333A"
                    date_str = date.strftime("%d %b")
                    val_str = f"{val:+.2f}%"
                    html_code += f"<div class='day-box' style='background-color: {color};'><div class='day-date'>{date_str}</div><div class='day-val'>{val_str}</div></div>"
                html_code += "</div>"
                st.markdown(html_code, unsafe_allow_html=True)

