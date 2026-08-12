import streamlit as st
import yfinance as yf
import pandas as pd
import time
from pathlib import Path
from datetime import datetime, timedelta

# ==================== PENGATURAN ====================
CACHE_DIR = Path("stock_cache")
CACHE_MAX_AGE_HOURS = 1          # Cache usang setelah berapa jam
DELAY_ANTAR_REQUEST = 1.2        # Jeda antar ticker (detik)
# ====================================================

CACHE_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Cek Drawdown 1 Bulan",
    page_icon="📉",
    layout="wide"
)

st.title("📉 Cek Jarak dari Titik Tertinggi 1 Bulan")
st.caption("Data dari Yahoo Finance • Disimpan lokal supaya tidak spam request")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Pengaturan")
    force_refresh = st.checkbox("Paksa ambil data baru (abaikan cache)", value=False)
    max_age = st.slider("Cache berlaku (jam)", 0.5, 24.0, float(CACHE_MAX_AGE_HOURS), 0.5)
    st.markdown("---")
    st.markdown("**Contoh ticker:**")
    st.code("BBCA.JK\nBBRI.JK\nTLKM.JK\nASII.JK\nGOTO.JK\nAAPL\nMSFT")

# ---------- Input ----------
default_tickers = "BBCA.JK\nBBRI.JK\nTLKM.JK\nASII.JK\nGOTO.JK"
tickers_input = st.text_area(
    "Masukkan ticker (satu per baris)",
    value=default_tickers,
    height=150,
    help="Saham Indonesia pakai .JK (contoh: BBCA.JK)"
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("🚀 Jalankan", type="primary", use_container_width=True)


# ---------- Fungsi cache & fetch ----------
def is_cache_valid(filepath: Path, max_age_hours: float) -> bool:
    if not filepath.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
    return age < timedelta(hours=max_age_hours)


def get_stock_data(ticker: str, force: bool, max_age_hours: float) -> pd.DataFrame | None:
    cache_file = CACHE_DIR / f"{ticker.replace('.', '_')}.csv"

    if not force and is_cache_valid(cache_file, max_age_hours):
        return pd.read_csv(cache_file, index_col=0, parse_dates=True)

    try:
        df = yf.download(
            ticker,
            period="1mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if df.empty:
            return None

        # Rapikan kolom multi-index kalau ada
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.to_csv(cache_file)
        return df
    except Exception:
        if cache_file.exists():
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        return None


def hitung_drawdown(df: pd.DataFrame) -> dict | None:
    if df is None or df.empty:
        return None

    high = df["High"]
    close = df["Close"]

    high_1m = float(high.max())
    current = float(close.iloc[-1])
    pct = ((current - high_1m) / high_1m) * 100
    tanggal_high = high.idxmax().strftime("%Y-%m-%d")

    return {
        "high_1m": high_1m,
        "current": current,
        "pct": pct,
        "tanggal_high": tanggal_high,
    }


# ---------- Main logic ----------
if run_button:
    tickers = [t.strip().upper() for t in tickers_input.splitlines() if t.strip()]
    
    if not tickers:
        st.warning("Masukkan minimal 1 ticker.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()
    results = []

    for i, ticker in enumerate(tickers):
        status.info(f"Memproses **{ticker}** ({i+1}/{len(tickers)})...")
        progress.progress((i) / len(tickers))

        df = get_stock_data(ticker, force_refresh, max_age)
        info = hitung_drawdown(df) if df is not None else None

        if info:
            results.append({
                "Ticker": ticker,
                "Harga Sekarang": round(info["current"], 2),
                "High 1 Bulan": round(info["high_1m"], 2),
                "Tanggal High": info["tanggal_high"],
                "% dari High": round(info["pct"], 2),
            })
        else:
            results.append({
                "Ticker": ticker,
                "Harga Sekarang": None,
                "High 1 Bulan": None,
                "Tanggal High": "-",
                "% dari High": None,
            })

        if i < len(tickers) - 1:
            time.sleep(DELAY_ANTAR_REQUEST)

    progress.progress(1.0)
    status.success("Selesai!")

    # ---------- Tampilkan hasil ----------
    df_hasil = pd.DataFrame(results)
    df_hasil = df_hasil.sort_values("% dari High", na_position="last")

    st.subheader("Hasil")
    
    # Format % dengan warna
    def color_pct(val):
        if pd.isna(val):
            return ""
        if val <= -10:
            color = "#ff4b4b"
        elif val < 0:
            color = "#ffa500"
        else:
            color = "#00c853"
        return f"color: {color}; font-weight: bold"

    st.dataframe(
        df_hasil.style.map(color_pct, subset=["% dari High"])
               .format({
                   "Harga Sekarang": "{:.2f}",
                   "High 1 Bulan": "{:.2f}",
                   "% dari High": "{:+.2f}%",
               }, na_rep="-"),
        use_container_width=True,
        hide_index=True
    )

    # Ringkasan cepat
    valid = df_hasil.dropna(subset=["% dari High"])
    if not valid.empty:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Paling dalam", f"{valid.iloc[0]['Ticker']}", f"{valid.iloc[0]['% dari High']:+.2f}%")
        col_b.metric("Rata-rata", f"{valid['% dari High'].mean():+.2f}%")
        col_c.metric("Paling dekat high", f"{valid.iloc[-1]['Ticker']}", f"{valid.iloc[-1]['% dari High']:+.2f}%")

    st.caption(f"Cache disimpan di folder `{CACHE_DIR.resolve()}` • Data di-refresh otomatis setelah {max_age} jam")
