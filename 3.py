import yfinance as yf
import pandas as pd

tickers = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT"
    # bisa sampai 100
]

def load_data(tickers):
    data = []
    for t in tickers:
        info = yf.Ticker(t).info
        data.append({
            "Ticker": t,
            "Price": info.get("currentPrice"),
            "PE": info.get("trailingPE"),
            "PS": info.get("priceToSalesTrailing12Months"),
            "ROE": info.get("returnOnEquity"),
            "DebtToEquity": info.get("debtToEquity"),
            "EPS": info.get("trailingEps")
        })
    return pd.DataFrame(data)

df = load_data(tickers)
from st_aggrid import AgGrid, GridOptionsBuilder

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)
gb.configure_column("PE", type=["numericColumn"])
gb.configure_column("ROE", type=["numericColumn"])

grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=500,
    theme="dark"
)

df_edit = grid_response["data"]
import streamlit as st

st.sidebar.header("Scoring Weight")

w_pe = st.sidebar.slider("Weight PE", 0.0, 1.0, 0.2)
w_ps = st.sidebar.slider("Weight PS", 0.0, 1.0, 0.2)
w_roe = st.sidebar.slider("Weight ROE", 0.0, 1.0, 0.3)
w_de = st.sidebar.slider("Weight D/E", 0.0, 1.0, 0.2)
w_eps = st.sidebar.slider("Weight EPS", 0.0, 1.0, 0.1)
def normalize(series, inverse=False):
    s = series.fillna(0)
    norm = (s - s.min()) / (s.max() - s.min() + 1e-9)
    return 1 - norm if inverse else norm

df_edit["Score"] = (
    w_pe  * normalize(df_edit["PE"], inverse=True) +
    w_ps  * normalize(df_edit["PS"], inverse=True) +
    w_roe * normalize(df_edit["ROE"]) +
    w_de  * normalize(df_edit["DebtToEquity"], inverse=True) +
    w_eps * normalize(df_edit["EPS"])
)

df_rank = df_edit.sort_values("Score", ascending=False)
import plotly.express as px

fig = px.bar(
    df_rank.head(20),
    x="Ticker",
    y="Score",
    title="Top 20 Saham Berdasarkan Composite Score"
)

st.plotly_chart(fig, use_container_width=True)
