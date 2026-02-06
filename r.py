import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# ================= CONFIG =================
st.set_page_config(page_title="IHSG Quarterly Revenue & EPS", layout="wide")
st.title("📊 IHSG Quarterly Revenue & EPS (Last 3 Years)")

TICKERS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "TLKM.JK"
]

# ================= FUNCTION =================
def fetch_quarterly_data(tickers):
    all_data = []
    three_years_ago = datetime.now() - timedelta(days=3*365)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # -------- Revenue (auto detect column) --------
            fin = stock.quarterly_financials.T
            if fin.empty:
                continue

            revenue_col = None
            for col in fin.columns:
                if "Revenue" in col or "Sales" in col:
                    revenue_col = col
                    break

            if revenue_col is None:
                continue

            revenue = fin[[revenue_col]]

            # -------- EPS --------
            eps = stock.quarterly_earnings
            if eps.empty:
                continue

            # -------- Merge --------
            df = revenue.join(eps[['Earnings']], how="inner")
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= three_years_ago]

            if df.empty:
                continue

            df.reset_index(inplace=True)
            df.rename(columns={
                "index": "Quarter",
                revenue_col: "Revenue",
                "Earnings": "EPS"
            }, inplace=True)

            df["Ticker"] = ticker.replace(".JK", "")
            df = df[["Ticker", "Quarter", "Revenue", "EPS"]]

            all_data.append(df)

        except Exception as e:
            print(f"Error {ticker}: {e}")

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.sort_values(["Ticker", "Quarter"], ascending=[True, False], inplace=True)
    return final_df

# ================= RUN =================
df = fetch_quarterly_data(TICKERS)

if df.empty:
    st.warning("⚠️ Yahoo Finance tidak menyediakan quarterly financial untuk saham ini")
else:
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="%.2e"),
            "EPS": st.column_config.NumberColumn(format="%.2f")
        }
    )

    st.caption("Source: Yahoo Finance (IHSG)")
