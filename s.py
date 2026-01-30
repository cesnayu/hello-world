import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Master Trader Dashboard", layout="wide")

# --- LIST SAHAM GLOBAL ---
ALL_TICKERS = [
    "AALI.JK","ABBA.JK","ABDA.JK","ABMM.JK","ACES.JK","ACST.JK","ADES.JK","ADHI.JK","ADMF.JK","ADMG.JK","ADRO.JK","AGII.JK","AGRO.JK","AGRS.JK","AHAP.JK","AIMS.JK","AISA.JK","AKKU.JK","AKPI.JK","AKRA.JK","AKSI.JK","ALDO.JK","ALKA.JK","ALMI.JK","ALTO.JK","AMAG.JK","AMFG.JK","AMIN.JK","AMRT.JK","ANJT.JK","ANTM.JK","APEX.JK","APIC.JK","APII.JK","APLI.JK","APLN.JK","ARGO.JK","ARII.JK","ARNA.JK","ARTA.JK","ARTI.JK","ARTO.JK","ASBI.JK","ASDM.JK","ASGR.JK","ASII.JK","ASJT.JK","ASMI.JK","ASRI.JK","ASRM.JK","ASSA.JK","ATIC.JK","AUTO.JK","BABP.JK","BACA.JK","BAJA.JK","BALI.JK","BAPA.JK","BATA.JK","BAYU.JK","BBCA.JK","BBHI.JK","BBKP.JK","BBLD.JK","BBMD.JK","BBNI.JK","BBRI.JK","BBRM.JK","BBTN.JK","BBYB.JK","BCAP.JK","BCIC.JK","BCIP.JK","BDMN.JK","BEKS.JK","BEST.JK","BFIN.JK","BGTG.JK","BHIT.JK","BIKA.JK","BIMA.JK","BINA.JK","BIPI.JK","BIPP.JK","BIRD.JK","BISI.JK","BJBR.JK","BJTM.JK","BKDP.JK","BKSL.JK","BKSW.JK","BLTA.JK","BLTZ.JK","BMAS.JK","BMRI.JK","BMSR.JK","BMTR.JK","BNBA.JK","BNBR.JK","BNGA.JK","BNII.JK","BNLI.JK","BOLT.JK","BPFI.JK","BPII.JK","BRAM.JK","BRMS.JK","BRNA.JK","BRPT.JK","BSDE.JK","BSIM.JK","BSSR.JK","BSWD.JK","BTEK.JK","BTEL.JK","BTON.JK","BTPN.JK","BUDI.JK","BUKK.JK","BULL.JK","BUMI.JK","BUVA.JK","BVIC.JK","BWPT.JK","BYAN.JK","CANI.JK","CASS.JK","CEKA.JK","CENT.JK","CFIN.JK","CINT.JK","CITA.JK","CLPI.JK","CMNP.JK","CMPP.JK","CNKO.JK","CNTX.JK","COWL.JK","CPIN.JK","CPRO.JK","CSAP.JK","CTBN.JK","CTRA.JK","CTTH.JK","DART.JK","DEFI.JK","DEWA.JK","DGIK.JK","DILD.JK","DKFT.JK","DLTA.JK","DMAS.JK","DNAR.JK","DNET.JK","DOID.JK","DPNS.JK","DSFI.JK","DSNG.JK","DSSA.JK","DUTI.JK","DVLA.JK","DYAN.JK","ECII.JK","EKAD.JK","ELSA.JK","ELTY.JK","EMDE.JK","EMTK.JK","ENRG.JK","EPMT.JK","ERAA.JK","ERTX.JK","ESSA.JK","ESTI.JK","ETWA.JK","EXCL.JK","FAST.JK","FASW.JK","FISH.JK","FMII.JK","FORU.JK","FPNI.JK","GAMA.JK","GDST.JK","GDYR.JK","GEMA.JK","GEMS.JK","GGRM.JK","GIAA.JK","GJTL.JK","GLOB.JK","GMTD.JK","GOLD.JK","GOLL.JK","GPRA.JK","GSMF.JK","GTBO.JK","GWSA.JK","GZCO.JK","HADE.JK","HDFA.JK","HERO.JK","HEXA.JK","HITS.JK","HMSP.JK","HOME.JK","HOTL.JK","HRUM.JK","IATA.JK","IBFN.JK","IBST.JK","ICBP.JK","ICON.JK","IGAR.JK","IIKP.JK","IKAI.JK","IKBI.JK","IMAS.JK","IMJS.JK","IMPC.JK","INAF.JK","INAI.JK","INCI.JK","INCO.JK","INDF.JK","INDR.JK","INDS.JK","INDX.JK","INDY.JK","INKP.JK","INPC.JK","INPP.JK","INRU.JK","INTA.JK","INTD.JK","INTP.JK","IPOL.JK","ISAT.JK","ISSP.JK","ITMA.JK","ITMG.JK","JAWA.JK","JECC.JK","JIHD.JK","JKON.JK","JPFA.JK","JRPT.JK","JSMR.JK","JSPT.JK","JTPE.JK","KAEF.JK","KARW.JK","KBLI.JK","KBLM.JK","KBLV.JK","KBRI.JK","KDSI.JK","KIAS.JK","KICI.JK","KIJA.JK","KKGI.JK","KLBF.JK","KOBX.JK","KOIN.JK","KONI.JK","KOPI.JK","KPIG.JK","KRAS.JK","KREN.JK","LAPD.JK","LCGP.JK","LEAD.JK","LINK.JK","LION.JK","LMAS.JK","LMPI.JK","LMSH.JK","LPCK.JK","LPGI.JK","LPIN.JK","LPKR.JK","LPLI.JK","LPPF.JK","LPPS.JK","LRNA.JK","LSIP.JK","LTLS.JK","MAGP.JK","MAIN.JK","MAPI.JK","MAYA.JK","MBAP.JK","MBSS.JK","MBTO.JK","MCOR.JK","MDIA.JK","MDKA.JK","MDLN.JK","MDRN.JK","MEDC.JK","MEGA.JK","MERK.JK","META.JK","MFMI.JK","MGNA.JK","MICE.JK","MIDI.JK","MIKA.JK","MIRA.JK","MITI.JK","MKPI.JK","MLBI.JK","MLIA.JK","MLPL.JK","MLPT.JK","MMLP.JK","MNCN.JK","MPMX.JK","MPPA.JK","MRAT.JK","MREI.JK","MSKY.JK","MTDL.JK","MTFN.JK","MTLA.JK","MTSM.JK","MYOH.JK","MYOR.JK","MYTX.JK","NELY.JK","NIKL.JK","NIRO.JK","NISP.JK","NOBU.JK","NRCA.JK","OCAP.JK","OKAS.JK","OMRE.JK","PADI.JK","PALM.JK","PANR.JK","PANS.JK","PBRX.JK","PDES.JK","PEGE.JK","PGAS.JK","PGLI.JK","PICO.JK","PJAA.JK","PKPK.JK","PLAS.JK","PLIN.JK","PNBN.JK","PNBS.JK","PNIN.JK","PNLF.JK","PNSE.JK","POLY.JK","POOL.JK","PPRO.JK","PSAB.JK","PSDN.JK","PSKT.JK","PTBA.JK","PTIS.JK","PTPP.JK","PTRO.JK","PTSN.JK","PTSP.JK","PUDP.JK","PWON.JK","PYFA.JK","RAJA.JK","RALS.JK","RANC.JK","RBMS.JK","RDTX.JK","RELI.JK","RICY.JK","RIGS.JK","RIMO.JK","RODA.JK","ROTI.JK","RUIS.JK","SAFE.JK","SAME.JK","SCCO.JK","SCMA.JK","SCPI.JK","SDMU.JK","SDPC.JK","SDRA.JK","SGRO.JK","SHID.JK","SIDO.JK","SILO.JK","SIMA.JK","SIMP.JK","SIPD.JK","SKBM.JK","SKLT.JK","SKYB.JK","SMAR.JK","SMBR.JK","SMCB.JK","SMDM.JK","SMDR.JK","SMGR.JK","SMMA.JK","SMMT.JK","SMRA.JK","SMRU.JK","SMSM.JK","SOCI.JK","SONA.JK","SPMA.JK","SQMI.JK","SRAJ.JK","SRIL.JK","SRSN.JK","SRTG.JK","SSIA.JK","SSMS.JK","SSTM.JK","STAR.JK","STTP.JK","SUGI.JK","SULI.JK","SUPR.JK","TALF.JK","TARA.JK","TAXI.JK","TBIG.JK","TBLA.JK","TBMS.JK","TCID.JK","TELE.JK","TFCO.JK","TGKA.JK","TIFA.JK","TINS.JK","TIRA.JK","TIRT.JK","TKIM.JK","TLKM.JK","TMAS.JK","TMPO.JK","TOBA.JK","TOTL.JK","TOTO.JK","TOWR.JK","TPIA.JK","TPMA.JK","TRAM.JK","TRIL.JK","TRIM.JK","TRIO.JK","TRIS.JK","TRST.JK","TRUS.JK","TSPC.JK","ULTJ.JK","UNIC.JK","UNIT.JK","UNSP.JK","UNTR.JK","UNVR.JK","VICO.JK","VINS.JK","VIVA.JK","VOKS.JK","VRNA.JK","WAPO.JK","WEHA.JK","WICO.JK","WIIM.JK","WIKA.JK","WINS.JK","WOMF.JK","WSKT.JK","WTON.JK","YPAS.JK","YULE.JK","ZBRA.JK","SHIP.JK","CASA.JK","DAYA.JK","DPUM.JK","IDPR.JK","JGLE.JK","KINO.JK","MARI.JK","MKNT.JK","MTRA.JK","OASA.JK","POWR.JK","INCF.JK","WSBP.JK","PBSA.JK","PRDA.JK","BOGA.JK","BRIS.JK","PORT.JK","CARS.JK","MINA.JK","CLEO.JK","TAMU.JK","CSIS.JK","TGRA.JK","FIRE.JK","TOPS.JK","KMTR.JK","ARMY.JK","MAPB.JK","WOOD.JK","HRTA.JK","MABA.JK","HOKI.JK","MPOW.JK","MARK.JK","NASA.JK","MDKI.JK","BELL.JK","KIOS.JK","GMFI.JK","MTWI.JK","ZINC.JK","MCAS.JK","PPRE.JK","WEGE.JK","PSSI.JK","MORA.JK","DWGL.JK","PBID.JK","JMAS.JK","CAMP.JK","IPCM.JK","PCAR.JK","LCKM.JK","BOSS.JK","HELI.JK","JSKY.JK","INPS.JK","GHON.JK","TDPM.JK","DFAM.JK","NICK.JK","BTPS.JK","SPTO.JK","PRIM.JK","HEAL.JK","TRUK.JK","PZZA.JK","TUGU.JK","MSIN.JK","SWAT.JK","TNCA.JK","MAPA.JK","TCPI.JK","IPCC.JK","RISE.JK","BPTR.JK","POLL.JK","NFCX.JK","MGRO.JK","NUSA.JK","FILM.JK","ANDI.JK","LAND.JK","MOLI.JK","PANI.JK","DIGI.JK","CITY.JK","SAPX.JK","SURE.JK","HKMU.JK","MPRO.JK","DUCK.JK","GOOD.JK","SKRN.JK","YELO.JK","CAKK.JK","SATU.JK","SOSS.JK","DEAL.JK","POLA.JK","DIVA.JK","LUCK.JK","URBN.JK","SOTS.JK","ZONE.JK","PEHA.JK","FOOD.JK","BEEF.JK","POLI.JK","CLAY.JK","NATO.JK","JAYA.JK","COCO.JK","MTPS.JK","CPRI.JK","HRME.JK","POSA.JK","JAST.JK","FITT.JK","BOLA.JK","CCSI.JK","SFAN.JK","POLU.JK","KJEN.JK","KAYU.JK","ITIC.JK","PAMG.JK","IPTV.JK","BLUE.JK","ENVY.JK","EAST.JK","LIFE.JK","FUJI.JK","KOTA.JK","INOV.JK","ARKA.JK","SMKL.JK","HDIT.JK","KEEN.JK","BAPI.JK","TFAS.JK","GGRP.JK","OPMS.JK","NZIA.JK","SLIS.JK","PURE.JK","IRRA.JK","DMMX.JK","SINI.JK","WOWS.JK","ESIP.JK","TEBE.JK","KEJU.JK","PSGO.JK","AGAR.JK","IFSH.JK","REAL.JK","IFII.JK","PMJS.JK","UCID.JK","GLVA.JK","PGJO.JK","AMAR.JK","CSRA.JK","INDO.JK","AMOR.JK","TRIN.JK","DMND.JK","PURA.JK","PTPW.JK","TAMA.JK","IKAN.JK","SAMF.JK","SBAT.JK","KBAG.JK","CBMF.JK","RONY.JK","CSMI.JK","BBSS.JK","BHAT.JK","CASH.JK","TECH.JK","EPAC.JK","UANG.JK","PGUN.JK","SOFA.JK","PPGL.JK","TOYS.JK","SGER.JK","TRJA.JK","PNGO.JK","SCNP.JK","BBSI.JK","KMDS.JK","PURI.JK","SOHO.JK","HOMI.JK","ROCK.JK","ENZO.JK","PLAN.JK","PTDU.JK","ATAP.JK","VICI.JK","PMMP.JK","BANK.JK","WMUU.JK","EDGE.JK","UNIQ.JK","BEBS.JK","SNLK.JK","ZYRX.JK","LFLO.JK","FIMP.JK","TAPG.JK","NPGF.JK","LUCY.JK","ADCP.JK","HOPE.JK","MGLV.JK","TRUE.JK","LABA.JK","ARCI.JK","IPAC.JK","MASB.JK","BMHS.JK","FLMC.JK","NICL.JK","UVCR.JK","BUKA.JK","HAIS.JK","OILS.JK","GPSO.JK","MCOL.JK","RSGK.JK","RUNS.JK","SBMA.JK","CMNT.JK","GTSI.JK","IDEA.JK","KUAS.JK","BOBA.JK","MTEL.JK","DEPO.JK","BINO.JK","CMRY.JK","WGSH.JK","TAYS.JK","WMPP.JK","RMKE.JK","OBMD.JK","AVIA.JK","IPPE.JK","NASI.JK","BSML.JK","DRMA.JK","ADMR.JK","SEMA.JK","ASLC.JK","NETV.JK","BAUT.JK","ENAK.JK","NTBK.JK","SMKM.JK","STAA.JK","NANO.JK","BIKE.JK","WIRG.JK","SICO.JK","GOTO.JK","TLDN.JK","MTMH.JK","WINR.JK","IBOS.JK","OLIV.JK","ASHA.JK","SWID.JK","TRGU.JK","ARKO.JK","CHEM.JK","DEWI.JK","AXIO.JK","KRYA.JK","HATM.JK","RCCC.JK","GULA.JK","JARR.JK","AMMS.JK","RAFI.JK","KKES.JK","ELPI.JK","EURO.JK","KLIN.JK","TOOL.JK","BUAH.JK","CRAB.JK","MEDS.JK","COAL.JK","PRAY.JK","CBUT.JK","BELI.JK","MKTR.JK","OMED.JK","BSBK.JK","PDPP.JK","KDTN.JK","ZATA.JK","NINE.JK","MMIX.JK","PADA.JK","ISAP.JK","VTNY.JK","SOUL.JK","ELIT.JK","BEER.JK","CBPE.JK","SUNI.JK","CBRE.JK","WINE.JK","BMBL.JK","PEVE.JK","LAJU.JK","FWCT.JK","NAYZ.JK","IRSX.JK","PACK.JK","VAST.JK","CHIP.JK","HALO.JK","KING.JK","PGEO.JK","FUTR.JK","HILL.JK","BDKR.JK","PTMP.JK","SAGE.JK","TRON.JK","CUAN.JK","NSSS.JK","GTRA.JK","HAJJ.JK","JATI.JK","TYRE.JK","MPXL.JK","SMIL.JK","KLAS.JK","MAXI.JK","VKTR.JK","RELF.JK","AMMN.JK","CRSN.JK","GRPM.JK","WIDI.JK","TGUK.JK","INET.JK","MAHA.JK","RMKO.JK","CNMA.JK","FOLK.JK","HBAT.JK","GRIA.JK","PPRI.JK","ERAL.JK","CYBR.JK","MUTU.JK","LMAX.JK","HUMI.JK","MSIE.JK","RSCH.JK","BABY.JK","AEGS.JK","IOTF.JK","KOCI.JK","PTPS.JK","BREN.JK","STRK.JK","KOKA.JK","LOPI.JK","UDNG.JK","RGAS.JK","MSTI.JK","IKPM.JK","AYAM.JK","SURI.JK","ASLI.JK","GRPH.JK","SMGA.JK","UNTD.JK","TOSK.JK","MPIX.JK","ALII.JK","MKAP.JK","MEJA.JK","LIVE.JK","HYGN.JK","BAIK.JK","VISI.JK","AREA.JK","MHKI.JK","ATLA.JK","DATA.JK","SOLA.JK","BATR.JK","SPRE.JK","PART.JK","GOLF.JK","ISEA.JK","BLES.JK","GUNA.JK","LABS.JK","DOSS.JK","NEST.JK","PTMR.JK","VERN.JK","DAAZ.JK","BOAT.JK","NAIK.JK","AADI.JK","MDIY.JK","KSIX.JK","RATU.JK","YOII.JK","HGII.JK","BRRC.JK","DGWG.JK","CBDK.JK","OBAT.JK","MINE.JK","ASPR.JK","PSAT.JK","COIN.JK","CDIA.JK","BLOG.JK","MERI.JK","CHEK.JK","PMUI.JK","EMAS.JK","PJHB.JK","KAQI.JK","YUPI.JK","FORE.JK","MDLA.JK","DKHH.JK","AYLS.JK","DADA.JK","ASPI.JK","ESTA.JK","BESS.JK","AMAN.JK","CARE.JK","PIPA.JK","NCKL.JK","MENN.JK","AWAN.JK","MBMA.JK","RAAM.JK","DOOH.JK","CGAS.JK","NICE.JK","MSJA.JK","SMLE.JK","ACRO.JK","MANG.JK","WIFI.JK","FAPA.JK","DCII.JK","KETR.JK","DGNS.JK","UFOE.JK",
    # Tambah sampai 100 ticker
]

# --- INISIALISASI SESSION STATE (CACHE) ---
if 'stock_cache' not in st.session_state:
    st.session_state['stock_cache'] = {} 
if 'current_view_mode' not in st.session_state:
    st.session_state['current_view_mode'] = "Intraday (1 Hari)"

# --- HELPER FUNCTIONS ---

def fix_timezone(df):
    """Konversi ke WIB"""
    if df.empty: return df
    try:
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        df.index = df.index.tz_convert('Asia/Jakarta')
    except: pass
    return df

def reset_cache():
    st.session_state['stock_cache'] = {}

# --- PLOTTING FUNCTIONS (DUAL AXIS) ---

def plot_dual_axis_line(data, ticker, title_text):
    base_price = data['Close'].min()
    max_price = data['Close'].max()
    pct_values = ((data['Close'] - base_price) / base_price) * 100
    color = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    # Trace Harga
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines',
        line=dict(color=color, width=2), fill='tozeroy',
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
        customdata=pct_values,
        hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Harga: Rp %{y:,.0f}<br>Posisi: <b>%{customdata:.2f}%</b> dari Low<extra></extra>"
    ))
    
    # Axis Logic
    y_range = [base_price * 0.99, max_price * 1.01]
    y2_min = ((y_range[0] - base_price) / base_price) * 100
    y2_max = ((y_range[1] - base_price) / base_price) * 100
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> <span style='font-size:10px'>({title_text})</span>", x=0),
        margin=dict(l=45, r=40, t=35, b=20), height=200, showlegend=False, hovermode="x unified",
        yaxis=dict(range=y_range, showgrid=False, side='left', tickfont=dict(size=9, color='gray')),
        yaxis2=dict(range=[y2_min, y2_max], overlaying='y', side='right', showgrid=True, gridcolor='#eee', ticksuffix='%', tickfont=dict(size=9, color='gray')),
        xaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

def plot_dual_axis_candle(data, ticker):
    open_price = data['Open'].iloc[0]
    # Hover text manual biar gak crash
    hover_text = []
    for index, row in data.iterrows():
        chg = ((row['Close'] - open_price) / open_price) * 100
        hover_text.append(f"<b>{index.strftime('%H:%M')}</b><br>O:{row['Open']:,.0f} H:{row['High']:,.0f}<br>L:{row['Low']:,.0f} C:{row['Close']:,.0f}<br>Chg: <b>{chg:+.2f}%</b>")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#00C805', decreasing_line_color='#FF3B30',
        text=hover_text, hoverinfo='text'
    ))
    
    y_min, y_max = data['Low'].min(), data['High'].max()
    padding = (y_max - y_min) * 0.1 if y_max != y_min else y_max * 0.01
    range_price = [y_min - padding, y_max + padding]
    range_pct = [((range_price[0] - open_price) / open_price) * 100, ((range_price[1] - open_price) / open_price) * 100]

    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> <span style='font-size:10px'>{data.index[0].strftime('%d %b')}</span>", x=0),
        margin=dict(l=45, r=40, t=35, b=20), height=250, showlegend=False, xaxis_rangeslider_visible=False, hovermode="closest",
        yaxis=dict(range=range_price, showgrid=False, side='left', tickfont=dict(size=9, color='gray')),
        yaxis2=dict(range=range_pct, overlaying='y', side='right', showgrid=True, gridcolor='#eee', ticksuffix='%', tickfont=dict(size=9, color='gray')),
        xaxis=dict(type='date', tickformat='%H:%M', showgrid=False)
    )
    return fig

def fetch_batch_data_cached(tickers, mode):
    """Download data on-demand untuk sistem pagination"""
    results = []
    if mode == "Intraday (1 Hari)":
        period_req, interval_req, mode_label = "1d", "15m", "Intraday"
    elif mode == "Short Term (5 Hari)":
        period_req, interval_req, mode_label = "5d", "60m", "5 Days"
    else: 
        period_req, interval_req, mode_label = "1mo", "1d", "1 Month"
        
    try:
        data = yf.download(" ".join(tickers), period=period_req, interval=interval_req, group_by='ticker', threads=True, progress=False)
        for ticker in tickers:
            try:
                if len(tickers) > 1:
                    if ticker not in data.columns.levels[0]: continue
                    hist = data[ticker].dropna()
                else:
                    hist = data.dropna()
                
                if len(hist) > 0:
                    hist = fix_timezone(hist)
                    curr = hist['Close'].iloc[-1]
                    
                    if mode == "Intraday (1 Hari)":
                        op_price = hist['Open'].iloc[0]
                        change = ((curr - op_price) / op_price) * 100
                        volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                    elif mode == "Short Term (5 Hari)":
                        prev = hist['Close'].iloc[0]
                        change = ((curr - prev) / prev) * 100
                        volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                    else:
                        prev = hist['Close'].iloc[0]
                        change = ((curr - prev) / prev) * 100
                        volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                        
                    results.append({
                        'Ticker': ticker.replace('.JK', ''),
                        'Harga': curr, 'Change %': change, 'Volatilitas': volatility,
                        'Data': hist, 'TitleMode': mode_label
                    })
            except: continue
    except: pass
    return results

# --- TAB SYSTEM ---
st.title("🚀 Master Trader Dashboard")

tab1, tab2 = st.tabs(["📊 Market Grid (Pagination)", "🎲 Prob Win Rate"])

# ==========================================
# TAB 1: MARKET GRID (PAGINATION)
# ==========================================
with tab1:
    # 1. Controls
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        selected_mode = st.selectbox("Timeframe:", ["Intraday (1 Hari)", "Short Term (5 Hari)", "History (1 Bulan)"], key="mode_sel")
        
        # Reset Cache logic
        if selected_mode != st.session_state['current_view_mode']:
            st.session_state['current_view_mode'] = selected_mode
            reset_cache()
            st.rerun()

    # 2. Pagination Logic
    ITEMS_PER_PAGE = 12
    total_stocks = len(ALL_TICKERS)
    total_pages = math.ceil(total_stocks / ITEMS_PER_PAGE)
    
    with col_t2:
        current_page = st.number_input(f"Halaman (Total {total_pages})", min_value=1, max_value=total_pages, value=1)

    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_tickers = ALL_TICKERS[start_idx:end_idx]

    # 3. Fetch Data Missing in Cache
    tickers_to_fetch = [t for t in page_tickers if t not in st.session_state['stock_cache']]
    
    if tickers_to_fetch:
        with st.spinner(f"Loading data halaman {current_page}..."):
            new_data = fetch_batch_data_cached(tickers_to_fetch, selected_mode)
            for item in new_data:
                st.session_state['stock_cache'][item['Ticker'] + ".JK"] = item

    # 4. Display Grid
    page_data_list = []
    for t in page_tickers:
        if t in st.session_state['stock_cache']:
            page_data_list.append(st.session_state['stock_cache'][t])

    if page_data_list:
        df_disp = pd.DataFrame(page_data_list)
        
        # Filter Sort
        sort_opt = st.radio("Sortir:", ["Default", "Volatilitas Tertinggi", "Kenaikan Tertinggi"], horizontal=True)
        if sort_opt == "Volatilitas Tertinggi": df_disp = df_disp.sort_values('Volatilitas', ascending=False)
        elif sort_opt == "Kenaikan Tertinggi": df_disp = df_disp.sort_values('Change %', ascending=False)
        
        st.divider()
        n_cols = 3 if selected_mode == "Intraday (1 Hari)" else 4
        cols = st.columns(n_cols)
        
        for i, (index, row) in enumerate(df_disp.iterrows()):
            with cols[i % n_cols]:
                color_c = "green" if row['Change %'] > 0 else "red"
                st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
                st.markdown(f"<small>Chg: <span style='color:{color_c}'>{row['Change %']:+.2f}%</span> | Vol: {row['Volatilitas']:.2f}%</small>", unsafe_allow_html=True)
                
                if selected_mode == "Intraday (1 Hari)":
                    fig = plot_dual_axis_candle(row['Data'], row['Ticker'])
                else:
                    fig = plot_dual_axis_line(row['Data'], row['Ticker'], row['TitleMode'])
                st.plotly_chart(fig, use_container_width=True)
                st.write("")
    else:
        st.warning("Data belum termuat. Coba refresh atau cek koneksi.")

# ==========================================
# TAB 2: PROB WIN RATE (FIXED)
# ==========================================
with tab2:
    st.subheader("Simulasi Peluang Win Rate (Histori 30 Hari)")
    st.write("Menghitung berapa kali saham Close Hijau vs Merah dalam 1 bulan terakhir.")

    # --- FIX NAME ERROR ---
    # Definisikan variabel ini DULUAN sebelum dipakai di text_area
    def_perf = "BBCA.JK, BBRI.JK, BMRI.JK, GOTO.JK, ANTM.JK, ADRO.JK"
    # ----------------------

    win_input = st.text_area("Input Saham (Pisahkan koma):", value=def_perf, height=100, key="win_in")
    
    if st.button("Hitung Win Rate"):
        if win_input:
            tickers_win = [x.strip() for x in win_input.split(',')]
            tickers_str_win = " ".join(tickers_win)
            
            with st.spinner("Menghitung probabilitas..."):
                try:
                    data_win = yf.download(tickers_str_win, period="1mo", group_by='ticker', threads=True, progress=False)
                    
                    win_results = []
                    for t in tickers_win:
                        try:
                            if len(tickers_win) > 1:
                                if t not in data_win.columns.levels[0]: continue
                                df_w = data_win[t].dropna()
                            else:
                                df_w = data_win.dropna()
                                
                            if len(df_w) > 0:
                                # Hitung hari hijau vs merah
                                green_days = df_w[df_w['Close'] > df_w['Open']]
                                red_days = df_w[df_w['Close'] < df_w['Open']]
                                total_days = len(df_w)
                                
                                win_rate = (len(green_days) / total_days) * 100
                                avg_gain = ((green_days['Close'] - green_days['Open']) / green_days['Open']).mean() * 100 if not green_days.empty else 0
                                avg_loss = ((red_days['Close'] - red_days['Open']) / red_days['Open']).mean() * 100 if not red_days.empty else 0
                                
                                win_results.append({
                                    'Ticker': t.replace('.JK', ''),
                                    'Total Hari': total_days,
                                    'Win Rate (%)': win_rate,
                                    'Avg Gain (%)': avg_gain,
                                    'Avg Loss (%)': avg_loss
                                })
                        except: continue
                    
                    if win_results:
                        df_win = pd.DataFrame(win_results).sort_values('Win Rate (%)', ascending=False)
                        st.dataframe(
                            df_win,
                            column_config={
                                "Win Rate (%)": st.column_config.ProgressColumn("Peluang Hijau", format="%.1f%%", min_value=0, max_value=100),
                                "Avg Gain (%)": st.column_config.NumberColumn(format="%.2f%%"),
                                "Avg Loss (%)": st.column_config.NumberColumn(format="%.2f%%"),
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        st.info("Win Rate tinggi menunjukkan saham sering ditutup hijau dalam sebulan terakhir.")
                    else:
                        st.error("Gagal menghitung.")
                except Exception as e:
                    st.error(f"Error data: {e}")
