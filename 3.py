import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config("DCF Valuation Dashboard", layout="wide")

st.title("📊 DCF Valuation Dashboard (Auto IHSG)")
st.caption("Masukkan ticker tanpa imbuhan .JK | contoh: INDF BBCA TLKM")

# ================= INPUT =================
tickers_input = st.text_input("Ticker Saham", "INDF BBCA TLKM")

growth_rate = st.slider("Growth Rate 5 Tahun (%)", 2, 15, 7) / 100
terminal_growth = st.slider("Terminal Growth (%)", 1, 6, 3) / 100
discount_rate = st.slider("Discount Rate / WACC (%)", 6, 15, 10) / 100

tickers = [t.upper() + ".JK" for t in tickers_input.split()]

results = []

# ================= PROCESS =================
for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)

        price = stock.history(period="1d")["Close"].iloc[-1]

        cashflow = stock.cashflow
        fcf = cashflow.loc["Free Cash Flow"].dropna()

        if len(fcf) < 1:
            continue

        base_fcf = fcf.iloc[0]

        shares = stock.info.get("sharesOutstanding", None)
        if not shares:
            continue

        # ---- DCF Projection ----
        projected_fcf = []
        for i in range(1, 6):
            projected_fcf.append(base_fcf * (1 + growth_rate) ** i)

        discounted_fcf = [
            fcf / (1 + discount_rate) ** i
            for i, fcf in enumerate(projected_fcf, start=1)
        ]

        terminal_value = (
            projected_fcf[-1] * (1 + terminal_growth)
        ) / (discount_rate - terminal_growth)

        discounted_terminal = terminal_value / (1 + discount_rate) ** 5

        enterprise_value = sum(discounted_fcf) + discounted_terminal
        fair_value = enterprise_value / shares

        results.append({
            "Ticker": ticker.replace(".JK", ""),
            "Harga Saat Ini": round(price, 0),
            "Nilai Wajar (DCF)": round(fair_value, 0),
            "Upside (%)": round((fair_value / price - 1) * 100, 1)
        })

    except Exception as e:
        st.warning(f"Gagal proses {ticker}")

# ================= OUTPUT =================
if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    st.bar_chart(
        df.set_index("Ticker")[["Harga Saat Ini", "Nilai Wajar (DCF)"]]
    )
else:
    st.info("Tidak ada data yang bisa diproses.")
