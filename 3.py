import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Valuasi DCF Saham Indonesia", layout="wide")
st.title("💰 Dashboard Valuasi Saham (DCF Model - Versi Stabil)")

# --- SIDEBAR: ASUMSI ---
st.sidebar.header("⚙️ Asumsi Valuasi")
discount_rate = st.sidebar.slider("Discount Rate (%)", 5.0, 20.0, 10.0, 0.5) / 100
growth_rate_input = st.sidebar.slider("Growth Rate 5 Tahun (%)", 0.0, 30.0, 8.0, 1.0) / 100
terminal_growth = st.sidebar.slider("Terminal Growth (%)", 1.0, 5.0, 2.5, 0.1) / 100

# --- FUNGSI UTAMA YANG LEBIH KUAT ---
def get_dcf_value(ticker, disc_rate, growth_r, term_growth):
    try:
        stock = yf.Ticker(ticker)
        
        # 1. AMBIL INFO RINGKAS (LEBIH CEPAT & STABIL)
        # Menggunakan .info lebih aman daripada .cashflow untuk pemula
        info = stock.info
        
        if not info:
            return None, "Ticker tidak ditemukan / Koneksi Error"

        current_price = info.get('currentPrice') or info.get('regularMarketPreviousClose')
        if not current_price:
             return None, "Harga saham saat ini nol/kosong"

        shares = info.get('sharesOutstanding')
        
        # 2. CARI FREE CASH FLOW (FCF)
        # Prioritas 1: Ambil langsung dari Yahoo
        fcf = info.get('freeCashflow')
        
        # Prioritas 2: Hitung Manual jika Prioritas 1 kosong
        if fcf is None:
            operating_cashflow = info.get('operatingCashflow')
            # Capex biasanya tidak ada di info, harus ambil default 0 atau estimasi
            # Kita coba ambil dari financial statement jika info kosong
            if operating_cashflow:
                # Asumsi Capex sekitar 20% dari OCF jika data capex hilang (Rule of thumb kasar)
                # Ini untuk mencegah error.
                fcf = operating_cashflow * 0.8 
            else:
                 return None, "Data Cashflow Kosong di Yahoo Finance"

        # 3. PROYEKSIKAN NILAI
        # Proyeksi FCF 5 Tahun ke Depan
        future_fcfs = []
        for i in range(1, 6):
            val = fcf * ((1 + growth_r) ** i)
            future_fcfs.append(val)
            
        # Terminal Value
        terminal_value = (future_fcfs[-1] * (1 + term_growth)) / (disc_rate - term_growth)
        
        # Discount ke Present Value
        pv_fcfs = sum([val / ((1 + disc_rate) ** (i + 1)) for i, val in enumerate(future_fcfs)])
        pv_terminal = terminal_value / ((1 + disc_rate) ** 5)
        
        enterprise_value = pv_fcfs + pv_terminal
        
        # 4. EQUITY VALUE (EV + Cash - Debt)
        total_cash = info.get('totalCash', 0)
        total_debt = info.get('totalDebt', 0)
        
        equity_value = enterprise_value + total_cash - total_debt
        
        if not shares:
            return None, "Jumlah Lembar Saham (Shares) Kosong"
            
        fair_value = equity_value / shares
        
        # Hitung Potensi
        upside = ((fair_value - current_price) / current_price) * 100
        
        return {
            'Ticker': ticker.replace('.JK', ''),
            'Harga': current_price,
            'Nilai Wajar': fair_value,
            'Potensi (%)': upside,
            'FCF (Miliar)': fcf / 1_000_000_000
        }, None

    except Exception as e:
        return None, f"Error: {str(e)}"

# --- INPUT USER ---
# Default input string
default_tickers = "BBCA, TLKM, ASII, UNVR, ICBP, GOTO, BMRI"

input_saham = st.text_area("Masukkan Kode Saham (pisahkan koma):", value=default_tickers)

if st.button("🚀 Hitung Sekarang"):
    
    # Bersihkan Input
    tickers = [x.strip().upper() for x in input_saham.split(',')]
    # Tambah .JK otomatis
    tickers = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers]
    
    results = []
    failed = []
    
    # Progress Bar
    progress_bar = st.progress(0, text="Memulai...")

    for i, t in enumerate(tickers):
        progress_bar.progress(int((i / len(tickers)) * 100), text=f"Menganalisa {t}...")
        
        data, error = get_dcf_value(t, discount_rate, growth_rate_input, terminal_growth)
        
        if data:
            results.append(data)
        else:
            failed.append(f"❌ {t.replace('.JK','')}: {error}")
            
    progress_bar.empty()
    
    # TAMPILKAN HASIL
    if results:
        df = pd.DataFrame(results)
        
        # Styling
        st.subheader("📊 Hasil Valuasi")
        
        def color_rule(val):
            color = '#d1e7dd' if val > 0 else '#f8d7da'
            return f'background-color: {color}; color: black'

        st.dataframe(
            df.style.applymap(color_rule, subset=['Potensi (%)'])
              .format("{:,.0f}", subset=['Harga', 'Nilai Wajar'])
              .format("{:,.2f}%", subset=['Potensi (%)'])
              .format("{:,.2f} M", subset=['FCF (Miliar)']),
            use_container_width=True,
            hide_index=True
        )
    
    # TAMPILKAN YANG GAGAL (Supaya user tau kenapa sahamnya hilang)
    if failed:
        st.warning("⚠️ Beberapa saham tidak bisa dihitung (Data Yahoo Finance Kurang):")
        for f in failed:
            st.write(f)
