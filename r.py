import yfinance as yf
import pandas as pd
import streamlit as st

# ================= CONFIG =================
st.set_page_config(page_title="IHSG PE & Revenue Screener", layout="wide")
st.title("📊 IHSG PE & Revenue Screener")

TICKERS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "TLKM.JK",
    "ASII.JK"
]

# ================= FUNCTION =================
def get_pe_revenue(tickers):
    rows = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        # ✅ DEFINE FIRST (PENTING)
        info = {}

        # -------- INFO --------
        try:
            info = stock.info or {}
        except:
            pass

        # -------- PRICE (fallback) --------
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        # -------- PE --------
        pe = info.get("trailingPE")

        # -------- REVENUE (ANNUAL) --------
        revenue = None
        try:
            fin = stock.financials
            if not fin.empty:
                for row in fin.index:
                    if "Revenue" in row or "Sales" in row:
                        revenue = fin.loc[row].iloc[0]
                        break
        except:
            pass

        rows.append({
            "Ticker": ticker.replace(".JK", ""),
            "Price": price,
            "PE": pe,
            "Revenue": revenue
        })

    return pd.DataFrame(rows)

# ================= RUN =================
df = get_pe_revenue(TICKERS)

st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "Price": st.column_config.NumberColumn(format="%.0f"),
        "PE": st.column_config.NumberColumn(format="%.2f"),
        "Revenue": st.column_config.NumberColumn(format="%.2e")
    }
)

st.caption("Source: Yahoo Finance | PE bisa None jika EPS negatif / tidak tersedia")
