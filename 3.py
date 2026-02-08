import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Valuasi DCF Saham Indonesia", layout="wide")

# --- JUDUL ---
st.title("💰 Dashboard Valuasi Saham (DCF Model)")
st.markdown("""
Aplikasi ini menghitung **Nilai Wajar (Intrinsic Value)** menggunakan metode **Discounted Cash Flow (DCF)** sederhana.
*Masukkan kode saham tanpa perlu '.JK' (contoh: bbca, tlkm, indf).*
""")

# --- SIDEBAR: ASUMSI DCF (PENTING!) ---
st.sidebar.header("⚙️ Asumsi Valuasi")
st.sidebar.info("DCF sangat sensitif terhadap angka di bawah ini. Sesuaikan dengan analisamu.")

# 1. Discount Rate (WACC / Required Return)
discount_rate = st.sidebar.slider(
    "Discount Rate (Required Return)", 
    min_value=5.0, max_value=20.0, value=10.0, step=0.5,
    help="Berapa return minimal yang kamu harapkan? (Biasanya 10-12% untuk Indonesia)"
) / 100

# 2. Growth Rate (Pertumbuhan FCF 5 Tahun ke Depan)
growth_rate_input = st.sidebar.slider(
    "Estimasi Growth Rate (5 Thn)", 
    min_value=0.0, max_value=30.0, value=8.0, step=1.0,
    help="Seberapa cepat perusahaan tumbuh tiap tahun?"
) / 100

# 3. Terminal Growth (Pertumbuhan Abadi)
terminal_growth = st.sidebar.slider(
    "Terminal Growth Rate (Selamanya)", 
    min_value=1.0, max_value=5.0, value=2.5, step=0.1,
    help="Pertumbuhan jangka panjang setelah tahun ke-5 (biasanya ikuti inflasi ~3%)"
) / 100

# --- FUNGSI UTAMA ---
def calculate_dcf(ticker, disc_rate, growth_r, term_growth):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. Ambil Data Keuangan
        # Coba ambil cashflow dari statement
        cf = stock.cashflow
        bs = stock.balance_sheet
        
        if cf.empty or bs.empty:
            return None, "Data Laporan Keuangan Kosong"

        # 2. Hitung Free Cash Flow (FCF) Terakhir (TTM jika mungkin, atau tahun terakhir)
        # FCF = Operating Cash Flow - Capital Expenditure
        try:
            # Mengambil kolom terbaru (tahun terakhir report)
            op_cashflow = cf.loc['Operating Cash Flow'].iloc[0]
            capex = cf.loc['Capital Expenditure'].iloc[0] 
            
            # Capex di Yahoo biasanya minus, jadi kita tambah (atau kurangi absolutnya)
            # Rumus umum: OCF - Capex. Karena Capex minus, jadi OCF + Capex
            fcf_last = op_cashflow + capex 
        except KeyError:
            return None, "Gagal hitung FCF (Data Op.Cashflow/Capex hilang)"

        # 3. Proyeksi FCF 5 Tahun ke Depan
        future_fcfs = []
        for i in range(1, 6):
            fcf_proj = fcf_last * ((1 + growth_r) ** i)
            future_fcfs.append(fcf_proj)
            
        # 4. Hitung Terminal Value (Nilai di Akhir Tahun ke-5)
        # Rumus Gordon Growth Model untuk Terminal Value
        terminal_value = (future_fcfs[-1] * (1 + term_growth)) / (disc_rate - term_growth)
        
        # 5. Discount ke Present Value (PV)
        pv_fcfs = 0
        for i, val in enumerate(future_fcfs):
            pv_fcfs += val / ((1 + disc_rate) ** (i + 1))
            
        pv_terminal = terminal_value / ((1 + disc_rate) ** 5)
        
        enterprise_value = pv_fcfs + pv_terminal
        
        # 6. Hitung Equity Value (EV + Cash - Debt)
        try:
            total_cash = bs.loc['Cash And Cash Equivalents'].iloc[0]
            total_debt = bs.loc['Total Debt'].iloc[0]
        except:
            # Fallback jika item spesifik tidak ada, pakai info
            total_cash = info.get('totalCash', 0)
            total_debt = info.get('totalDebt', 0)
            
        equity_value = enterprise_value + total_cash - total_debt
        
        # 7. Bagi dengan Jumlah Saham Beredar
        shares = info.get('sharesOutstanding', 0)
        if shares == 0:
            return None, "Data Jumlah Saham (Shares Outstanding) 0"
            
        fair_value = equity_value / shares
        current_price = info.get('currentPrice', 0)
        
        if current_price == 0:
             # Coba ambil history last close kalau info kosong
             hist = stock.history(period="1d")
             if not hist.empty:
                 current_price = hist['Close'].iloc[0]
             else:
                 return None, "Harga saat ini tidak ditemukan"

        # Margin of Safety (Upside/Downside)
        upside = ((fair_value - current_price) / current_price) * 100
        
        return {
            'Ticker': ticker.replace('.JK', ''),
            'Harga Saat Ini': current_price,
            'Nilai Wajar (DCF)': fair_value,
            'Potensi (Upside)': upside,
            'FCF Terakhir (Miliar)': fcf_last / 1_000_000_000
        }, None

    except Exception as e:
        return None, f"Error sistem: {str(e)}"

# --- INPUT USER ---
default_input = "BBCA, TLKM, UNVR, ASII, GOTO"
user_input = st.text_area("Masukkan Kode Saham (pisahkan koma):", value=default_input)

if st.button("🚀 Hitung Valuasi DCF"):
    # Parsing Input
    tickers_raw = [x.strip().upper() for x in user_input.split(',')]
    tickers_fixed = []
    
    # Logic nambahin .JK otomatis
    for t in tickers_raw:
        if not t.endswith(".JK"):
            tickers_fixed.append(f"{t}.JK")
        else:
            tickers_fixed.append(t)
            
    results = []
    errors = []
    
    progress_bar = st.progress(0, text="Memulai perhitungan...")
    
    for i, tick in enumerate(tickers_fixed):
        progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menghitung {tick}...")
        
        data, err = calculate_dcf(tick, discount_rate, growth_rate_input, terminal_growth)
        
        if data:
            results.append(data)
        else:
            # Simpan error tapi jangan stop app
            errors.append(f"{tick.replace('.JK','')}: {err}")
            
    progress_bar.empty()
    
    # --- TAMPILKAN HASIL ---
    if results:
        df_res = pd.DataFrame(results)
        
        # Format Tampilan Streamlit
        st.subheader("📊 Hasil Perhitungan")
        
        # Highlight Logic
        def color_upside(val):
            color = '#d4edda' if val > 0 else '#f8d7da' # Hijau jika Undervalued, Merah jika Overvalued
            return f'background-color: {color}; color: black'

        st.dataframe(
            df_res.style.applymap(color_upside, subset=['Potensi (Upside)'])
                  .format("{:,.0f}", subset=['Harga Saat Ini', 'Nilai Wajar (DCF)'])
                  .format("{:,.2f}%", subset=['Potensi (Upside)'])
                  .format("{:,.2f} M", subset=['FCF Terakhir (Miliar)']),
            use_container_width=True,
            height=400
        )
        
        # Kes
