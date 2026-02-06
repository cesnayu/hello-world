import yfinance as yf
import pandas as pd
import streamlit as st

# ================= CONFIG =================
st.set_page_config(page_title="5D Gain & Loser Screener", layout="wide")
st.title("📈 5-Day Gain & Loser Screener")

# 👉 ISI SAHAM SENDIRI
TICKERS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "TLKM.JK",
    "ASII.JK"
]

# ================= USER FILTER =================
min_volume = st.number_input(
    "Minimum Average Volume (5 hari)",
    min_value=0,
    value=1_000_000,
    step=500_000
)

# ================= FUNCTION =================
def get_5d_returns(tickers):
    rows = []

    for ticker in tickers:
        try:
            df = yf.download(
                ticker,
                period="6d",
                interval="1d",
                progress=False
            )

            if df.empty or len(df) < 6:
                continue

            # Daily return (%)
            ret = df["Close"].pct_change().dropna() * 100
            ret = ret[-5:]

            total_return = ret.sum()
            avg_volume = df["Volume"].tail(5).mean()

            rows.append({
                "Ticker": ticker.replace(".JK", ""),
                "Day-5": ret.iloc[0],
                "Day-4": ret.iloc[1],
                "Day-3": ret.iloc[2],
                "Day-2": ret.iloc[3],
                "Day-1": ret.iloc[4],
                "Total 5D (%)": total_return,
                "Status": "GAIN" if total_return > 0 else "LOSS",
                "Avg Volume": avg_volume
            })

        except Exception as e:
            print(f"Error {ticker}: {e}")

    return pd.DataFrame(rows)

# ================= RUN =================
df = get_5d_returns(TICKERS)

# Filter volume
df = df[df["Avg Volume"] >= min_volume]

# ================= DISPLAY =================
st.dataframe(
    df.sort_values("Total 5D (%)", ascending=False),
    use_container_width=True,
    column_config={
        "Day-5": st.column_config.NumberColumn(format="%.2f%%"),
        "Day-4": st.column_config.NumberColumn(format="%.2f%%"),
        "Day-3": st.column_config.NumberColumn(format="%.2f%%"),
        "Day-2": st.column_config.NumberColumn(format="%.2f%%"),
        "Day-1": st.column_config.NumberColumn(format="%.2f%%"),
        "Total 5D (%)": st.column_config.NumberColumn(format="%.2f%%"),
        "Avg Volume": st.column_config.NumberColumn(format="%.0f")
    }
)

st.caption("Source: Yahoo Finance | 5 trading days | Sort kolom langsung di tabel")
