import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="IHSG Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Daftar saham IHSG
STOCK_LIST = [
    "AALI.JK","ABBA.JK","ABDA.JK","ABMM.JK","ACES.JK","ACST.JK","ADES.JK","ADHI.JK","ADMF.JK","ADMG.JK","ADRO.JK","AGII.JK","AGRO.JK","AGRS.JK","AHAP.JK","AIMS.JK","AISA.JK","AKKU.JK","AKPI.JK","AKRA.JK","AKSI.JK","ALDO.JK","ALKA.JK","ALMI.JK","ALTO.JK","AMAG.JK","AMFG.JK","AMIN.JK","AMRT.JK","ANJT.JK","ANTM.JK","APEX.JK","APIC.JK","APII.JK","APLI.JK","APLN.JK","ARGO.JK","ARII.JK","ARNA.JK","ARTA.JK","ARTI.JK","ARTO.JK","ASBI.JK","ASDM.JK","ASGR.JK","ASII.JK","ASJT.JK","ASMI.JK","ASRI.JK","ASRM.JK","ASSA.JK","ATIC.JK","AUTO.JK","BABP.JK","BACA.JK","BAJA.JK","BALI.JK","BAPA.JK","BATA.JK","BAYU.JK","BBCA.JK","BBHI.JK","BBKP.JK","BBLD.JK","BBMD.JK","BBNI.JK","BBRI.JK","BBRM.JK","BBTN.JK","BBYB.JK","BCAP.JK","BCIC.JK","BCIP.JK","BDMN.JK","BEKS.JK","BEST.JK","BFIN.JK","BGTG.JK","BHIT.JK","BIKA.JK","BIMA.JK","BINA.JK","BIPI.JK","BIPP.JK","BIRD.JK","BISI.JK","BJBR.JK","BJTM.JK","BKDP.JK","BKSL.JK","BKSW.JK","BLTA.JK","BLTZ.JK","BMAS.JK","BMRI.JK","BMSR.JK","BMTR.JK","BNBA.JK","BNBR.JK","BNGA.JK","BNII.JK","BNLI.JK","BOLT.JK","BPFI.JK","BPII.JK","BRAM.JK","BRMS.JK","BRNA.JK","BRPT.JK","BSDE.JK","BSIM.JK","BSSR.JK","BSWD.JK","BTEK.JK","BTEL.JK","BTON.JK","BTPN.JK","BUDI.JK","BUKK.JK","BULL.JK","BUMI.JK","BUVA.JK","BVIC.JK","BWPT.JK","BYAN.JK","CANI.JK","CASS.JK","CEKA.JK","CENT.JK","CFIN.JK","CINT.JK","CITA.JK","CLPI.JK","CMNP.JK","CMPP.JK","CNKO.JK","CNTX.JK","COWL.JK","CPIN.JK","CPRO.JK","CSAP.JK","CTBN.JK","CTRA.JK","CTTH.JK","DART.JK","DEFI.JK","DEWA.JK","DGIK.JK","DILD.JK","DKFT.JK","DLTA.JK","DMAS.JK","DNAR.JK","DNET.JK","DOID.JK","DPNS.JK","DSFI.JK","DSNG.JK","DSSA.JK","DUTI.JK","DVLA.JK","DYAN.JK","ECII.JK","EKAD.JK","ELSA.JK","ELTY.JK","EMDE.JK","EMTK.JK","ENRG.JK","EPMT.JK","ERAA.JK","ERTX.JK","ESSA.JK","ESTI.JK","ETWA.JK","EXCL.JK","FAST.JK","FASW.JK","FISH.JK","FMII.JK","FORU.JK","FPNI.JK","GAMA.JK","GDST.JK","GDYR.JK","GEMA.JK","GEMS.JK","GGRM.JK","GIAA.JK","GJTL.JK","GLOB.JK","GMTD.JK","GOLD.JK","GOLL.JK","GPRA.JK","GSMF.JK","GTBO.JK","GWSA.JK","GZCO.JK","HADE.JK","HDFA.JK","HERO.JK","HEXA.JK","HITS.JK","HMSP.JK","HOME.JK","HOTL.JK","HRUM.JK","IATA.JK","IBFN.JK","IBST.JK","ICBP.JK","ICON.JK","IGAR.JK","IIKP.JK","IKAI.JK","IKBI.JK","IMAS.JK","IMJS.JK","IMPC.JK","INAF.JK","INAI.JK","INCI.JK","INCO.JK","INDF.JK","INDR.JK","INDS.JK","INDX.JK","INDY.JK","INKP.JK","INPC.JK","INPP.JK","INRU.JK","INTA.JK","INTD.JK","INTP.JK","IPOL.JK","ISAT.JK","ISSP.JK","ITMA.JK","ITMG.JK","JAWA.JK","JECC.JK","JIHD.JK","JKON.JK","JPFA.JK","JRPT.JK","JSMR.JK","JSPT.JK","JTPE.JK","KAEF.JK","KARW.JK","KBLI.JK","KBLM.JK","KBLV.JK","KBRI.JK","KDSI.JK","KIAS.JK","KICI.JK","KIJA.JK","KKGI.JK","KLBF.JK","KOBX.JK","KOIN.JK","KONI.JK","KOPI.JK","KPIG.JK","KRAS.JK","KREN.JK","LAPD.JK","LCGP.JK","LEAD.JK","LINK.JK","LION.JK","LMAS.JK","LMPI.JK","LMSH.JK","LPCK.JK","LPGI.JK","LPIN.JK","LPKR.JK","LPLI.JK","LPPF.JK","LPPS.JK","LRNA.JK","LSIP.JK","LTLS.JK","MAGP.JK","MAIN.JK","MAPI.JK","MAYA.JK","MBAP.JK","MBSS.JK","MBTO.JK","MCOR.JK","MDIA.JK","MDKA.JK","MDLN.JK","MDRN.JK","MEDC.JK","MEGA.JK","MERK.JK","META.JK","MFMI.JK","MGNA.JK","MICE.JK","MIDI.JK","MIKA.JK","MIRA.JK","MITI.JK","MKPI.JK","MLBI.JK","MLIA.JK","MLPL.JK","MLPT.JK","MMLP.JK","MNCN.JK","MPMX.JK","MPPA.JK","MRAT.JK","MREI.JK","MSKY.JK","MTDL.JK","MTFN.JK","MTLA.JK","MTSM.JK","MYOH.JK","MYOR.JK","MYTX.JK","NELY.JK","NIKL.JK","NIRO.JK","NISP.JK","NOBU.JK","NRCA.JK","OCAP.JK","OKAS.JK","OMRE.JK","PADI.JK","PALM.JK","PANR.JK","PANS.JK","PBRX.JK","PDES.JK","PEGE.JK","PGAS.JK","PGLI.JK","PICO.JK","PJAA.JK","PKPK.JK","PLAS.JK","PLIN.JK","PNBN.JK","PNBS.JK","PNIN.JK","PNLF.JK","PNSE.JK","POLY.JK","POOL.JK","PPRO.JK","PSAB.JK","PSDN.JK","PSKT.JK","PTBA.JK","PTIS.JK","PTPP.JK","PTRO.JK","PTSN.JK","PTSP.JK","PUDP.JK","PWON.JK","PYFA.JK","RAJA.JK","RALS.JK","RANC.JK","RBMS.JK","RDTX.JK","RELI.JK","RICY.JK","RIGS.JK","RIMO.JK","RODA.JK","ROTI.JK","RUIS.JK","SAFE.JK","SAME.JK","SCCO.JK","SCMA.JK","SCPI.JK","SDMU.JK","SDPC.JK","SDRA.JK","SGRO.JK","SHID.JK","SIDO.JK","SILO.JK","SIMA.JK","SIMP.JK","SIPD.JK","SKBM.JK","SKLT.JK","SKYB.JK","SMAR.JK","SMBR.JK","SMCB.JK","SMDM.JK","SMDR.JK","SMGR.JK","SMMA.JK","SMMT.JK","SMRA.JK","SMRU.JK","SMSM.JK","SOCI.JK","SONA.JK","SPMA.JK","SQMI.JK","SRAJ.JK","SRIL.JK","SRSN.JK","SRTG.JK","SSIA.JK","SSMS.JK","SSTM.JK","STAR.JK","STTP.JK","SUGI.JK","SULI.JK","SUPR.JK","TALF.JK","TARA.JK","TAXI.JK","TBIG.JK","TBLA.JK","TBMS.JK","TCID.JK","TELE.JK","TFCO.JK","TGKA.JK","TIFA.JK","TINS.JK","TIRA.JK","TIRT.JK","TKIM.JK","TLKM.JK","TMAS.JK","TMPO.JK","TOBA.JK","TOTL.JK","TOTO.JK","TOWR.JK","TPIA.JK","TPMA.JK","TRAM.JK","TRIL.JK","TRIM.JK","TRIO.JK","TRIS.JK","TRST.JK","TRUS.JK","TSPC.JK","ULTJ.JK","UNIC.JK","UNIT.JK","UNSP.JK","UNTR.JK","UNVR.JK","VICO.JK","VINS.JK","VIVA.JK","VOKS.JK","VRNA.JK","WAPO.JK","WEHA.JK","WICO.JK","WIIM.JK","WIKA.JK","WINS.JK","WOMF.JK","WSKT.JK","WTON.JK","YPAS.JK","YULE.JK","ZBRA.JK","SHIP.JK","CASA.JK","DAYA.JK","DPUM.JK","IDPR.JK","JGLE.JK","KINO.JK","MARI.JK","MKNT.JK","MTRA.JK","OASA.JK","POWR.JK","INCF.JK","WSBP.JK","PBSA.JK","PRDA.JK","BOGA.JK","BRIS.JK","PORT.JK","CARS.JK","MINA.JK","CLEO.JK","TAMU.JK","CSIS.JK","TGRA.JK","FIRE.JK","TOPS.JK","KMTR.JK","ARMY.JK","MAPB.JK","WOOD.JK","HRTA.JK","MABA.JK","HOKI.JK","MPOW.JK","MARK.JK","NASA.JK","MDKI.JK","BELL.JK","KIOS.JK","GMFI.JK","MTWI.JK","ZINC.JK","MCAS.JK","PPRE.JK","WEGE.JK","PSSI.JK","MORA.JK","DWGL.JK","PBID.JK","JMAS.JK","CAMP.JK","IPCM.JK","PCAR.JK","LCKM.JK","BOSS.JK","HELI.JK","JSKY.JK","INPS.JK","GHON.JK","TDPM.JK","DFAM.JK","NICK.JK","BTPS.JK","SPTO.JK","PRIM.JK","HEAL.JK","TRUK.JK","PZZA.JK","TUGU.JK","MSIN.JK","SWAT.JK","TNCA.JK","MAPA.JK","TCPI.JK","IPCC.JK","RISE.JK","BPTR.JK","POLL.JK","NFCX.JK","MGRO.JK","NUSA.JK","FILM.JK","ANDI.JK","LAND.JK","MOLI.JK","PANI.JK","DIGI.JK","CITY.JK","SAPX.JK","SURE.JK","HKMU.JK","MPRO.JK","DUCK.JK","GOOD.JK","SKRN.JK","YELO.JK","CAKK.JK","SATU.JK","SOSS.JK","DEAL.JK","POLA.JK","DIVA.JK","LUCK.JK","URBN.JK","SOTS.JK","ZONE.JK","PEHA.JK","FOOD.JK","BEEF.JK","POLI.JK","CLAY.JK","NATO.JK","JAYA.JK","COCO.JK","MTPS.JK","CPRI.JK","HRME.JK","POSA.JK","JAST.JK","FITT.JK","BOLA.JK","CCSI.JK","SFAN.JK","POLU.JK","KJEN.JK","KAYU.JK","ITIC.JK","PAMG.JK","IPTV.JK","BLUE.JK","ENVY.JK","EAST.JK","LIFE.JK","FUJI.JK","KOTA.JK","INOV.JK","ARKA.JK","SMKL.JK","HDIT.JK","KEEN.JK","BAPI.JK","TFAS.JK","GGRP.JK","OPMS.JK","NZIA.JK","SLIS.JK","PURE.JK","IRRA.JK","DMMX.JK","SINI.JK","WOWS.JK","ESIP.JK","TEBE.JK","KEJU.JK","PSGO.JK","AGAR.JK","IFSH.JK","REAL.JK","IFII.JK","PMJS.JK","UCID.JK","GLVA.JK","PGJO.JK","AMAR.JK","CSRA.JK","INDO.JK","AMOR.JK","TRIN.JK","DMND.JK","PURA.JK","PTPW.JK","TAMA.JK","IKAN.JK","SAMF.JK","SBAT.JK","KBAG.JK","CBMF.JK","RONY.JK","CSMI.JK","BBSS.JK","BHAT.JK","CASH.JK","TECH.JK","EPAC.JK","UANG.JK","PGUN.JK","SOFA.JK","PPGL.JK","TOYS.JK","SGER.JK","TRJA.JK","PNGO.JK","SCNP.JK","BBSI.JK","KMDS.JK","PURI.JK","SOHO.JK","HOMI.JK","ROCK.JK","ENZO.JK","PLAN.JK","PTDU.JK","ATAP.JK","VICI.JK","PMMP.JK","BANK.JK","WMUU.JK","EDGE.JK","UNIQ.JK","BEBS.JK","SNLK.JK","ZYRX.JK","LFLO.JK","FIMP.JK","TAPG.JK","NPGF.JK","LUCY.JK","ADCP.JK","HOPE.JK","MGLV.JK","TRUE.JK","LABA.JK","ARCI.JK","IPAC.JK","MASB.JK","BMHS.JK","FLMC.JK","NICL.JK","UVCR.JK","BUKA.JK","HAIS.JK","OILS.JK","GPSO.JK","MCOL.JK","RSGK.JK","RUNS.JK","SBMA.JK","CMNT.JK","GTSI.JK","IDEA.JK","KUAS.JK","BOBA.JK","MTEL.JK","DEPO.JK","BINO.JK","CMRY.JK","WGSH.JK","TAYS.JK","WMPP.JK","RMKE.JK","OBMD.JK","AVIA.JK","IPPE.JK","NASI.JK","BSML.JK","DRMA.JK","ADMR.JK","SEMA.JK","ASLC.JK","NETV.JK","BAUT.JK","ENAK.JK","NTBK.JK","SMKM.JK","STAA.JK","NANO.JK","BIKE.JK","WIRG.JK","SICO.JK","GOTO.JK","TLDN.JK","MTMH.JK","WINR.JK","IBOS.JK","OLIV.JK","ASHA.JK","SWID.JK","TRGU.JK","ARKO.JK","CHEM.JK","DEWI.JK","AXIO.JK","KRYA.JK","HATM.JK","RCCC.JK","GULA.JK","JARR.JK","AMMS.JK","RAFI.JK","KKES.JK","ELPI.JK","EURO.JK","KLIN.JK","TOOL.JK","BUAH.JK","CRAB.JK","MEDS.JK","COAL.JK","PRAY.JK","CBUT.JK","BELI.JK","MKTR.JK","OMED.JK","BSBK.JK","PDPP.JK","KDTN.JK","ZATA.JK","NINE.JK","MMIX.JK","PADA.JK","ISAP.JK","VTNY.JK","SOUL.JK","ELIT.JK","BEER.JK","CBPE.JK","SUNI.JK","CBRE.JK","WINE.JK","BMBL.JK","PEVE.JK","LAJU.JK","FWCT.JK","NAYZ.JK","IRSX.JK","PACK.JK","VAST.JK","CHIP.JK","HALO.JK","KING.JK","PGEO.JK","FUTR.JK","HILL.JK","BDKR.JK","PTMP.JK","SAGE.JK","TRON.JK","CUAN.JK","NSSS.JK","GTRA.JK","HAJJ.JK","JATI.JK","TYRE.JK","MPXL.JK","SMIL.JK","KLAS.JK","MAXI.JK","VKTR.JK","RELF.JK","AMMN.JK","CRSN.JK","GRPM.JK","WIDI.JK","TGUK.JK","INET.JK","MAHA.JK","RMKO.JK","CNMA.JK","FOLK.JK","HBAT.JK","GRIA.JK","PPRI.JK","ERAL.JK","CYBR.JK","MUTU.JK","LMAX.JK","HUMI.JK","MSIE.JK","RSCH.JK","BABY.JK","AEGS.JK","IOTF.JK","KOCI.JK","PTPS.JK","BREN.JK","STRK.JK","KOKA.JK","LOPI.JK","UDNG.JK","RGAS.JK","MSTI.JK","IKPM.JK","AYAM.JK","SURI.JK","ASLI.JK","GRPH.JK","SMGA.JK","UNTD.JK","TOSK.JK","MPIX.JK","ALII.JK","MKAP.JK","MEJA.JK","LIVE.JK","HYGN.JK","BAIK.JK","VISI.JK","AREA.JK","MHKI.JK","ATLA.JK","DATA.JK","SOLA.JK","BATR.JK","SPRE.JK","PART.JK","GOLF.JK","ISEA.JK","BLES.JK","GUNA.JK","LABS.JK","DOSS.JK","NEST.JK","PTMR.JK","VERN.JK","DAAZ.JK","BOAT.JK","NAIK.JK","AADI.JK","MDIY.JK","KSIX.JK","RATU.JK","YOII.JK","HGII.JK","BRRC.JK","DGWG.JK","CBDK.JK","OBAT.JK","MINE.JK","ASPR.JK","PSAT.JK","COIN.JK","CDIA.JK","BLOG.JK","MERI.JK","CHEK.JK","PMUI.JK","EMAS.JK","PJHB.JK","KAQI.JK","YUPI.JK","FORE.JK","MDLA.JK","DKHH.JK","AYLS.JK","DADA.JK","ASPI.JK","ESTA.JK","BESS.JK","AMAN.JK","CARE.JK","PIPA.JK","NCKL.JK","MENN.JK","AWAN.JK","MBMA.JK","RAAM.JK","DOOH.JK","CGAS.JK","NICE.JK","MSJA.JK","SMLE.JK","ACRO.JK","MANG.JK","WIFI.JK","FAPA.JK","DCII.JK","KETR.JK","DGNS.JK","UFOE.JK",
    # Tambah sampai 100 ticker
]

# Initialize session state for watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

@st.cache_data(ttl=3600)
def get_stock_data(ticker, period='3mo'):
    """Ambil data saham dari Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return None

@st.cache_data(ttl=3600)
def calculate_performance(stock_list):
    """Hitung performa saham untuk berbagai periode"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(stock_list):
        try:
            status_text.text(f"Mengambil data {ticker}... ({idx+1}/{len(stock_list)})")
            data = get_stock_data(ticker, period='3mo')
            
            if data is None or len(data) < 2:
                continue
            
            current_price = data['Close'].iloc[-1]
            volume_today = data['Volume'].iloc[-1]
            volume_week = data['Volume'].tail(5).mean() if len(data) >= 5 else volume_today
            
            day_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) >= 2 else 0
            week_change = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100 if len(data) >= 6 else 0
            month_change = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100 if len(data) >= 21 else 0
            month3_change = ((current_price - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100 if len(data) >= 60 else 0
            
            results.append({
                'Ticker': ticker.replace('.JK', ''),
                'TickerFull': ticker,
                'Harga': current_price,
                'Volume': volume_today,
                'Volume Week': volume_week,
                'Hari Ini': day_change,
                '1 Minggu': week_change,
                '1 Bulan': month_change,
                '3 Bulan': month3_change,
                'Data': data
            })
            
            progress_bar.progress((idx + 1) / len(stock_list))
            
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def create_price_chart_with_1month_line(data, ticker, change_pct):
    """Buat grafik harga dengan garis 1 bulan"""
    color = 'green' if change_pct > 0 else 'red'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=ticker,
        line=dict(color=color, width=2)
    ))
    
    # Garis 1 bulan
    if len(data) >= 21:
        one_month_ago = data.index[-21]
        fig.add_vline(
            x=one_month_ago,
            line_dash="dash",
            line_color="blue",
            annotation_text="1 bulan lalu",
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f"{ticker} - Rp {data['Close'].iloc[-1]:,.0f}",
        xaxis_title="Tanggal",
        yaxis_title="Harga",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_mini_charts(df, title):
    """Buat mini charts untuk top stocks"""
    n_stocks = min(len(df), 20)
    rows = (n_stocks + 3) // 4
    
    fig = make_subplots(
        rows=rows,
        cols=4,
        subplot_titles=[f"{row['Ticker']}" for _, row in df.head(n_stocks).iterrows()],
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    for idx, (_, row) in enumerate(df.head(n_stocks).iterrows()):
        r = (idx // 4) + 1
        c = (idx % 4) + 1
        
        data = row['Data']
        color = 'green' if row['Hari Ini'] > 0 else 'red'
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                line=dict(color=color, width=2),
                showlegend=False
            ),
            row=r, col=c
        )
        
        # Garis 1 bulan
        if len(data) >= 21:
            one_month_ago = data.index[-21]
            y_min = data['Close'].min()
            y_max = data['Close'].max()
            
            fig.add_trace(
                go.Scatter(
                    x=[one_month_ago, one_month_ago],
                    y=[y_min, y_max],
                    mode='lines',
                    line=dict(color='blue', width=1, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=r, col=c
            )
        
        fig.update_xaxes(showticklabels=False, row=r, col=c)
        fig.update_yaxes(title_text="", row=r, col=c)
    
    fig.update_layout(
        title_text=title,
        height=300 * rows,
        showlegend=False
    )
    
    return fig

# Main App
st.title("📊 Dashboard IHSG - Top Gainers & Losers")
st.markdown(f"*Terakhir diupdate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Edit Daftar Saham")
    st.markdown("Edit `STOCK_LIST` di kode untuk menambah/mengurangi saham")

# Load data
with st.spinner("Mengambil data dari Yahoo Finance..."):
    df_all = calculate_performance(STOCK_LIST)

if len(df_all) == 0:
    st.error("❌ Tidak ada data yang berhasil diambil!")
    st.stop()

st.success(f"✅ Berhasil mengambil data {len(df_all)} saham")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⭐ Watchlist Saya",
    "📈 Top Gainers", 
    "📉 Top Losers",
    "📊 Top Volume",
    "📅 5 Hari Terakhir"
])

# TAB 1: WATCHLIST
with tab1:
    st.header("⭐ Watchlist Saya")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search = st.text_input("🔍 Cari saham (contoh: BBCA, BBRI)", "")
        
        if search:
            filtered = df_all[df_all['Ticker'].str.contains(search.upper())]
            
            if len(filtered) > 0:
                st.markdown("**Hasil pencarian:**")
                for _, row in filtered.iterrows():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    with col_a:
                        st.write(f"**{row['Ticker']}** - Rp {row['Harga']:,.0f}")
                    with col_b:
                        change_color = "green" if row['Hari Ini'] > 0 else "red"
                        st.markdown(f":{change_color}[{row['Hari Ini']:+.2f}%]")
                    with col_c:
                        if row['Ticker'] in st.session_state.watchlist:
                            if st.button("⭐", key=f"remove_{row['Ticker']}"):
                                st.session_state.watchlist.remove(row['Ticker'])
                                st.rerun()
                        else:
                            if st.button("☆", key=f"add_{row['Ticker']}"):
                                st.session_state.watchlist.append(row['Ticker'])
                                st.rerun()
            else:
                st.info("Tidak ada saham yang cocok")
    
    with col2:
        st.markdown("**Saham di Watchlist:**")
        if st.session_state.watchlist:
            for ticker in st.session_state.watchlist:
                if st.button(f"❌ {ticker}", key=f"del_{ticker}", use_container_width=True):
                    st.session_state.watchlist.remove(ticker)
                    st.rerun()
        else:
            st.info("Belum ada saham di watchlist")
    
    st.markdown("---")
    
    # Display watchlist charts
    if st.session_state.watchlist:
        st.subheader("📊 Grafik Saham di Watchlist")
        
        for ticker in st.session_state.watchlist:
            stock_data = df_all[df_all['Ticker'] == ticker]
            if len(stock_data) > 0:
                row = stock_data.iloc[0]
                fig = create_price_chart_with_1month_line(row['Data'], row['Ticker'], row['Hari Ini'])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Gunakan search box di atas untuk mencari dan menambahkan saham ke watchlist")

# TAB 2: TOP GAINERS
with tab2:
    st.header("📈 Top 20 Gainers")
    
    period = st.radio(
        "Pilih periode:",
        ["Hari Ini", "1 Minggu", "1 Bulan", "3 Bulan"],
        horizontal=True,
        key="gainers_period"
    )
    
    period_map = {
        "Hari Ini": "Hari Ini",
        "1 Minggu": "1 Minggu",
        "1 Bulan": "1 Bulan",
        "3 Bulan": "3 Bulan"
    }
    
    df_gainers = df_all.nlargest(20, period_map[period]).reset_index(drop=True)
    
    # Tabel
    df_display = df_gainers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].copy()
    df_display['Harga'] = df_display['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    df_display['Hari Ini'] = df_display['Hari Ini'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Minggu'] = df_display['1 Minggu'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Bulan'] = df_display['1 Bulan'].apply(lambda x: f"{x:+.2f}%")
    df_display['3 Bulan'] = df_display['3 Bulan'].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )
    
    # Charts
    st.subheader(f"Grafik Top 20 Gainers - {period}")
    fig = create_mini_charts(df_gainers, f"Top 20 Gainers - {period} (Garis biru = 1 bulan lalu)")
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: TOP LOSERS
with tab3:
    st.header("📉 Top 20 Losers")
    
    period = st.radio(
        "Pilih periode:",
        ["Hari Ini", "1 Minggu", "1 Bulan", "3 Bulan"],
        horizontal=True,
        key="losers_period"
    )
    
    period_map = {
        "Hari Ini": "Hari Ini",
        "1 Minggu": "1 Minggu",
        "1 Bulan": "1 Bulan",
        "3 Bulan": "3 Bulan"
    }
    
    df_losers = df_all.nsmallest(20, period_map[period]).reset_index(drop=True)
    
    # Tabel
    df_display = df_losers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].copy()
    df_display['Harga'] = df_display['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    df_display['Hari Ini'] = df_display['Hari Ini'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Minggu'] = df_display['1 Minggu'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Bulan'] = df_display['1 Bulan'].apply(lambda x: f"{x:+.2f}%")
    df_display['3 Bulan'] = df_display['3 Bulan'].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )
    
    # Charts
    st.subheader(f"Grafik Top 20 Losers - {period}")
    fig = create_mini_charts(df_losers, f"Top 20 Losers - {period} (Garis biru = 1 bulan lalu)")
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: TOP VOLUME
with tab4:
    st.header("📊 Top 20 Volume")
    
    volume_type = st.radio(
        "Pilih tipe:",
        ["Hari Ini", "Rata-rata 1 Minggu"],
        horizontal=True,
        key="volume_type"
    )
    
    if volume_type == "Hari Ini":
        df_volume = df_all.nlargest(20, 'Volume').reset_index(drop=True)
        vol_col = 'Volume'
    else:
        df_volume = df_all.nlargest(20, 'Volume Week').reset_index(drop=True)
        vol_col = 'Volume Week'
    
    # Tabel
    df_display = df_volume[['Ticker', 'Harga', 'Volume', 'Volume Week', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].copy()
    df_display['Harga'] = df_display['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    df_display['Volume'] = df_display['Volume'].apply(lambda x: f"{int(x):,}")
    df_display['Volume Week'] = df_display['Volume Week'].apply(lambda x: f"{int(x):,}")
    df_display['Hari Ini'] = df_display['Hari Ini'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Minggu'] = df_display['1 Minggu'].apply(lambda x: f"{x:+.2f}%")
    df_display['1 Bulan'] = df_display['1 Bulan'].apply(lambda x: f"{x:+.2f}%")
    df_display['3 Bulan'] = df_display['3 Bulan'].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )

# TAB 5: 5 HARI TERAKHIR
with tab5:
    st.header("📅 Top 20 Gainers - 5 Hari Terakhir")
    
    with st.spinner("Menghitung data harian..."):
        daily_results = {}
        
        for ticker in STOCK_LIST:
            try:
                data = get_stock_data(ticker, period='1mo')
                if data is None or len(data) < 6:
                    continue
                
                recent_data = data.tail(6)
                
                for i in range(1, len(recent_data)):
                    date = recent_data.index[i].strftime('%Y-%m-%d')
                    price_prev = recent_data['Close'].iloc[i-1]
                    price_curr = recent_data['Close'].iloc[i]
                    change = ((price_curr - price_prev) / price_prev) * 100
                    
                    if date not in daily_results:
                        daily_results[date] = []
                    
                    daily_results[date].append({
                        'Ticker': ticker.replace('.JK', ''),
                        'Perubahan': change,
                        'Harga': price_curr
                    })
            except:
                continue
    
    dates = sorted(daily_results.keys(), reverse=True)[:5]
    
    for date in dates:
        st.subheader(f"📅 {date}")
        df_day = pd.DataFrame(daily_results[date])
        df_day = df_day.nlargest(20, 'Perubahan').reset_index(drop=True)
        df_day.index = df_day.index + 1
        
        df_display = df_day[['Ticker', 'Harga', 'Perubahan']].copy()
        df_display['Harga'] = df_display['Harga'].apply(lambda x: f"Rp {x:,.0f}")
        df_display['Perubahan'] = df_display['Perubahan'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(
            df_display,
            use_container_width=True
        )
        st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Cara Deploy ke Streamlit Cloud (Gratis):
1. Upload kode ini ke GitHub repository
2. Buka [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub dan pilih repo kamu
4. Deploy! Dashboard bisa diakses dari mana aja

### 📱 Akses dari HP:
- Setelah deploy, akan dapat link seperti: `https://username-app.streamlit.app`
- Bisa dibuka dari browser HP kapan aja
- Watchlist tersimpan selama session aktif
""")
