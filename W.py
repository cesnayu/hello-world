import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Analyzer", layout="wide")

st.title("📈 Real-Time Stock Dashboard")

# 1. Input Ticker Saham (Contoh: ASII.JK untuk Astra, BBCA.JK untuk BCA)
ticker_input = st.text_input("Masukkan Kode Saham (Gunakan .JK untuk saham Indonesia):", "ASII.JK")

if ticker_input:
    try:
        # Ambil data dari Yahoo Finance
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # Ambil Laporan Keuangan (Financials) untuk Revenue
        df_financials = stock.financials
        
        # Ambil Data Revenue (biasanya baris pertama di laporan laba rugi)
        if "Total Revenue" in df_financials.index:
            rev_now = df_financials.loc["Total Revenue"].iloc[0]   # Tahun terbaru
            rev_prev = df_financials.loc["Total Revenue"].iloc[1]  # Tahun sebelumnya
            rev_delta = rev_now - rev_prev
        else:
            rev_now = rev_prev = rev_delta = 0

        # Ambil PER (Price to Earning Ratio)
        # yfinance terkadang mengembalikan None jika data tidak tersedia
        per_now = info.get("forwardPE") or info.get("trailingPE") or 0
        
        # 2. Tampilkan Metric
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label=f"Price to Earning Ratio (PER) - {ticker_input}",
                value=f"{per_now:.2f}x" if per_now != 0 else "N/A",
                delta="Cek valuasi" if per_now != 0 else None
            )

        with col2:
            st.metric(
                label="Annual Revenue (Latest vs Prev)",
                value=f"{rev_now:,.0f}",
                delta=f"{rev_delta:,.0f}"
            )

        # 3. Grafik Pendapatan
        st.subheader(f"History Revenue {ticker_input}")
        st.bar_chart(df_financials.loc["Total Revenue"])

    except Exception as e:
        st.error(f"Data tidak ditemukan atau error: {e}")
