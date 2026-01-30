import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz # Library timezone

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Dashboard Fix", layout="wide")

# --- LIST SAHAM ---
DEFAULT_TICKERS = [
    "AALI.JK","ABBA.JK","ABDA.JK","ABMM.JK","ACES.JK","ACST.JK","ADES.JK","ADHI.JK","ADMF.JK","ADMG.JK","ADRO.JK","AGII.JK","AGRO.JK","AGRS.JK","AHAP.JK","AIMS.JK","AISA.JK","AKKU.JK","AKPI.JK","AKRA.JK","AKSI.JK","ALDO.JK","ALKA.JK","ALMI.JK","ALTO.JK","AMAG.JK","AMFG.JK","AMIN.JK","AMRT.JK","ANJT.JK","ANTM.JK","APEX.JK","APIC.JK","APII.JK","APLI.JK","APLN.JK","ARGO.JK","ARII.JK","ARNA.JK","ARTA.JK","ARTI.JK","ARTO.JK","ASBI.JK","ASDM.JK","ASGR.JK","ASII.JK","ASJT.JK","ASMI.JK","ASRI.JK","ASRM.JK","ASSA.JK","ATIC.JK","AUTO.JK","BABP.JK","BACA.JK","BAJA.JK","BALI.JK","BAPA.JK","BATA.JK","BAYU.JK","BBCA.JK","BBHI.JK","BBKP.JK","BBLD.JK","BBMD.JK","BBNI.JK","BBRI.JK","BBRM.JK","BBTN.JK","BBYB.JK","BCAP.JK","BCIC.JK","BCIP.JK","BDMN.JK","BEKS.JK","BEST.JK","BFIN.JK","BGTG.JK","BHIT.JK","BIKA.JK","BIMA.JK","BINA.JK","BIPI.JK","BIPP.JK","BIRD.JK","BISI.JK","BJBR.JK","BJTM.JK","BKDP.JK","BKSL.JK","BKSW.JK","BLTA.JK","BLTZ.JK","BMAS.JK","BMRI.JK","BMSR.JK","BMTR.JK","BNBA.JK","BNBR.JK","BNGA.JK","BNII.JK","BNLI.JK","BOLT.JK","BPFI.JK","BPII.JK","BRAM.JK","BRMS.JK","BRNA.JK","BRPT.JK","BSDE.JK","BSIM.JK","BSSR.JK","BSWD.JK","BTEK.JK","BTEL.JK","BTON.JK","BTPN.JK","BUDI.JK","BUKK.JK","BULL.JK","BUMI.JK","BUVA.JK","BVIC.JK","BWPT.JK","BYAN.JK","CANI.JK","CASS.JK","CEKA.JK","CENT.JK","CFIN.JK","CINT.JK","CITA.JK","CLPI.JK","CMNP.JK","CMPP.JK","CNKO.JK","CNTX.JK","COWL.JK","CPIN.JK","CPRO.JK","CSAP.JK","CTBN.JK","CTRA.JK","CTTH.JK","DART.JK","DEFI.JK","DEWA.JK","DGIK.JK","DILD.JK","DKFT.JK","DLTA.JK","DMAS.JK","DNAR.JK","DNET.JK","DOID.JK","DPNS.JK","DSFI.JK","DSNG.JK","DSSA.JK","DUTI.JK","DVLA.JK","DYAN.JK","ECII.JK","EKAD.JK","ELSA.JK","ELTY.JK","EMDE.JK","EMTK.JK","ENRG.JK","EPMT.JK","ERAA.JK","ERTX.JK","ESSA.JK","ESTI.JK","ETWA.JK","EXCL.JK","FAST.JK","FASW.JK","FISH.JK","FMII.JK","FORU.JK","FPNI.JK","GAMA.JK","GDST.JK","GDYR.JK","GEMA.JK","GEMS.JK","GGRM.JK","GIAA.JK","GJTL.JK","GLOB.JK","GMTD.JK","GOLD.JK","GOLL.JK","GPRA.JK","GSMF.JK","GTBO.JK","GWSA.JK","GZCO.JK","HADE.JK","HDFA.JK","HERO.JK","HEXA.JK","HITS.JK","HMSP.JK","HOME.JK","HOTL.JK","HRUM.JK","IATA.JK","IBFN.JK","IBST.JK","ICBP.JK","ICON.JK","IGAR.JK","IIKP.JK","IKAI.JK","IKBI.JK","IMAS.JK","IMJS.JK","IMPC.JK","INAF.JK","INAI.JK","INCI.JK","INCO.JK","INDF.JK","INDR.JK","INDS.JK","INDX.JK","INDY.JK","INKP.JK","INPC.JK","INPP.JK","INRU.JK","INTA.JK","INTD.JK","INTP.JK","IPOL.JK","ISAT.JK","ISSP.JK","ITMA.JK","ITMG.JK","JAWA.JK","JECC.JK","JIHD.JK","JKON.JK","JPFA.JK","JRPT.JK","JSMR.JK","JSPT.JK","JTPE.JK","KAEF.JK","KARW.JK","KBLI.JK","KBLM.JK","KBLV.JK","KBRI.JK","KDSI.JK","KIAS.JK","KICI.JK","KIJA.JK","KKGI.JK","KLBF.JK","KOBX.JK","KOIN.JK","KONI.JK","KOPI.JK","KPIG.JK","KRAS.JK","KREN.JK","LAPD.JK","LCGP.JK","LEAD.JK","LINK.JK","LION.JK","LMAS.JK","LMPI.JK","LMSH.JK","LPCK.JK","LPGI.JK","LPIN.JK","LPKR.JK","LPLI.JK","LPPF.JK","LPPS.JK","LRNA.JK","LSIP.JK","LTLS.JK","MAGP.JK","MAIN.JK","MAPI.JK","MAYA.JK","MBAP.JK","MBSS.JK","MBTO.JK","MCOR.JK","MDIA.JK","MDKA.JK","MDLN.JK","MDRN.JK","MEDC.JK","MEGA.JK","MERK.JK","META.JK","MFMI.JK","MGNA.JK","MICE.JK","MIDI.JK","MIKA.JK","MIRA.JK","MITI.JK","MKPI.JK","MLBI.JK","MLIA.JK","MLPL.JK","MLPT.JK","MMLP.JK","MNCN.JK","MPMX.JK","MPPA.JK","MRAT.JK","MREI.JK","MSKY.JK","MTDL.JK","MTFN.JK","MTLA.JK","MTSM.JK","MYOH.JK","MYOR.JK","MYTX.JK","NELY.JK","NIKL.JK","NIRO.JK","NISP.JK","NOBU.JK","NRCA.JK","OCAP.JK","OKAS.JK","OMRE.JK","PADI.JK","PALM.JK","PANR.JK","PANS.JK","PBRX.JK","PDES.JK","PEGE.JK","PGAS.JK","PGLI.JK","PICO.JK","PJAA.JK","PKPK.JK","PLAS.JK","PLIN.JK","PNBN.JK","PNBS.JK","PNIN.JK","PNLF.JK","PNSE.JK","POLY.JK","POOL.JK","PPRO.JK","PSAB.JK","PSDN.JK","PSKT.JK","PTBA.JK","PTIS.JK","PTPP.JK","PTRO.JK","PTSN.JK","PTSP.JK","PUDP.JK","PWON.JK","PYFA.JK","RAJA.JK","RALS.JK","RANC.JK","RBMS.JK","RDTX.JK","RELI.JK","RICY.JK","RIGS.JK","RIMO.JK","RODA.JK","ROTI.JK","RUIS.JK","SAFE.JK","SAME.JK","SCCO.JK","SCMA.JK","SCPI.JK","SDMU.JK","SDPC.JK","SDRA.JK","SGRO.JK","SHID.JK","SIDO.JK","SILO.JK","SIMA.JK","SIMP.JK","SIPD.JK","SKBM.JK","SKLT.JK","SKYB.JK","SMAR.JK","SMBR.JK","SMCB.JK","SMDM.JK","SMDR.JK","SMGR.JK","SMMA.JK","SMMT.JK","SMRA.JK","SMRU.JK","SMSM.JK","SOCI.JK","SONA.JK","SPMA.JK","SQMI.JK","SRAJ.JK","SRIL.JK","SRSN.JK","SRTG.JK","SSIA.JK","SSMS.JK","SSTM.JK","STAR.JK","STTP.JK","SUGI.JK","SULI.JK","SUPR.JK","TALF.JK","TARA.JK","TAXI.JK","TBIG.JK","TBLA.JK","TBMS.JK","TCID.JK","TELE.JK","TFCO.JK","TGKA.JK","TIFA.JK","TINS.JK","TIRA.JK","TIRT.JK","TKIM.JK","TLKM.JK","TMAS.JK","TMPO.JK","TOBA.JK","TOTL.JK","TOTO.JK","TOWR.JK","TPIA.JK","TPMA.JK","TRAM.JK","TRIL.JK","TRIM.JK","TRIO.JK","TRIS.JK","TRST.JK","TRUS.JK","TSPC.JK","ULTJ.JK","UNIC.JK","UNIT.JK","UNSP.JK","UNTR.JK","UNVR.JK","VICO.JK","VINS.JK","VIVA.JK","VOKS.JK","VRNA.JK","WAPO.JK","WEHA.JK","WICO.JK","WIIM.JK","WIKA.JK","WINS.JK","WOMF.JK","WSKT.JK","WTON.JK","YPAS.JK","YULE.JK","ZBRA.JK","SHIP.JK","CASA.JK","DAYA.JK","DPUM.JK","IDPR.JK","JGLE.JK","KINO.JK","MARI.JK","MKNT.JK","MTRA.JK","OASA.JK","POWR.JK","INCF.JK","WSBP.JK","PBSA.JK","PRDA.JK","BOGA.JK","BRIS.JK","PORT.JK","CARS.JK","MINA.JK","CLEO.JK","TAMU.JK","CSIS.JK","TGRA.JK","FIRE.JK","TOPS.JK","KMTR.JK","ARMY.JK","MAPB.JK","WOOD.JK","HRTA.JK","MABA.JK","HOKI.JK","MPOW.JK","MARK.JK","NASA.JK","MDKI.JK","BELL.JK","KIOS.JK","GMFI.JK","MTWI.JK","ZINC.JK","MCAS.JK","PPRE.JK","WEGE.JK","PSSI.JK","MORA.JK","DWGL.JK","PBID.JK","JMAS.JK","CAMP.JK","IPCM.JK","PCAR.JK","LCKM.JK","BOSS.JK","HELI.JK","JSKY.JK","INPS.JK","GHON.JK","TDPM.JK","DFAM.JK","NICK.JK","BTPS.JK","SPTO.JK","PRIM.JK","HEAL.JK","TRUK.JK","PZZA.JK","TUGU.JK","MSIN.JK","SWAT.JK","TNCA.JK","MAPA.JK","TCPI.JK","IPCC.JK","RISE.JK","BPTR.JK","POLL.JK","NFCX.JK","MGRO.JK","NUSA.JK","FILM.JK","ANDI.JK","LAND.JK","MOLI.JK","PANI.JK","DIGI.JK","CITY.JK","SAPX.JK","SURE.JK","HKMU.JK","MPRO.JK","DUCK.JK","GOOD.JK","SKRN.JK","YELO.JK","CAKK.JK","SATU.JK","SOSS.JK","DEAL.JK","POLA.JK","DIVA.JK","LUCK.JK","URBN.JK","SOTS.JK","ZONE.JK","PEHA.JK","FOOD.JK","BEEF.JK","POLI.JK","CLAY.JK","NATO.JK","JAYA.JK","COCO.JK","MTPS.JK","CPRI.JK","HRME.JK","POSA.JK","JAST.JK","FITT.JK","BOLA.JK","CCSI.JK","SFAN.JK","POLU.JK","KJEN.JK","KAYU.JK","ITIC.JK","PAMG.JK","IPTV.JK","BLUE.JK","ENVY.JK","EAST.JK","LIFE.JK","FUJI.JK","KOTA.JK","INOV.JK","ARKA.JK","SMKL.JK","HDIT.JK","KEEN.JK","BAPI.JK","TFAS.JK","GGRP.JK","OPMS.JK","NZIA.JK","SLIS.JK","PURE.JK","IRRA.JK","DMMX.JK","SINI.JK","WOWS.JK","ESIP.JK","TEBE.JK","KEJU.JK","PSGO.JK","AGAR.JK","IFSH.JK","REAL.JK","IFII.JK","PMJS.JK","UCID.JK","GLVA.JK","PGJO.JK","AMAR.JK","CSRA.JK","INDO.JK","AMOR.JK","TRIN.JK","DMND.JK","PURA.JK","PTPW.JK","TAMA.JK","IKAN.JK","SAMF.JK","SBAT.JK","KBAG.JK","CBMF.JK","RONY.JK","CSMI.JK","BBSS.JK","BHAT.JK","CASH.JK","TECH.JK","EPAC.JK","UANG.JK","PGUN.JK","SOFA.JK","PPGL.JK","TOYS.JK","SGER.JK","TRJA.JK","PNGO.JK","SCNP.JK","BBSI.JK","KMDS.JK","PURI.JK","SOHO.JK","HOMI.JK","ROCK.JK","ENZO.JK","PLAN.JK","PTDU.JK","ATAP.JK","VICI.JK","PMMP.JK","BANK.JK","WMUU.JK","EDGE.JK","UNIQ.JK","BEBS.JK","SNLK.JK","ZYRX.JK","LFLO.JK","FIMP.JK","TAPG.JK","NPGF.JK","LUCY.JK","ADCP.JK","HOPE.JK","MGLV.JK","TRUE.JK","LABA.JK","ARCI.JK","IPAC.JK","MASB.JK","BMHS.JK","FLMC.JK","NICL.JK","UVCR.JK","BUKA.JK","HAIS.JK","OILS.JK","GPSO.JK","MCOL.JK","RSGK.JK","RUNS.JK","SBMA.JK","CMNT.JK","GTSI.JK","IDEA.JK","KUAS.JK","BOBA.JK","MTEL.JK","DEPO.JK","BINO.JK","CMRY.JK","WGSH.JK","TAYS.JK","WMPP.JK","RMKE.JK","OBMD.JK","AVIA.JK","IPPE.JK","NASI.JK","BSML.JK","DRMA.JK","ADMR.JK","SEMA.JK","ASLC.JK","NETV.JK","BAUT.JK","ENAK.JK","NTBK.JK","SMKM.JK","STAA.JK","NANO.JK","BIKE.JK","WIRG.JK","SICO.JK","GOTO.JK","TLDN.JK","MTMH.JK","WINR.JK","IBOS.JK","OLIV.JK","ASHA.JK","SWID.JK","TRGU.JK","ARKO.JK","CHEM.JK","DEWI.JK","AXIO.JK","KRYA.JK","HATM.JK","RCCC.JK","GULA.JK","JARR.JK","AMMS.JK","RAFI.JK","KKES.JK","ELPI.JK","EURO.JK","KLIN.JK","TOOL.JK","BUAH.JK","CRAB.JK","MEDS.JK","COAL.JK","PRAY.JK","CBUT.JK","BELI.JK","MKTR.JK","OMED.JK","BSBK.JK","PDPP.JK","KDTN.JK","ZATA.JK","NINE.JK","MMIX.JK","PADA.JK","ISAP.JK","VTNY.JK","SOUL.JK","ELIT.JK","BEER.JK","CBPE.JK","SUNI.JK","CBRE.JK","WINE.JK","BMBL.JK","PEVE.JK","LAJU.JK","FWCT.JK","NAYZ.JK","IRSX.JK","PACK.JK","VAST.JK","CHIP.JK","HALO.JK","KING.JK","PGEO.JK","FUTR.JK","HILL.JK","BDKR.JK","PTMP.JK","SAGE.JK","TRON.JK","CUAN.JK","NSSS.JK","GTRA.JK","HAJJ.JK","JATI.JK","TYRE.JK","MPXL.JK","SMIL.JK","KLAS.JK","MAXI.JK","VKTR.JK","RELF.JK","AMMN.JK","CRSN.JK","GRPM.JK","WIDI.JK","TGUK.JK","INET.JK","MAHA.JK","RMKO.JK","CNMA.JK","FOLK.JK","HBAT.JK","GRIA.JK","PPRI.JK","ERAL.JK","CYBR.JK","MUTU.JK","LMAX.JK","HUMI.JK","MSIE.JK","RSCH.JK","BABY.JK","AEGS.JK","IOTF.JK","KOCI.JK","PTPS.JK","BREN.JK","STRK.JK","KOKA.JK","LOPI.JK","UDNG.JK","RGAS.JK","MSTI.JK","IKPM.JK","AYAM.JK","SURI.JK","ASLI.JK","GRPH.JK","SMGA.JK","UNTD.JK","TOSK.JK","MPIX.JK","ALII.JK","MKAP.JK","MEJA.JK","LIVE.JK","HYGN.JK","BAIK.JK","VISI.JK","AREA.JK","MHKI.JK","ATLA.JK","DATA.JK","SOLA.JK","BATR.JK","SPRE.JK","PART.JK","GOLF.JK","ISEA.JK","BLES.JK","GUNA.JK","LABS.JK","DOSS.JK","NEST.JK","PTMR.JK","VERN.JK","DAAZ.JK","BOAT.JK","NAIK.JK","AADI.JK","MDIY.JK","KSIX.JK","RATU.JK","YOII.JK","HGII.JK","BRRC.JK","DGWG.JK","CBDK.JK","OBAT.JK","MINE.JK","ASPR.JK","PSAT.JK","COIN.JK","CDIA.JK","BLOG.JK","MERI.JK","CHEK.JK","PMUI.JK","EMAS.JK","PJHB.JK","KAQI.JK","YUPI.JK","FORE.JK","MDLA.JK","DKHH.JK","AYLS.JK","DADA.JK","ASPI.JK","ESTA.JK","BESS.JK","AMAN.JK","CARE.JK","PIPA.JK","NCKL.JK","MENN.JK","AWAN.JK","MBMA.JK","RAAM.JK","DOOH.JK","CGAS.JK","NICE.JK","MSJA.JK","SMLE.JK","ACRO.JK","MANG.JK","WIFI.JK","FAPA.JK","DCII.JK","KETR.JK","DGNS.JK","UFOE.JK",
    # Tambah sampai 100 ticker
]

# --- FUNGSI BANTUAN TIMEZONE ---
def fix_timezone(df):
    """Konversi ke WIB (Asia/Jakarta)"""
    if df.empty: return df
    try:
        # Jika index belum punya timezone, set ke UTC dulu baru convert
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        
        # Convert ke Jakarta
        df.index = df.index.tz_convert('Asia/Jakarta')
    except Exception as e:
        pass # Jika gagal, biarkan apa adanya
    return df

# --- 1. GRAFIK GARIS (5 HARI & 1 BULAN) ---
def plot_dual_axis_line(data, ticker, title_text):
    # Tentukan Baseline (Titik 0%) = Harga Terendah di periode itu
    base_price = data['Close'].min()
    max_price = data['Close'].max()
    
    # Hitung kolom persentase untuk tooltip
    # Rumus: Seberapa persen harga ini dibandingkan harga terendah
    pct_values = ((data['Close'] - base_price) / base_price) * 100
    
    # Warna garis
    color = '#00C805' if data['Close'].iloc[-1] >= data['Open'].iloc[0] else '#FF3B30'
    
    fig = go.Figure()
    
    # Trace Harga (Sumbu Kiri)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
        name='Harga',
        # Custom Data untuk Hover
        customdata=pct_values,
        hovertemplate=(
            "<b>%{x|%d %b %H:%M}</b><br>" +
            "Harga: Rp %{y:,.0f}<br>" +
            "Posisi: <b>%{customdata:.2f}%</b> dari Low<extra></extra>"
        )
    ))
    
    # LOGIKA DUAL AXIS MANUAL
    # Kita set range sumbu kanan agar sinkron dengan sumbu kiri
    # Jika Harga (Y1) = Base Price, maka Persen (Y2) = 0%
    y_range = [base_price * 0.99, max_price * 1.01] # Padding dikit
    
    # Konversi range harga ke range persen
    y2_min = ((y_range[0] - base_price) / base_price) * 100
    y2_max = ((y_range[1] - base_price) / base_price) * 100
    
    fig.update_layout(
        title=dict(text=f"<b>{ticker}</b> <span style='font-size:10px'>({title_text})</span>", x=0),
        margin=dict(l=45, r=40, t=35, b=20),
        height=200,
        showlegend=False,
        hovermode="x unified",
        
        # Sumbu Kiri (Harga)
        yaxis=dict(
            title=None,
            range=y_range,
            showgrid=False,
            side='left',
            tickfont=dict(size=9, color='gray')
        ),
        
        # Sumbu Kanan (Persentase)
        yaxis2=dict(
            title=None,
            range=[y2_min, y2_max], # Sinkronkan
            overlaying='y',
            side='right',
            showgrid=True,
            gridcolor='#eee',
            ticksuffix='%',
            tickfont=dict(size=9, color='gray')
        ),
        xaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

# --- 2. GRAFIK CANDLESTICK (1 HARI) - FIXED ---
def plot_dual_axis_candle(data, ticker):
    # Baseline untuk Intraday = Harga OPEN pagi ini
    open_price = data['Open'].iloc[0]
    
    # Hitung % Change untuk setiap baris (untuk tooltip)
    # Kita masukkan ke string html biar aman dan gak error
    hover_text = []
    for index, row in data.iterrows():
        chg = ((row['Close'] - open_price) / open_price) * 100
        # Format tanggal lokal
        d_str = index.strftime('%d %b %H:%M')
        txt = (f"<b>{d_str}</b><br>"
               f"O: {row['Open']:,.0f}<br>"
               f"H: {row['High']:,.0f}<br>"
               f"L: {row['Low']:,.0f}<br>"
               f"C: {row['Close']:,.0f}<br>"
               f"Chg: <b>{chg:+.2f}%</b>")
        hover_text.append(txt)

    fig = go.Figure()
    
    # Trace Candle
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        increasing_line_color='#00C805',
        decreasing_line_color='#FF3B30',
        name=ticker,
        text=hover_text, # Pakai ini biar gak crash!
        hoverinfo='text' # Suruh plotly baca text di atas
    ))
    
    # SINKRONISASI SUMBU KIRI & KANAN
    y_min = data['Low'].min()
    y_max = data['High'].max()
    padding = (y_max - y_min) * 0.1 if y_max != y_min else y_max * 0.01
    
    # Range Harga (Kiri)
    range_price = [y_min - padding, y_max + padding]
    
    # Range Persen (Kanan) - Relatif terhadap OPEN Price
    range_pct = [
        ((range_price[0] - open_price) / open_price) * 100,
        ((range_price[1] - open_price) / open_price) * 100
    ]

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> <span style='font-size:10px'>{data.index[0].strftime('%d %b %Y')}</span>", 
            x=0
        ),
        margin=dict(l=45, r=40, t=35, b=20),
        height=250,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        hovermode="closest", # Candle lebih enak hover per item
        
        # Y1: Harga
        yaxis=dict(
            title=None,
            side='left',
            showgrid=False,
            range=range_price,
            tickfont=dict(size=9, color='gray')
        ),
        
        # Y2: Persen
        yaxis2=dict(
            title=None,
            side='right',
            overlaying='y',
            showgrid=True,
            gridcolor='#eee',
            range=range_pct, # Range sinkron
            ticksuffix='%',
            tickfont=dict(size=9, color='gray')
        ),
        
        # X: Waktu
        xaxis=dict(
            type='date',
            tickformat='%H:%M',
            showgrid=False
        )
    )
    return fig

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=300)
def get_stock_data(tickers_list, mode):
    all_results = []
    chunk_size = 50 
    
    if mode == "Intraday (1 Hari)":
        period_req, interval_req = "1d", "15m"
    elif mode == "Short Term (5 Hari)":
        period_req, interval_req = "5d", "60m"
    else: 
        period_req, interval_req = "1mo", "1d"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(tickers_list)
    
    for i in range(0, total, chunk_size):
        batch = tickers_list[i : i + chunk_size]
        batch_str = " ".join(batch)
        status_text.text(f"Scanning {mode}... ({i}/{total})")
        progress_bar.progress(min((i + chunk_size) / total, 1.0))
        
        try:
            # Download
            data = yf.download(batch_str, period=period_req, interval=interval_req, group_by='ticker', threads=True, progress=False)
            
            for ticker in batch:
                try:
                    if len(batch) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        hist = data[ticker].dropna()
                    else:
                        hist = data.dropna()
                    
                    if len(hist) > 0:
                        # FIX TIMEZONE
                        hist = fix_timezone(hist)
                        
                        curr = hist['Close'].iloc[-1]
                        
                        # Logic Perhitungan
                        if mode == "Intraday (1 Hari)":
                            op_price = hist['Open'].iloc[0]
                            change = ((curr - op_price) / op_price) * 100
                            # Volatilitas Intraday
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "Intraday"
                            
                        elif mode == "Short Term (5 Hari)":
                            prev = hist['Close'].iloc[0]
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "5 Days"
                            
                        else: # 1 Month
                            prev = hist['Close'].iloc[0]
                            change = ((curr - prev) / prev) * 100
                            volatility = ((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100
                            title_mode = "1 Month"

                        all_results.append({
                            'Ticker': ticker.replace('.JK', ''),
                            'Harga': curr,
                            'Change %': change,
                            'Volatilitas': volatility,
                            'Data': hist,
                            'TitleMode': title_mode
                        })
                except: continue
        except: continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_results)

# --- UI UTAMA ---
st.title("📈 Pro Trader Dashboard v3 (Dual Axis)")

# KONTROL
col1, col2 = st.columns([3, 1])
with col1:
    view_mode = st.selectbox("Timeframe:", ["Intraday (1 Hari)", "Short Term (5 Hari)", "History (1 Bulan)"])
with col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# PROSES
df = get_stock_data(DEFAULT_TICKERS, view_mode)

if not df.empty:
    # SORTING
    col_s1, col_s2 = st.columns([2, 2])
    with col_s1:
        sort_opt = st.selectbox("Urutkan:", ["Volatilitas (Range Lebar)", "Top Gainers", "Top Losers"])
    
    if sort_opt == "Volatilitas (Range Lebar)":
        df_display = df.nlargest(20, 'Volatilitas')
    elif sort_opt == "Top Gainers":
        df_display = df.nlargest(20, 'Change %')
    else:
        df_display = df.nsmallest(20, 'Change %')
        
    st.divider()
    
    # GRID LAYOUT
    n_cols = 3 if view_mode == "Intraday (1 Hari)" else 4
    cols = st.columns(n_cols)
    
    for i, (index, row) in enumerate(df_display.iterrows()):
        with cols[i % n_cols]:
            # INFO HEADER
            color_c = "green" if row['Change %'] > 0 else "red"
            st.markdown(f"**{row['Ticker']}** | Rp {row['Harga']:,.0f}")
            st.markdown(f"<small>Chg: <span style='color:{color_c}'>{row['Change %']:+.2f}%</span> | Volatility: {row['Volatilitas']:.2f}%</small>", unsafe_allow_html=True)
            
            # PLOT CHART
            if view_mode == "Intraday (1 Hari)":
                fig = plot_dual_axis_candle(row['Data'], row['Ticker'])
            else:
                fig = plot_dual_axis_line(row['Data'], row['Ticker'], row['TitleMode'])
                
            st.plotly_chart(fig, use_container_width=True)
            st.write("")
else:
    st.error("Data tidak tersedia. Pastikan market buka atau koneksi aman.")
