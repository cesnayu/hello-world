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

        # -------- PRICE (fallback) --------
        price = None
        try:
            info = stock.info or {}
            price = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
            )
        except:
            pass

        # -------- PE --------
        pe = info.get("trailingPE") if info else None

        # -------- REVENUE (annual fallback) --------
        revenue = None
        try:
            fin = stock.financials
            if not fin.empty:
                for col in fin.index:
                    if "Revenue" in col or "Sales" in col:
                        revenue = fin.loc[col].iloc[0]
                        break
        except:
            pass

        # 👉 tetap append walau ada None
        rows.append({
            "Ticker": ticker.replace(".JK", ""),
            "Price": price,
            "PE": pe,
            "Revenue": revenue
        })

    return pd.DataFrame(rows)

# ================= RUN =================
df = get_pe_revenue(TICKERS)

if df.empty:
    st.error("Yahoo Finance tidak mengembalikan data sama sekali")
else:
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Price": st.column_config.NumberColumn(format="%.0f"),
            "PE": st.column_config.NumberColumn(format="%.2f"),
            "Revenue": st.column_config.NumberColumn(format="%.2e")
        }
    )

    st.caption("Source: Yahoo Finance | PE bisa kosong jika EPS negatif / tidak tersedia")
