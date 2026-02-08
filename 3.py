import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Valuasi Saham (Input Manual)", layout="wide")

st.title("🧮 Smart Valuation Dashboard (Input Presisi)")
st.markdown("""
Masukkan asumsi valuasi dengan mengetik angka secara manual (bukan digeser).
* **Bank:** Menggunakan DDM.
* **Non-Bank:** Menggunakan DCF.
""")

# --- SIDEBAR: ASUMSI (INPUT ANGKA MANUAL) ---
st.sidebar.header("⚙️ Input Asumsi (%)")
st.sidebar.info("Ketik angka persentase di bawah ini.")

# Menggunakan number_input pengganti slider
# step=0.1 artinya setiap klik panah naik/turun 0.1
# format="%.2f" artinya menampilkan 2 angka belakang koma

discount_rate_pct = st.sidebar.number_input(
    "Discount Rate / Cost of Equity (%)", 
    min_value=1.0, 
    max_value=50.0, 
    value=12.0, 
    step=0.1,
    format="%.2f",
    help="Return minimal yang diharapkan investor."
)

growth_rate_pct = st.sidebar.number_input(
    "Growth Rate Tahunan (%)", 
    min_value=-10.0, 
    max_value=50.0, 
    value=5.0, 
    step=0.1,
    format="%.2f",
    help="Estimasi pertumbuhan laba/cashflow per tahun."
)

terminal_growth_pct = st.sidebar.number_input(
    "Terminal Growth (Khusus DCF) (%)", 
    min_value=0.0, 
    max_value=10.0, 
    value=2.5, 
    step=0.1,
    format="%.2f",
    help="Pertumbuhan jangka panjang selamanya (biasanya ikut inflasi 2-3%)."
)

# Konversi ke desimal untuk rumus matematika
disc_rate = discount_rate_pct / 100
growth_r = growth_rate_pct / 100
term_growth = terminal_growth_pct / 100

# --- LIST BANK ---
LIST_BANK = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'BRIS', 'BBTN', 'ARTO', 'BDMN', 'BNGA', 'PNBN']

# --- FUNGSI HITUNG ---
def calculate_smart_valuation(ticker_raw, disc, grow, term):
    ticker_clean = ticker_raw.upper().replace('.JK', '').strip()
    ticker_yf = f"{ticker_clean}.JK"
    
    try:
        stock = yf.Ticker(ticker_yf)
        info = stock.info
        
        if not info: return None, "Data Tidak Ditemukan"
            
        curr_price = info.get('currentPrice') or info.get('regularMarketPreviousClose')
        if not curr_price: return None, "Harga saham kosong"

        # --- LOGIKA PEMILIHAN METODE ---
        is_bank = ticker_clean in LIST_BANK
        method = "DDM (Dividen)" if is_bank else "DCF (Cashflow)"
        
        fair_value = 0
        metric_used = 0 
        
        # 1. METODE DDM (BANK)
        if is_bank:
            if disc <= grow:
                return None, "Error: Discount Rate harus > Growth Rate"

            last_dividend = info.get('dividendRate')
            if not last_dividend: return None, "Tidak ada Dividen (DDM Gagal)"
            
            metric_used = last_dividend
            next_dividend = last_dividend * (1 + grow)
            fair_value = next_dividend / (disc - grow)

        # 2. METODE DCF (NON-BANK)
        else:
            shares = info.get('sharesOutstanding')
            fcf = info.get('freeCashflow')
            
            # Fallback jika FCF kosong
            if fcf is None:
                ocf = info.get('operatingCashflow')
                if ocf: fcf = ocf * 0.7 
            
            if not fcf or not shares: return None, "Data Cashflow/Shares Kosong"
            
            metric_used = fcf / 1_000_000_000 # Miliar
            
            # Proyeksi
            future_fcfs = [fcf * ((1 + grow) ** i) for i in range(1, 6)]
            term_val = (future_fcfs[-1] * (1 + term)) / (disc - term)
            
            pv_total = sum([val / ((1 + disc) ** (i + 1)) for i, val in enumerate(future_fcfs)])
            pv_total += term_val / ((1 + disc) ** 5)
            
            cash = info.get('totalCash', 0) or 0
            debt = info.get('totalDebt', 0) or 0
            
            equity_val = pv_total + cash - debt
            fair_value = equity_val / shares

        # Hitung Potensi
        upside = ((fair_value - curr_price) / curr_price) * 100
        
        return {
            'Ticker': ticker_clean,
            'Metode': method,
            'Harga Pasar': curr_price,
            'Nilai Wajar': fair_value,
            'Potensi (%)': upside,
            'Basis Data': metric_used
        }, None

    except Exception as e:
        return None, str(e)

# --- UI UTAMA ---
default_list = "BMRI, BBRI, BBCA, TLKM, ASII, UNVR, ADRO"
input_user = st.text_area("Masukkan Saham:", value=default_list)

if st.button("🚀 Hitung Valuasi"):
    tickers = [x.strip() for x in input_user.split(',')]
    
    results = []
    errors = []
    
    bar = st.progress(0, "Menganalisa...")
