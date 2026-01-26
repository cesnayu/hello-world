import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Super Stock Dashboard")

# --- 2. INISIALISASI SESSION STATE (PENTING UNTUK BOOKMARK) ---
if 'watchlist' not in st.session_state:
    # Default watchlist awal (bisa kosong [])
    st.session_state.watchlist = ["BBCA.JK", "GOTO.JK", "BBRI.JK"]

# --- 3. DATA MAPPING (SEKTOR) ---
SECTOR_MAP = {
    "Banking (Finance)": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BBTN.JK", "ARTO.JK"],
    "Energy & Mining": ["ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "MDKA.JK", "ANTM.JK", "INCO.JK", "BUMI.JK"],
    "Telco & Tech": ["TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK", "BUKA.JK", "EMTK.JK"],
    "Consumer Goods": ["ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "GGRM.JK", "HMSP.JK", "KLBF.JK"],
    "Infrastructure & Auto": ["ASII.JK", "JSMR.JK", "UNTR.JK", "SMGR.JK", "INTP.JK"]
}

# --- 4. FUNGSI LOAD DATA (CACHED) ---

@st.cache_data(ttl=600)
def get_stock_history_bulk(tickers, period="3mo"):
    """Mengambil history harga untuk Grid Chart."""
    if not tickers:
        return pd.DataFrame()
    # Download data
    data = yf.download(tickers, period=period, group_by='ticker', progress=False)
    return data

@st.cache_data(ttl=300)
def get_stock_volume_stats(tickers_str):
    """Mengambil data volume & value transaksi."""
    if not tickers_str: return None
    
    ticker_list = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not ticker_list: return None

    data = yf.download(ticker_list, period="1mo", group_by='ticker', progress=False)
    
    stats = []
    for t in ticker_list:
        try:
            if len(ticker_list) == 1:
                df = data
                symbol = ticker_list[0]
            else:
                df = data[t]
                symbol = t
            
            if df.empty: continue
            
            last_vol = df['Volume'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            avg_vol_1w = df['Volume'].tail(5).mean()
            txn_value = last_close * last_vol 
            
            stats.append({
                "Ticker": symbol,
                "Last Close": last_close,
                "Volume (Hari Ini)": last_vol,
                "Avg Volume (1 Week)": avg_vol_1w,
                "Est. Value (IDR)": txn_value
            })
        except Exception:
            continue
            
    return pd.DataFrame(stats)

@st.cache_data(ttl=600)
def get_sector_performance(sector_name):
    """Hitung gain sektor."""
    tickers = SECTOR_MAP.get(sector_name, [])
    if not tickers: return pd.DataFrame()
    
    data = yf.download(tickers, period="3mo", group_by='ticker', progress=False)
    
    perf_list = []
    for t in tickers:
        try:
            df = data[t] if len(tickers) > 1 else data
            if df.empty: continue
            df = df.sort_index()
            curr = df['Close'].iloc[-1]
            
            def calc_pct(days_ago):
                if len(df) > days_ago:
                    prev = df['Close'].iloc[-(days_ago+1)]
                    return ((curr - prev) / prev) * 100
                return 0.0

            perf_list.append({
                "Ticker": t,
                "Price": curr,
                "1D %": calc_pct(1),
                "1W %": calc_pct(5),
                "1M %": calc_pct(20)
            })
        except Exception:
            continue
    return pd.DataFrame(perf_list)

# --- 5. FUNGSI VISUALISASI GRID (DIGUNAKAN DI TAB 1 & 4) ---
def create_stock_grid(tickers, chart_data):
    if not tickers: return None
    
    rows = math.ceil(len(tickers) / 4)
    
    # Logic Spacing Dinamis
    if rows > 1:
        calc_spacing = 0.2 / (rows - 1)
        vertical_spacing = min(0.08, calc_spacing)
    else:
        vertical_spacing = 0.1
    
    fig = make_subplots(
        rows=rows, cols=4, 
        subplot_titles=tickers,
        vertical_spacing=vertical_spacing,
        horizontal_spacing=0.03
    )

    one_month_ago = datetime.now() - timedelta(days=30)

    for i, ticker in enumerate(tickers):
        row = (i // 4) + 1
        col = (i % 4) + 1

        try:
            df = chart_data[ticker] if len(tickers) > 1 else chart_data
        except KeyError: continue

        if df.empty or 'Close' not in df.columns: continue
        df = df.dropna()
        if len(df) < 2: continue

        # Warna Chart
        last_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        color = '#00C805' if float(last_p) >= float(prev_p) else '#FF333A'

        fig.add_trace(
            go.Scatter(x=df.index, y=df['Close'], mode='lines',
                       line=dict(color=color, width=1.5), name=ticker),
            row=row, col=col
        )
        
        # Garis 1 Bulan Lalu
        fig.add_vline(x=one_month_ago.timestamp() * 1000, 
                      line_width=1, line_dash="dot", line_color="blue", row=row, col=col)
        
        fig.update_xaxes(showticklabels=False, row=row, col=col)
        fig.update_yaxes(showticklabels=False, row=row, col=col)

    fig.update_layout(height=max(300, rows * 180), showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# --- 6. MAIN UI & TABS ---
st.title("📈 All-in-One Stock Dashboard")

# List Default untuk Tab Grid
default_tickers = [
    "AALI.JK","ABBA.JK","ABDA.JK","ABMM.JK","ACES.JK","ACST.JK","ADES.JK","ADHI.JK","ADMF.JK","ADMG.JK","ADRO.JK","AGII.JK","AGRO.JK","AGRS.JK","AHAP.JK","AIMS.JK","AISA.JK","AKKU.JK","AKPI.JK","AKRA.JK","AKSI.JK","ALDO.JK","ALKA.JK","ALMI.JK","ALTO.JK","AMAG.JK","AMFG.JK","AMIN.JK","AMRT.JK","ANJT.JK","ANTM.JK","APEX.JK","APIC.JK","APII.JK","APLI.JK","APLN.JK","ARGO.JK","ARII.JK","ARNA.JK","ARTA.JK","ARTI.JK","ARTO.JK","ASBI.JK","ASDM.JK","ASGR.JK","ASII.JK","ASJT.JK","ASMI.JK","ASRI.JK","ASRM.JK","ASSA.JK","ATIC.JK","AUTO.JK","BABP.JK","BACA.JK","BAJA.JK","BALI.JK","BAPA.JK","BATA.JK","BAYU.JK","BBCA.JK","BBHI.JK","BBKP.JK","BBLD.JK","BBMD.JK","BBNI.JK","BBRI.JK","BBRM.JK","BBTN.JK","BBYB.JK","BCAP.JK","BCIC.JK","BCIP.JK","BDMN.JK","BEKS.JK","BEST.JK","BFIN.JK","BGTG.JK","BHIT.JK","BIKA.JK","BIMA.JK","BINA.JK","BIPI.JK","BIPP.JK","BIRD.JK","BISI.JK","BJBR.JK","BJTM.JK","BKDP.JK","BKSL.JK","BKSW.JK","BLTA.JK","BLTZ.JK","BMAS.JK","BMRI.JK","BMSR.JK","BMTR.JK","BNBA.JK","BNBR.JK","BNGA.JK","BNII.JK","BNLI.JK","BOLT.JK","BPFI.JK","BPII.JK","BRAM.JK","BRMS.JK","BRNA.JK","BRPT.JK","BSDE.JK","BSIM.JK","BSSR.JK","BSWD.JK","BTEK.JK","BTEL.JK","BTON.JK","BTPN.JK","BUDI.JK","BUKK.JK","BULL.JK","BUMI.JK","BUVA.JK","BVIC.JK","BWPT.JK","BYAN.JK","CANI.JK","CASS.JK","CEKA.JK","CENT.JK","CFIN.JK","CINT.JK","CITA.JK","CLPI.JK","CMNP.JK","CMPP.JK","CNKO.JK","CNTX.JK","COWL.JK","CPIN.JK","CPRO.JK","CSAP.JK","CTBN.JK","CTRA.JK","CTTH.JK","DART.JK","DEFI.JK","DEWA.JK","DGIK.JK","DILD.JK","DKFT.JK","DLTA.JK","DMAS.JK","DNAR.JK","DNET.JK","DOID.JK","DPNS.JK","DSFI.JK","DSNG.JK","DSSA.JK","DUTI.JK","DVLA.JK","DYAN.JK","ECII.JK","EKAD.JK","ELSA.JK","ELTY.JK","EMDE.JK","EMTK.JK","ENRG.JK","EPMT.JK","ERAA.JK","ERTX.JK","ESSA.JK","ESTI.JK","ETWA.JK","EXCL.JK","FAST.JK","FASW.JK","FISH.JK","FMII.JK","FORU.JK","FPNI.JK","GAMA.JK","GDST.JK","GDYR.JK","GEMA.JK","GEMS.JK","GGRM.JK","GIAA.JK","GJTL.JK","GLOB.JK","GMTD.JK","GOLD.JK","GOLL.JK","GPRA.JK","GSMF.JK","GTBO.JK","GWSA.JK","GZCO.JK","HADE.JK","HDFA.JK","HERO.JK","HEXA.JK","HITS.JK","HMSP.JK","HOME.JK","HOTL.JK","HRUM.JK","IATA.JK","IBFN.JK","IBST.JK","ICBP.JK","ICON.JK","IGAR.JK","IIKP.JK","IKAI.JK","IKBI.JK","IMAS.JK","IMJS.JK","IMPC.JK","INAF.JK","INAI.JK","INCI.JK","INCO.JK","INDF.JK","INDR.JK","INDS.JK","INDX.JK","INDY.JK","INKP.JK","INPC.JK","INPP.JK","INRU.JK","INTA.JK","INTD.JK","INTP.JK","IPOL.JK","ISAT.JK","ISSP.JK","ITMA.JK","ITMG.JK","JAWA.JK","JECC.JK","JIHD.JK","JKON.JK","JPFA.JK","JRPT.JK","JSMR.JK","JSPT.JK","JTPE.JK","KAEF.JK","KARW.JK","KBLI.JK","KBLM.JK","KBLV.JK","KBRI.JK","KDSI.JK","KIAS.JK","KICI.JK","KIJA.JK","KKGI.JK","KLBF.JK","KOBX.JK","KOIN.JK","KONI.JK","KOPI.JK","KPIG.JK","KRAS.JK","KREN.JK","LAPD.JK","LCGP.JK","LEAD.JK","LINK.JK","LION.JK","LMAS.JK","LMPI.JK","LMSH.JK","LPCK.JK","LPGI.JK","LPIN.JK","LPKR.JK","LPLI.JK","LPPF.JK","LPPS.JK","LRNA.JK","LSIP.JK","LTLS.JK","MAGP.JK","MAIN.JK","MAPI.JK","MAYA.JK","MBAP.JK","MBSS.JK","MBTO.JK","MCOR.JK","MDIA.JK","MDKA.JK","MDLN.JK","MDRN.JK","MEDC.JK","MEGA.JK","MERK.JK","META.JK","MFMI.JK","MGNA.JK","MICE.JK","MIDI.JK","MIKA.JK","MIRA.JK","MITI.JK","MKPI.JK","MLBI.JK","MLIA.JK","MLPL.JK","MLPT.JK","MMLP.JK","MNCN.JK","MPMX.JK","MPPA.JK","MRAT.JK","MREI.JK","MSKY.JK","MTDL.JK","MTFN.JK","MTLA.JK","MTSM.JK","MYOH.JK","MYOR.JK","MYTX.JK","NELY.JK","NIKL.JK","NIRO.JK","NISP.JK","NOBU.JK","NRCA.JK","OCAP.JK","OKAS.JK","OMRE.JK","PADI.JK","PALM.JK","PANR.JK","PANS.JK","PBRX.JK","PDES.JK","PEGE.JK","PGAS.JK","PGLI.JK","PICO.JK","PJAA.JK","PKPK.JK","PLAS.JK","PLIN.JK","PNBN.JK","PNBS.JK","PNIN.JK","PNLF.JK","PNSE.JK","POLY.JK","POOL.JK","PPRO.JK","PSAB.JK","PSDN.JK","PSKT.JK","PTBA.JK","PTIS.JK","PTPP.JK","PTRO.JK","PTSN.JK","PTSP.JK","PUDP.JK","PWON.JK","PYFA.JK","RAJA.JK","RALS.JK","RANC.JK","RBMS.JK","RDTX.JK","RELI.JK","RICY.JK","RIGS.JK","RIMO.JK","RODA.JK","ROTI.JK","RUIS.JK","SAFE.JK","SAME.JK","SCCO.JK","SCMA.JK","SCPI.JK","SDMU.JK","SDPC.JK","SDRA.JK","SGRO.JK","SHID.JK","SIDO.JK","SILO.JK","SIMA.JK","SIMP.JK","SIPD.JK","SKBM.JK","SKLT.JK","SKYB.JK","SMAR.JK","SMBR.JK","SMCB.JK","SMDM.JK","SMDR.JK","SMGR.JK","SMMA.JK","SMMT.JK","SMRA.JK","SMRU.JK","SMSM.JK","SOCI.JK","SONA.JK","SPMA.JK","SQMI.JK","SRAJ.JK","SRIL.JK","SRSN.JK","SRTG.JK","SSIA.JK","SSMS.JK","SSTM.JK","STAR.JK","STTP.JK","SUGI.JK","SULI.JK","SUPR.JK","TALF.JK","TARA.JK","TAXI.JK","TBIG.JK","TBLA.JK","TBMS.JK","TCID.JK","TELE.JK","TFCO.JK","TGKA.JK","TIFA.JK","TINS.JK","TIRA.JK","TIRT.JK","TKIM.JK","TLKM.JK","TMAS.JK","TMPO.JK","TOBA.JK","TOTL.JK","TOTO.JK","TOWR.JK","TPIA.JK","TPMA.JK","TRAM.JK","TRIL.JK","TRIM.JK","TRIO.JK","TRIS.JK","TRST.JK","TRUS.JK","TSPC.JK","ULTJ.JK","UNIC.JK","UNIT.JK","UNSP.JK","UNTR.JK","UNVR.JK","VICO.JK","VINS.JK","VIVA.JK","VOKS.JK","VRNA.JK","WAPO.JK","WEHA.JK","WICO.JK","WIIM.JK","WIKA.JK","WINS.JK","WOMF.JK","WSKT.JK","WTON.JK","YPAS.JK","YULE.JK","ZBRA.JK","SHIP.JK","CASA.JK","DAYA.JK","DPUM.JK","IDPR.JK","JGLE.JK","KINO.JK","MARI.JK","MKNT.JK","MTRA.JK","OASA.JK","POWR.JK","INCF.JK","WSBP.JK","PBSA.JK","PRDA.JK","BOGA.JK","BRIS.JK","PORT.JK","CARS.JK","MINA.JK","CLEO.JK","TAMU.JK","CSIS.JK","TGRA.JK","FIRE.JK","TOPS.JK","KMTR.JK","ARMY.JK","MAPB.JK","WOOD.JK","HRTA.JK","MABA.JK","HOKI.JK","MPOW.JK","MARK.JK","NASA.JK","MDKI.JK","BELL.JK","KIOS.JK","GMFI.JK","MTWI.JK","ZINC.JK","MCAS.JK","PPRE.JK","WEGE.JK","PSSI.JK","MORA.JK","DWGL.JK","PBID.JK","JMAS.JK","CAMP.JK","IPCM.JK","PCAR.JK","LCKM.JK","BOSS.JK","HELI.JK","JSKY.JK","INPS.JK","GHON.JK","TDPM.JK","DFAM.JK","NICK.JK","BTPS.JK","SPTO.JK","PRIM.JK","HEAL.JK","TRUK.JK","PZZA.JK","TUGU.JK","MSIN.JK","SWAT.JK","TNCA.JK","MAPA.JK","TCPI.JK","IPCC.JK","RISE.JK","BPTR.JK","POLL.JK","NFCX.JK","MGRO.JK","NUSA.JK","FILM.JK","ANDI.JK","LAND.JK","MOLI.JK","PANI.JK","DIGI.JK","CITY.JK","SAPX.JK","SURE.JK","HKMU.JK","MPRO.JK","DUCK.JK","GOOD.JK","SKRN.JK","YELO.JK","CAKK.JK","SATU.JK","SOSS.JK","DEAL.JK","POLA.JK","DIVA.JK","LUCK.JK","URBN.JK","SOTS.JK","ZONE.JK","PEHA.JK","FOOD.JK","BEEF.JK","POLI.JK","CLAY.JK","NATO.JK","JAYA.JK","COCO.JK","MTPS.JK","CPRI.JK","HRME.JK","POSA.JK","JAST.JK","FITT.JK","BOLA.JK","CCSI.JK","SFAN.JK","POLU.JK","KJEN.JK","KAYU.JK","ITIC.JK","PAMG.JK","IPTV.JK","BLUE.JK","ENVY.JK","EAST.JK","LIFE.JK","FUJI.JK","KOTA.JK","INOV.JK","ARKA.JK","SMKL.JK","HDIT.JK","KEEN.JK","BAPI.JK","TFAS.JK","GGRP.JK","OPMS.JK","NZIA.JK","SLIS.JK","PURE.JK","IRRA.JK","DMMX.JK","SINI.JK","WOWS.JK","ESIP.JK","TEBE.JK","KEJU.JK","PSGO.JK","AGAR.JK","IFSH.JK","REAL.JK","IFII.JK","PMJS.JK","UCID.JK","GLVA.JK","PGJO.JK","AMAR.JK","CSRA.JK","INDO.JK","AMOR.JK","TRIN.JK","DMND.JK","PURA.JK","PTPW.JK","TAMA.JK","IKAN.JK","SAMF.JK","SBAT.JK","KBAG.JK","CBMF.JK","RONY.JK","CSMI.JK","BBSS.JK","BHAT.JK","CASH.JK","TECH.JK","EPAC.JK","UANG.JK","PGUN.JK","SOFA.JK","PPGL.JK","TOYS.JK","SGER.JK","TRJA.JK","PNGO.JK","SCNP.JK","BBSI.JK","KMDS.JK","PURI.JK","SOHO.JK","HOMI.JK","ROCK.JK","ENZO.JK","PLAN.JK","PTDU.JK","ATAP.JK","VICI.JK","PMMP.JK","BANK.JK","WMUU.JK","EDGE.JK","UNIQ.JK","BEBS.JK","SNLK.JK","ZYRX.JK","LFLO.JK","FIMP.JK","TAPG.JK","NPGF.JK","LUCY.JK","ADCP.JK","HOPE.JK","MGLV.JK","TRUE.JK","LABA.JK","ARCI.JK","IPAC.JK","MASB.JK","BMHS.JK","FLMC.JK","NICL.JK","UVCR.JK","BUKA.JK","HAIS.JK","OILS.JK","GPSO.JK","MCOL.JK","RSGK.JK","RUNS.JK","SBMA.JK","CMNT.JK","GTSI.JK","IDEA.JK","KUAS.JK","BOBA.JK","MTEL.JK","DEPO.JK","BINO.JK","CMRY.JK","WGSH.JK","TAYS.JK","WMPP.JK","RMKE.JK","OBMD.JK","AVIA.JK","IPPE.JK","NASI.JK","BSML.JK","DRMA.JK","ADMR.JK","SEMA.JK","ASLC.JK","NETV.JK","BAUT.JK","ENAK.JK","NTBK.JK","SMKM.JK","STAA.JK","NANO.JK","BIKE.JK","WIRG.JK","SICO.JK","GOTO.JK","TLDN.JK","MTMH.JK","WINR.JK","IBOS.JK","OLIV.JK","ASHA.JK","SWID.JK","TRGU.JK","ARKO.JK","CHEM.JK","DEWI.JK","AXIO.JK","KRYA.JK","HATM.JK","RCCC.JK","GULA.JK","JARR.JK","AMMS.JK","RAFI.JK","KKES.JK","ELPI.JK","EURO.JK","KLIN.JK","TOOL.JK","BUAH.JK","CRAB.JK","MEDS.JK","COAL.JK","PRAY.JK","CBUT.JK","BELI.JK","MKTR.JK","OMED.JK","BSBK.JK","PDPP.JK","KDTN.JK","ZATA.JK","NINE.JK","MMIX.JK","PADA.JK","ISAP.JK","VTNY.JK","SOUL.JK","ELIT.JK","BEER.JK","CBPE.JK","SUNI.JK","CBRE.JK","WINE.JK","BMBL.JK","PEVE.JK","LAJU.JK","FWCT.JK","NAYZ.JK","IRSX.JK","PACK.JK","VAST.JK","CHIP.JK","HALO.JK","KING.JK","PGEO.JK","FUTR.JK","HILL.JK","BDKR.JK","PTMP.JK","SAGE.JK","TRON.JK","CUAN.JK","NSSS.JK","GTRA.JK","HAJJ.JK","JATI.JK","TYRE.JK","MPXL.JK","SMIL.JK","KLAS.JK","MAXI.JK","VKTR.JK","RELF.JK","AMMN.JK","CRSN.JK","GRPM.JK","WIDI.JK","TGUK.JK","INET.JK","MAHA.JK","RMKO.JK","CNMA.JK","FOLK.JK","HBAT.JK","GRIA.JK","PPRI.JK","ERAL.JK","CYBR.JK","MUTU.JK","LMAX.JK","HUMI.JK","MSIE.JK","RSCH.JK","BABY.JK","AEGS.JK","IOTF.JK","KOCI.JK","PTPS.JK","BREN.JK","STRK.JK","KOKA.JK","LOPI.JK","UDNG.JK","RGAS.JK","MSTI.JK","IKPM.JK","AYAM.JK","SURI.JK","ASLI.JK","GRPH.JK","SMGA.JK","UNTD.JK","TOSK.JK","MPIX.JK","ALII.JK","MKAP.JK","MEJA.JK","LIVE.JK","HYGN.JK","BAIK.JK","VISI.JK","AREA.JK","MHKI.JK","ATLA.JK","DATA.JK","SOLA.JK","BATR.JK","SPRE.JK","PART.JK","GOLF.JK","ISEA.JK","BLES.JK","GUNA.JK","LABS.JK","DOSS.JK","NEST.JK","PTMR.JK","VERN.JK","DAAZ.JK","BOAT.JK","NAIK.JK","AADI.JK","MDIY.JK","KSIX.JK","RATU.JK","YOII.JK","HGII.JK","BRRC.JK","DGWG.JK","CBDK.JK","OBAT.JK","MINE.JK","ASPR.JK","PSAT.JK","COIN.JK","CDIA.JK","BLOG.JK","MERI.JK","CHEK.JK","PMUI.JK","EMAS.JK","PJHB.JK","KAQI.JK","YUPI.JK","FORE.JK","MDLA.JK","DKHH.JK","AYLS.JK","DADA.JK","ASPI.JK","ESTA.JK","BESS.JK","AMAN.JK","CARE.JK","PIPA.JK","NCKL.JK","MENN.JK","AWAN.JK","MBMA.JK","RAAM.JK","DOOH.JK","CGAS.JK","NICE.JK","MSJA.JK","SMLE.JK","ACRO.JK","MANG.JK","WIFI.JK","FAPA.JK","DCII.JK","KETR.JK","DGNS.JK","UFOE.JK",
    # Tambah sampai 100 ticker
] 

# UPDATE TABS: Tab 4 diganti Search & Watchlist
tab_grid, tab_vol, tab_sector, tab_search = st.tabs([
    "📊 Chart Grid", 
    "🔊 Top Volume", 
    "🏢 Sector Gain", 
    "🔍 Search & Watchlist"
])

# === TAB 1: CHART GRID (PAGINATION) ===
with tab_grid:
    st.write("Grid Overview (All Stocks)")
    if 'page' not in st.session_state: st.session_state.page = 1
    items_per_page = 20
    total_pages = math.ceil(len(default_tickers) / items_per_page)
    
    c1, _ = st.columns([1, 5])
    curr_page = c1.number_input("Halaman", 1, total_pages, key="grid_page")
    
    start = (curr_page - 1) * items_per_page
    end = start + items_per_page
    batch = default_tickers[start:end]

    with st.spinner("Memuat grafik..."):
        data_grid = get_stock_history_bulk(batch)
        if not data_grid.empty:
            fig_main = create_stock_grid(batch, data_grid)
            if fig_main:
                st.plotly_chart(fig_main, use_container_width=True)

# === TAB 2: TOP VOLUME (BOOKMARKABLE) ===
with tab_vol:
    st.header("Analisis Volume & Likuiditas")
    
    # 1. Tentukan Default List (Saham bawaan saat Reset)
    DEFAULT_VOL_LIST = ["GOTO.JK", "BBRI.JK", "BUMI.JK", "ANTM.JK", "DEWA.JK"]

    # 2. Inisialisasi Session State khusus Volume
    if 'vol_watchlist' not in st.session_state:
        st.session_state.vol_watchlist = DEFAULT_VOL_LIST

    # 3. UI: Input Tambah & Tombol Reset
    col_input, col_add, col_reset = st.columns([3, 1, 1])
    
    with col_input:
        new_vol_ticker = st.text_input("Tambah Saham ke Analisa Volume:", placeholder="Contoh: ADRO.JK", key="vol_add_input").strip().upper()
    
    with col_add:
        st.write("") # Spacer layout
        st.write("")
        if st.button("➕ Tambah", key="btn_add_vol"):
            if new_vol_ticker and new_vol_ticker not in st.session_state.vol_watchlist:
                st.session_state.vol_watchlist.append(new_vol_ticker)
                st.rerun()
            elif new_vol_ticker in st.session_state.vol_watchlist:
                st.warning("Saham sudah ada di list.")

    with col_reset:
        st.write("") # Spacer layout
        st.write("")
        if st.button("🔄 Reset Awal", key="btn_reset_vol"):
            st.session_state.vol_watchlist = DEFAULT_VOL_LIST # Kembalikan ke default
            st.rerun()

    # 4. Tampilkan List Saham yang Sedang Dianalisa (Bisa dihapus user)
    st.caption("Daftar saham yang dianalisa saat ini:")
    
    # Tampilkan sebagai chips/multiselect agar user bisa hapus jika mau
    edited_vol_list = st.multiselect(
        "Edit List:",
        options=st.session_state.vol_watchlist,
        default=st.session_state.vol_watchlist,
        key="vol_multiselect_editor",
        label_visibility="collapsed"
    )
    
    # Update session state jika user menghapus lewat multiselect
    if len(edited_vol_list) != len(st.session_state.vol_watchlist):
        st.session_state.vol_watchlist = edited_vol_list
        st.rerun()

    st.divider()

    # 5. Proses Data
    # Kita gabungkan list menjadi string koma (karena fungsi get_stock_volume_stats butuh string)
    current_vol_str = ", ".join(st.session_state.vol_watchlist)
    
    if current_vol_str:
        with st.spinner("Mengambil data volume..."):
            df_vol = get_stock_volume_stats(current_vol_str)
            
            if df_vol is not None and not df_vol.empty:
                # Opsi Sorting
                sort_col = st.radio("Urutkan Berdasarkan:", 
                                    ["Volume (Hari Ini)", "Avg Volume (1 Week)", "Est. Value (IDR)"], 
                                    horizontal=True)
                
                # Sorting Numerik
                df_sorted = df_vol.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
                
                st.dataframe(
                    df_sorted.style.format({
                        "Last Close": "{:,.0f}",
                        "Volume (Hari Ini)": "{:,.0f}",
                        "Avg Volume (1 Week)": "{:,.0f}",
                        "Est. Value (IDR)": "Rp {:,.0f}"
                    }), use_container_width=True
                )
            else:
                st.warning("Data tidak ditemukan untuk saham yang diinput.")
    else:
        st.info("List kosong. Silakan tambahkan saham atau klik Reset.")

# === TAB 3: SECTOR GAIN ===
with tab_sector:
    st.header("Performa Sektoral")
    chosen_sector = st.selectbox("Pilih Sektor:", list(SECTOR_MAP.keys()))
    
    if chosen_sector:
        with st.spinner("Analisa sektor..."):
            df_sec = get_sector_performance(chosen_sector)
            if not df_sec.empty:
                def color_scale(val):
                    color = '#d4f7d4' if val > 0 else '#f7d4d4' if val < 0 else ''
                    return f'background-color: {color}'

                st.dataframe(
                    df_sec.style.applymap(color_scale, subset=['1D %', '1W %', '1M %'])
                                .format({"Price": "{:,.0f}", "1D %": "{:+.2f}%", "1W %": "{:+.2f}%", "1M %": "{:+.2f}%"}),
                    use_container_width=True
                )

# === TAB 4: SEARCH & WATCHLIST (FIXED BULK PASTE) ===
with tab_search:
    st.header("🔍 Pencarian & Watchlist Saya")
    st.write("Cari saham dan tambahkan ke daftar pantauan. Bisa input satu atau banyak sekaligus (pisahkan koma).")

    # 1. INPUT SECTION
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        # Gunakan text_area agar lebih enak kalau paste list panjang
        new_ticker_input = st.text_area("Ketik/Paste Kode Saham (contoh: UNTR.JK, AAPL, BBCA.JK)", height=68, key="search_box")
    with col_btn:
        st.write("") # Spacer agar tombol sejajar
        st.write("")
        add_btn = st.button("➕ Tambahkan ke Watchlist")

    # Logic Tambah Saham (SUDAH DIPERBAIKI UNTUK BULK)
    if add_btn and new_ticker_input:
        # Langkah 1: Pecah text berdasarkan koma
        # Langkah 2: Bersihkan spasi dan ubah ke huruf besar
        tickers_to_process = [t.strip().upper() for t in new_ticker_input.split(',') if t.strip()]
        
        count_added = 0
        
        for ticker in tickers_to_process:
            # Cek duplikasi sebelum append
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                count_added += 1
        
        if count_added > 0:
            st.success(f"Berhasil menambahkan {count_added} saham baru!")
            st.rerun() # Refresh halaman agar grid update
        else:
            st.warning("Semua saham yang diinput sudah ada di watchlist kamu.")

    st.divider()

    # 2. DISPLAY WATCHLIST SECTION
    current_watchlist = st.session_state.watchlist

    if not current_watchlist:
        st.info("Watchlist kamu masih kosong. Silakan tambahkan saham di atas.")
    else:
        # Tombol Hapus / Reset
        if st.button("🗑️ Hapus Semua Watchlist"):
            st.session_state.watchlist = []
            st.rerun()
        
        st.subheader(f"Daftar Pantauan ({len(current_watchlist)} Saham)")
        
        # Menggunakan Fungsi Grid yang SAMA dengan Tab 1
        with st.spinner("Memuat grafik watchlist..."):
            data_watch = get_stock_history_bulk(current_watchlist)
            
            if not data_watch.empty:
                fig_watch = create_stock_grid(current_watchlist, data_watch)
                if fig_watch:
                    st.plotly_chart(fig_watch, use_container_width=True)
            else:
                st.error("Gagal mengambil data. Pastikan kode saham benar (contoh: BBCA.JK untuk Indonesia).")
# === TAB 5: ANALISA DETAIL (NEW FEATURE) ===
with tab_detail:
    st.header("🔎 Analisa Saham Mendalam")
    st.write("Lihat grafik lengkap dengan candlestick, volume, dan rentang waktu bebas.")
    
    # 1. Kontrol Input (Ticker & Timeframe)
    col_search, col_period = st.columns([2, 3])
    
    with col_search:
        # Default value ambil dari watchlist pertama kalau ada
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input("Ketik Kode Saham:", value=default_ticker, key="detail_input").strip().upper()
        
    with col_period:
        # Pilihan Rentang Waktu
        period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        # Label yang lebih manusiawi
        period_labels = {"1mo": "1 Bulan", "3mo": "3 Bulan", "6mo": "6 Bulan", "1y": "1 Tahun", "2y": "2 Tahun", "5y": "5 Tahun", "max": "Sejak IPO"}
        
        selected_period_code = st.select_slider(
            "Pilih Rentang Waktu:",
            options=period_options,
            value="1y", # Default 1 tahun
            format_func=lambda x: period_labels[x]
        )

    st.divider()

    # 2. Render Chart
    if detail_ticker:
        with st.spinner(f"Mengambil data {detail_ticker} ({period_labels[selected_period_code]})..."):
            
            # Panggil fungsi baru get_single_stock_detail
            df_detail = get_single_stock_detail(detail_ticker, selected_period_code)
            
            if df_detail is not None and not df_detail.empty:
                # Tampilkan Chart Candlestick
                fig_detail = create_detail_chart(df_detail, detail_ticker)
                st.plotly_chart(fig_detail, use_container_width=True)
                
                # Tampilkan Data Statistik Singkat
                last_row = df_detail.iloc[-1]
                prev_row = df_detail.iloc[-2] if len(df_detail) > 1 else last_row
                change = last_row['Close'] - prev_row['Close']
                pct_change = (change / prev_row['Close']) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Harga Terakhir", f"{last_row['Close']:,.0f}")
                col2.metric("Perubahan", f"{change:,.0f}", f"{pct_change:.2f}%")
                col3.metric("Volume", f"{last_row['Volume']:,.0f}")
                col4.metric("Tertinggi (Periode Ini)", f"{df_detail['High'].max():,.0f}")
                
            else:
                st.error(f"Data tidak ditemukan untuk {detail_ticker}. Pastikan kode benar (tambah .JK untuk Indonesia).")
