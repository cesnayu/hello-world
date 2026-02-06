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
                period="7d",     # buffer lebih aman
                interval="1d",
                progress=False
            )

            if df.empty or len(df) < 6:
                continue

            close = df["Close"].dropna()
            volume = df["Volume"].dropna()

            if len(close) < 6 or len(volume) < 5:
                continue

            ret = close.pct_change().dropna().tail(5) * 100
            avg_volume = volume.tail(5).mean()
            total_return = ret.sum()

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

    # ✅ RETURN DENGAN KOLUM TETAP
    columns = [
        "Ticker", "Day-5", "Day-4", "Day-3",
        "Day-2", "Day-1", "Total 5D (%)",
        "Status", "Avg Volume"
    ]

    return pd.DataFrame(rows, columns=columns)

# ================= RUN =================
df = get_5d_returns(TICKERS)

# ================= SAFETY CHECK =================
if df.emp:
