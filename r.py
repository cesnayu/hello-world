import yfinance as yf
import pandas as pd
import streamlit as st

# ================= CONFIG =================
st.set_page_config(page_title="PE & Revenue Screener", layout="wide")
st.title("📊 PE Ratio & Revenue Screener")

# 👉 EDIT SAHAM DI SINI
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
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # --- Price ---
            price = info.get("currentPrice")

            # --- PE ---
            pe = info.get("trailingPE")

            # --- Revenue (Annual) ---
            fin = stock.financials
            revenue = None
            if not fin.empty:
                for col in fin.columns:
                    if "Revenue" in col or "Sales" in col:
                        revenue = fin.loc[col].iloc[0]
                        break

            rows.append({
                "Ticker": ticker.replace(".JK", ""),
                "Price": price,
                "PE": pe,
                "Revenue": revenue
            })

        except Exception as e:
            print(f"Error {ticker}: {e}")

    return pd.DataFrame(rows)

# ================= RUN =================
df = get_pe_revenue(TICKERS)

if df.empty:
    st.warning("Data tidak tersedia")
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

    st.caption("Source: Yahoo Finance | Annual Revenue | Trailing PE")
