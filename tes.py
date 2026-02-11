import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Market Movers Dashboard", layout="wide")

st.title("🏆 Market Movers: Gainers & Losers")
st.markdown("Dashboard ini memantau pergerakan harga saham LQ45 secara Real-Time.")

# --- 1. DAFTAR SAHAM (BISA DITAMBAH) ---
# Kita pakai LQ45 sebagai sampel agar loading tidak terlalu lama
LIST_SAHAM = [
     "BREN.JK", "BBCA.JK", "DSSA.JK", "BBRI.JK", "TPIA.JK", "DCII.JK", "BYAN.JK", "AMMN.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "MORA.JK", "SRAJ.JK", "CUAN.JK", "BRPT.JK", "BBNI.JK", "PANI.JK", "BNLI.JK", "BRMS.JK", "CDIA.JK", "DNET.JK", "IMPC.JK", "FILM.JK", "MPRO.JK", "BRIS.JK", "ICBP.JK", "HMSP.JK", "BUMI.JK", "EMAS.JK", "UNTR.JK", "ANTM.JK", "NCKL.JK", "SMMA.JK", "ADMR.JK", "CASA.JK", "UNVR.JK", "RISE.JK", "CPIN.JK", "MLPT.JK", "AMRT.JK", "MDKA.JK", "ISAT.JK", "MBMA.JK", "GOTO.JK", "INCO.JK", "AADI.JK", "INDF.JK", "PTRO.JK", "BELI.JK", "ADRO.JK", "EXCL.JK", "TCPI.JK", "KLBF.JK", "EMTK.JK", "MYOR.JK", "PGAS.JK", "INKP.JK", "PGUN.JK", "PGEO.JK", "GEMS.JK", "MTEL.JK", "BNGA.JK", "CMRY.JK", "ARCI.JK", "TBIG.JK", "MEGA.JK", "SILO.JK", "MEDC.JK", "GIAA.JK", "SOHO.JK", "VKTR.JK", "CBDK.JK", "MIKA.JK", "NISP.JK", "JPFA.JK", "GGRM.JK", "TOWR.JK", "BBHI.JK", "ENRG.JK", "TAPG.JK", "SUPA.JK", "BUVA.JK", "PTBA.JK", "BINA.JK", "COIN.JK", "AVIA.JK", "JSMR.JK", "AKRA.JK", "NSSS.JK", "PNBN.JK", "ITMG.JK", "BDMN.JK", "ARKO.JK", "MDIY.JK", "TINS.JK", "BSIM.JK", "INTP.JK", "JARR.JK", "BKSL.JK", "BTPN.JK", "ARTO.JK", "FAPA.JK", "MKPI.JK", "RMKE.JK", "SRTG.JK", "TKIM.JK", "MAPA.JK", "MSIN.JK", "MAPI.JK", "RLCO.JK", "HEAL.JK", "BSDE.JK", "KPIG.JK", "CITA.JK", "PWON.JK", "BNBR.JK", "APIC.JK", "BBTN.JK", "SMGR.JK", "RAJA.JK", "POLU.JK", "LIFE.JK", "BNII.JK", "INDY.JK", "CTRA.JK", "SMAR.JK", "SCMA.JK", "SSMS.JK", "CARE.JK", "ULTJ.JK", "SIDO.JK", "DSNG.JK", "BBSI.JK", "BUKA.JK", "AALI.JK", "RATU.JK", "BBKP.JK", "HRUM.JK", "CMNT.JK", "SGRO.JK", "PSAB.JK", "JRPT.JK", "YUPI.JK", "STAA.JK", "STTP.JK", "GOOD.JK", "MCOL.JK", "WIFI.JK", "AUTO.JK", "TSPC.JK", "NICL.JK", "ALII.JK", "SHIP.JK", "MLBI.JK", "PACK.JK", "DEWA.JK", "CYBR.JK", "PRAY.JK", "POWR.JK", "ESSA.JK", "BMAS.JK", "MIDI.JK", "EDGE.JK", "BIPI.JK", "BSSR.JK", "SMSM.JK", "ADMF.JK", "ELPI.JK", "BFIN.JK", "HRTA.JK", "CLEO.JK", "BTPS.JK", "CMNP.JK", "CNMA.JK", "BANK.JK", "ADES.JK", "INPP.JK", "BJBR.JK", "SIMP.JK", "BJTM.JK", "PNLF.JK", "INET.JK", "SINI.JK", "TLDN.JK", "GMFI.JK", "NATO.JK", "BBMD.JK", "LSIP.JK", "TMAS.JK", "ABMM.JK", "DUTI.JK", "BHAT.JK", "DAAZ.JK", "SGER.JK", "DMND.JK", "CLAY.JK", "IBST.JK", "MTDL.JK", "BULL.JK", "ACES.JK", "LPKR.JK", "DMAS.JK", "SMRA.JK", "SSIA.JK", "ERAA.JK", "EPMT.JK", "SMDR.JK", "KRAS.JK", "JSPT.JK", "BOGA.JK", "MAYA.JK", "AGII.JK", "OMED.JK", "PALM.JK", "ANJT.JK", "TOBA.JK", "DATA.JK", "BESS.JK", "INDS.JK", "CASS.JK", "ELSA.JK", "AGRO.JK", "SAME.JK", "UANG.JK", "MNCN.JK", "LINK.JK", "BPII.JK", "YULE.JK", "TRIN.JK", "BALI.JK", "UDNG.JK", "PBSA.JK", "CTBN.JK", "DRMA.JK", "NIRO.JK", "DKFT.JK", "GTSI.JK", "MTLA.JK", "BBYB.JK", "TFCO.JK", "ROTI.JK", "FISH.JK", "TRIM.JK", "PYFA.JK", "TGKA.JK", "GOLF.JK", "KIJA.JK", "JTPE.JK", "MASB.JK", "HUMI.JK", "FORE.JK", "MPMX.JK", "RDTX.JK", "MSTI.JK", "BSWD.JK", "IMAS.JK", "BIRD.JK", "LPCK.JK", "ASSA.JK", "TUGU.JK", "BWPT.JK", "WIIM.JK", "RONY.JK", "LPPF.JK", "CENT.JK", "SDRA.JK", "SURE.JK", "VICI.JK", "MGLV.JK", "NOBU.JK", "KEEN.JK", "PSGO.JK", "AMAR.JK", "CPRO.JK", "CBRE.JK", "SOCI.JK", "ARNA.JK", "TBLA.JK", "STAR.JK", "GJTL.JK", "VICO.JK", "PBID.JK", "INPC.JK", "GGRP.JK", "IRSX.JK", "AGRS.JK", "HEXA.JK", "TOTL.JK", "UNIC.JK", "SMMT.JK", "BUKK.JK", "ROCK.JK", "SKRN.JK", "MDLA.JK", "MMLP.JK", "MINA.JK", "BACA.JK", "MAPB.JK", "KEJU.JK", "BGTG.JK", "SOTS.JK", "MBSS.JK", "SAMF.JK", "BHIT.JK", "ARGO.JK", "CBUT.JK", "PNIN.JK", "MARK.JK", "SMDM.JK", "ISSP.JK", "FPNI.JK", "APLN.JK", "MYOH.JK", "ASRI.JK", "SMIL.JK", "DAYA.JK", "KAEF.JK", "IFSH.JK", "BNBA.JK", "RALS.JK", "JAWA.JK", "MCOR.JK", "PKPK.JK", "HATM.JK", "TOTO.JK", "BCIC.JK", "IATA.JK", "MAHA.JK", "FOLK.JK", "SMBR.JK", "SFAN.JK", "BISI.JK", "BABP.JK", "FUTR.JK", "PSKT.JK", "OASA.JK", "ASLI.JK", "SSTM.JK", "SIPD.JK", "MGRO.JK", "PORT.JK", "DNAR.JK", "MKAP.JK", "BVIC.JK", "BOLT.JK", "PNGO.JK", "IPCC.JK", "BLTZ.JK", "ASGR.JK", "POLI.JK", "DWGL.JK", "BMTR.JK", "GMTD.JK", "WINS.JK", "IFII.JK", "MSJA.JK", "BCAP.JK", "OMRE.JK", "BEEF.JK", "KMTR.JK", "NICE.JK", "BKSW.JK", "PRDA.JK", "DOID.JK", "TRUE.JK", "BLUE.JK", "MDIA.JK", "WOOD.JK", "ACST.JK", "IMJS.JK", "AMAG.JK", "PTPP.JK", "MTMH.JK", "CSRA.JK", "MLIA.JK", "ITMA.JK", "DGWG.JK", "KETR.JK", "NRCA.JK", "DMMX.JK", "SCCO.JK", "INDR.JK", "PNBS.JK", "BRAM.JK", "LUCY.JK", "MBAP.JK", "TPMA.JK", "ELTY.JK", "IPTV.JK", "STRK.JK", "TEBE.JK", "ADHI.JK", "LPGI.JK", "SUNI.JK", "HILL.JK", "PSSI.JK", "MINE.JK", "FAST.JK", "DVLA.JK", "ERAL.JK", "HERO.JK", "KINO.JK", "CSAP.JK", "UCID.JK", "IPCM.JK", "MLPL.JK", "VISI.JK", "PTSN.JK", "BBRM.JK", "SPTO.JK", "FMII.JK", "PPRE.JK", "MAIN.JK", "AYAM.JK", "EURO.JK", "SKLT.JK", "DEPO.JK", "BSBK.JK", "MKTR.JK", "BMHS.JK", "NEST.JK", "PMJS.JK", "BEKS.JK", "KKGI.JK", "DLTA.JK", "AMFG.JK", "RAAM.JK", "TRGU.JK", "ALDO.JK", "GWSA.JK", "PSAT.JK", "GSMF.JK", "CARS.JK", "PADI.JK", "BBLD.JK", "DOOH.JK", "ABDA.JK", "BELL.JK", "NETV.JK", "MERK.JK", "BLOG.JK", "DILD.JK", "TAMU.JK", "CEKA.JK", "ATIC.JK", "TRST.JK", "SONA.JK", "BBSS.JK", "KBLI.JK", "BLES.JK", "CFIN.JK", "JKON.JK", "TIFA.JK", "CAMP.JK", "RANC.JK", "MITI.JK", "TCID.JK", "WSBP.JK", "GZCO.JK", "AISA.JK", "CITY.JK", "JIHD.JK", "LTLS.JK", "IBOS.JK", "ADCP.JK", "ARTA.JK", "BUAH.JK", "INDO.JK", "WOMF.JK", "BEST.JK", "PANS.JK", "TBMS.JK", "ENAK.JK", "RSCH.JK", "BLTA.JK", "JGLE.JK", "MTWI.JK", "ARII.JK", "BTEK.JK", "AREA.JK", "BOLA.JK", "SHID.JK", "ZINC.JK", "ASLC.JK", "PEVE.JK", "LIVE.JK", "MMIX.JK", "GHON.JK", "CHIP.JK", "WIRG.JK", "GDST.JK", "PBRX.JK", "GRIA.JK", "ATAP.JK", "CMPP.JK", "NELY.JK", "RMKO.JK", "NICK.JK", "SMGA.JK", "SPMA.JK", "RELI.JK", "HGII.JK", "BUDI.JK", "SKBM.JK", "COCO.JK", "LEAD.JK", "VOKS.JK", "PDPP.JK", "MHKI.JK", "NFCX.JK", "PTPW.JK", "PJAA.JK", "ZATA.JK", "NIKL.JK", "FUJI.JK", "AMOR.JK", "PANR.JK", "ADMG.JK", "MGNA.JK", "TALF.JK", "AMAN.JK", "BABY.JK", "MTFN.JK", "WTON.JK", "IPOL.JK", "SULI.JK", "PMUI.JK", "KSIX.JK", "PADA.JK", "LFLO.JK", "BPFI.JK", "JECC.JK", "FORU.JK", "HDFA.JK", "KOKA.JK", "BDKR.JK", "DGIK.JK", "WMUU.JK", "PGJO.JK", "RODA.JK", "KDSI.JK", "AXIO.JK", "TIRA.JK", "MDLN.JK", "MOLI.JK", "BEER.JK", "HOKI.JK", "BRNA.JK", "GTBO.JK", "BIKE.JK", "UNIQ.JK", "MPPA.JK", "APEX.JK", "AHAP.JK", "GTRA.JK", "SWID.JK", "IKBI.JK", "HOMI.JK", "HOPE.JK", "EKAD.JK", "VIVA.JK", "UNSP.JK", "PEGE.JK", "PZZA.JK", "SOFA.JK", "IRRA.JK", "ELIT.JK", "WEGE.JK", "SOSS.JK", "AWAN.JK", "SMKL.JK", "GLVA.JK", "TRIS.JK", "KOTA.JK", "GUNA.JK", "HAIS.JK", "UNTD.JK", "CHEK.JK", "LABS.JK", "BOAT.JK", "PNSE.JK", "MREI.JK", "FITT.JK", "KONI.JK", "VTNY.JK", "URBN.JK", "TRON.JK", "IDPR.JK", "WINE.JK", "DART.JK", "PJHB.JK", "GPRA.JK", "MDKI.JK", "KING.JK", "CNKO.JK", "UFOE.JK", "BSML.JK", "VERN.JK", "HALO.JK", "COAL.JK", "APLI.JK", "CRAB.JK", "ESTA.JK", "SURI.JK", "MDRN.JK", "MAXI.JK", "KMDS.JK", "CLPI.JK", "BAYU.JK", "VRNA.JK", "TIRT.JK", "IGAR.JK", "LAPD.JK", "IKPM.JK", "SCNP.JK", "MCAS.JK", "REAL.JK", "RIGS.JK", "CCSI.JK", "GDYR.JK", "GULA.JK", "NASA.JK", "PDES.JK", "CSIS.JK", "GOLD.JK", "PTPS.JK", "CBPE.JK", "SOLA.JK", "TYRE.JK", "ZONE.JK", "BIPP.JK", "BKDP.JK", "ESTI.JK", "IOTF.JK", "LPLI.JK", "VAST.JK", "HYGN.JK", "ASRM.JK", "KREN.JK", "SMLE.JK", "DYAN.JK", "DGNS.JK", "EAST.JK", "HAJJ.JK", "TFAS.JK", "SRSN.JK", "JATI.JK", "KBLM.JK", "DADA.JK", "BMSR.JK", "KOBX.JK", "NAIK.JK", "KBAG.JK", "TARA.JK", "SATU.JK", "ASPR.JK", "ASHA.JK", "YOII.JK", "UVCR.JK", "CRSN.JK", "YPAS.JK", "TRUS.JK", "ATLA.JK", "INTA.JK", "ERTX.JK", "GPSO.JK", "PART.JK", "MUTU.JK", "SAFE.JK", "KLAS.JK", "AKPI.JK", "ITIC.JK", "CGAS.JK", "EMDE.JK", "MICE.JK", "VINS.JK", "ASMI.JK", "HRME.JK", "BPTR.JK", "AMIN.JK", "ASPI.JK", "IKAI.JK", "BINO.JK", "SAGE.JK", "TOSK.JK", "BTON.JK", "OKAS.JK", "MPXL.JK", "WGSH.JK", "ACRO.JK", "AGAR.JK", "INOV.JK", "POLA.JK", "LMPI.JK", "FIRE.JK", "ANDI.JK", "PUDP.JK", "DOSS.JK", "FWCT.JK", "AKSI.JK", "CASH.JK", "KBLV.JK", "PRIM.JK", "NTBK.JK", "DEWI.JK", "OBAT.JK", "ASJT.JK", "ALKA.JK", "ECII.JK", "RELF.JK", "LCKM.JK", "PEHA.JK", "AKKU.JK", "ENZO.JK", "AYLS.JK", "INPS.JK", "BAJA.JK", "WINR.JK", "ASDM.JK", "SDPC.JK", "TRJA.JK", "SAPX.JK", "WAPO.JK", "PTMP.JK", "BAUT.JK", "MEJA.JK", "JMAS.JK", "LPPS.JK", "OBMD.JK", "NPGF.JK", "NZIA.JK", "MANG.JK", "LION.JK", "TAXI.JK", "PTSP.JK", "APII.JK", "CAKK.JK", "NANO.JK", "SLIS.JK", "DFAM.JK", "WOWS.JK", "SDMU.JK", "CINT.JK", "ZYRX.JK", "DKHH.JK", "MRAT.JK", "ABBA.JK", "BOBA.JK", "DIVA.JK", "PURA.JK", "MARI.JK", "PAMG.JK", "BAPI.JK", "CANI.JK", "KOPI.JK", "DSFI.JK", "SMKM.JK", "WEHA.JK", "PURI.JK", "LPIN.JK", "IBFN.JK", "RUIS.JK", "NAYZ.JK", "LAJU.JK", "TRUK.JK", "LAND.JK", "KARW.JK", "HELI.JK", "CHEM.JK", "SEMA.JK", "PSDN.JK", "IPAC.JK", "SNLK.JK", "INTD.JK", "MSKY.JK", "MBTO.JK", "KRYA.JK", "ASBI.JK", "INCI.JK", "TMPO.JK", "GEMA.JK", "ISAP.JK", "YELO.JK", "MERI.JK", "PTIS.JK", "ISEA.JK", "FOOD.JK", "LABA.JK", "MPIX.JK", "RGAS.JK", "DEFI.JK", "KUAS.JK", "SBMA.JK", "EPAC.JK", "RCCC.JK", "KIOS.JK", "INAI.JK", "RBMS.JK", "MIRA.JK", "NASI.JK", "MEDS.JK", "CSMI.JK", "CTTH.JK", "OLIV.JK", "JAST.JK", "IDEA.JK", "OPMS.JK", "PTDU.JK", "PGLI.JK", "FLMC.JK", "BCIP.JK", "INCF.JK", "HDIT.JK", "JAYA.JK", "AIMS.JK", "RUNS.JK", "POLY.JK", "OILS.JK", "BATA.JK", "KOIN.JK", "ICON.JK", "LRNA.JK", "MPOW.JK", "PICO.JK", "IKAN.JK", "TAYS.JK", "ESIP.JK", "KJEN.JK", "LUCK.JK", "TNCA.JK", "KICI.JK", "SOUL.JK", "ARKA.JK", "PLAN.JK", "BMBL.JK", "BAPA.JK", "RICY.JK", "WIDI.JK", "DIGI.JK", "INDX.JK", "HADE.JK", "TAMA.JK", "PCAR.JK", "LOPI.JK", "GRPH.JK", "HBAT.JK", "PIPA.JK", "KLIN.JK", "PPRI.JK", "AEGS.JK", "SPRE.JK", "KAQI.JK", "NINE.JK", "KOCI.JK", "LMAX.JK", "BRRC.JK", "RAFI.JK", "TOOL.JK", "BATR.JK", "AMMS.JK", "KKES.JK", "SICO.JK", "BAIK.JK", "GRPM.JK", "KDTN.JK", "MSIE.JK"
]


# --- 2. FUNGSI AMBIL DATA MASSAL ---
@st.cache_data(ttl=300) # Cache data 5 menit biar gak lemot
def get_market_data(tickers):
    # Download data 5 hari terakhir untuk dapat Closing Price kemarin & hari ini
    data = yf.download(tickers, period="5d", group_by='ticker', progress=False)
    
    results = []
    
    for ticker in tickers:
        try:
            # Handling MultiIndex Dataframe
            if len(tickers) > 1:
                df = data[ticker]
            else:
                df = data
            
            # Pastikan data tidak kosong
            df = df.dropna()
            if len(df) < 2:
                continue
                
            # Ambil Harga Terakhir & Sebelumnya
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            
            # Hitung Persentase Perubahan
            change_pct = ((last_price - prev_price) / prev_price) * 100
            volume = df['Volume'].iloc[-1]
            
            results.append({
                "Ticker": ticker.replace(".JK", ""),
                "Harga": last_price,
                "Change (%)": change_pct,
                "Volume": volume
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(results)

# --- 3. SIDEBAR KONTROL ---
st.sidebar.header("⚙️ Pengaturan Tampilan")

# A. Slider Jumlah Baris (Ini jawaban dari request kamu)
# Kamu bisa geser dari 5 sampai Total Saham
jumlah_tampil = st.sidebar.slider(
    "Jumlah Saham Ditampilkan:", 
    min_value=5, 
    max_value=len(LIST_SAHAM), 
    value=10  # Default 10, tapi bisa digeser mentok kanan
)

# B. Pilihan Sortir
sort_option = st.sidebar.radio(
    "Urutkan Berdasarkan:",
    ["🚀 Top Gainers (Tertinggi)", "🔻 Top Losers (Terendah)", "🔤 Abjad (A-Z)"]
)

# --- 4. EKSEKUSI & TAMPILAN ---
if st.button("🔄 Refresh Data Pasar"):
    st.cache_data.clear() # Tombol reset cache untuk ambil data terbaru

with st.spinner("Sedang memindai pasar..."):
    df_market = get_market_data(LIST_SAHAM)

if not df_market.empty:
    # Logic Sorting
    if sort_option == "🚀 Top Gainers (Tertinggi)":
        df_sorted = df_market.sort_values(by="Change (%)", ascending=False)
    elif sort_option == "🔻 Top Losers (Terendah)":
        df_sorted = df_market.sort_values(by="Change (%)", ascending=True)
    else:
        df_sorted = df_market.sort_values(by="Ticker", ascending=True)
    
    # Logic Limiting (Potong Data sesuai Slider)
    df_final = df_sorted.head(jumlah_tampil).reset_index(drop=True)
    
    # --- TAMPILAN DATAFRAME CANTIK ---
    st.subheader(f"Menampilkan {jumlah_tampil} Saham - {sort_option}")
    
    # Fungsi pewarnaan (Hijau Positif, Merah Negatif)
    def highlight_change(val):
        color = '#d4f7d4' if val > 0 else '#f7d4d4' if val < 0 else ''
        return f'background-color: {color}'

    st.dataframe(
        df_final.style.format({
            "Harga": "Rp {:,.0f}",
            "Change (%)": "{:+.2f}%",
            "Volume": "{:,.0f}"
        }).applymap(highlight_change, subset=['Change (%)']),
        use_container_width=True,
        height=(35 * jumlah_tampil) + 40 # Tinggi tabel menyesuaikan jumlah data
    )
    
else:
    st.error("Gagal mengambil data pasar. Coba refresh.")
