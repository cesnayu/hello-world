import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Custom Stock Screener", layout="wide")

st.title("🎯 Dashboard Screening Fundamental (Kriteria Sendiri)")
st.markdown("Masukkan standar angka yang kamu mau (ketik manual), sistem akan mencari saham yang lolos kriteria tersebut.")

# --- SIDEBAR: INPUT KRITERIA (ANGKA MANUAL) ---
st.sidebar.header("⚙️ Tentukan Standar Kamu")
st.sidebar.caption("Ketik angka batas yang kamu inginkan.")

# 1. Target P/E Ratio (Maksimal)
target_pe = st.sidebar.number_input(
    "Maksimal P/E Ratio (x)", 
    min_value=0.0, max_value=100.0, value=15.0, step=0.1,
    help="Saham dianggap murah jika P/E di bawah angka ini."
)

# 2. Target P/S Ratio (Maksimal)
target_ps = st.sidebar.number_input(
    "Maksimal P/S Ratio (x)", 
    min_value=0.0, max_value=50.0, value=2.0, step=0.1,
    help="Saham dianggap murah jika P/S di bawah angka ini."
)

# 3. Target ROE (Minimal)
target_roe = st.sidebar.number_input(
    "Minimal ROE (%)", 
    min_value=0.0, max_value=100.0, value=10.0, step=0.5,
    help="Perusahaan dianggap profitabel jika ROE di atas angka ini."
)

# 4. Target DER (Maksimal)
target_der = st.sidebar.number_input(
    "Maksimal DER / Utang (%)", 
    min_value=0.0, max_value=500.0, value=100.0, step=10.0,
    help="Perusahaan dianggap aman jika Utang di bawah angka ini."
)

# --- FUNGSI AMBIL DATA ---
def get_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Sedang mengambil data...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Cek {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Ambil data (Handle jika kosong)
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            price = info.get('currentPrice')
            
            # Konversi ROE ke Persen
            if roe is not None: roe = roe * 100

            # Hitung Skor Kelulusan (Berapa kriteria yang lolos?)
            score = 0
            status_pe = "❌"
            status_roe = "❌"
            
            # Cek P/E
            if pe and pe <= target_pe: 
                score += 1
                status_pe = "✅"
                
            # Cek P/S
            if ps and ps <= target_ps: 
                score += 1
                
            # Cek ROE
            if roe and roe >= target_roe: 
                score += 1
                status_roe = "✅"
                
            # Cek DER
            if der and der <= target_der: 
                score += 1

            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Harga': price,
                'Skor (Max 4)': score, # Total kriteria yang terpenuhi
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except:
            continue
            
    progress_bar.empty()
    return pd.DataFrame(data)

# --- UI UTAMA ---
default_tickers = "BBCA, BBRI, BMRI, BBNI, ASII, TLKM, UNVR, ICBP, ADRO, PTBA, ITMG, GOTO, SIDO"
input_saham = st.text_area("Masukkan Kode Saham:", value=default_tickers)

if st.button("🔍 Cek Kriteria Saya"):
    if not input_saham:
        st.warning("Masukkan kode saham dulu.")
    else:
        df = get_data(input_saham)
        
        if not df.empty:
            # Urutkan berdasarkan SKOR TERTINGGI (Paling sesuai kriteria kamu)
            df = df.sort_values(by=['Skor (Max 4)', 'ROE (%)'], ascending=[False, False])
            
            st.success(f"Berhasil menganalisa {len(df)} saham berdasarkan kriteria kamu.")
            
            # --- 1. TAMPILAN SCORE CARD ---
            st.subheader("🏆 Saham Paling Lolos Kriteria")
            st.caption(f"Kriteria Kamu: P/E < {target_pe}, ROE > {target_roe}%, DER < {target_der}%, P/S < {target_ps}")
            
            # Highlight Warna Warni berdasarkan Kriteria User
            def highlight_custom_rules(row):
                styles = [''] * len(row)
                
                # Index kolom di DataFrame (sesuaikan manual atau pakai nama kolom)
                # Kita pakai logika sederhana: Buat styler function terpisah per kolom
                return styles

            # Konfigurasi Kolom
            column_config = {
                "Kode": st.column_config.TextColumn("Ticker", width="small"),
                "Skor (Max 4)": st.column_config.ProgressColumn(
                    "Kecocokan", 
                    format="%d/4", 
                    min_value=0, 
                    max_value=4,
                    help="Berapa banyak kriteria kamu yang terpenuhi?"
                ),
                "P/E Ratio (x)": st.column_config.NumberColumn("P/E", format="%.2fx"),
                "P/S Ratio (x)": st.column_config.NumberColumn("P/S", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "DER (%)": st.column_config.NumberColumn("DER", format="%.2f%%"),
            }

            # --- LOGIC WARNA BARIS ---
            # Kita warnai background cell Hijau jika lolos kriteria user, Merah jika gagal
            
            def color_pe(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_pe else 'background-color: #f8d7da; color: black'

            def color_ps(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_ps else 'background-color: #f8d7da; color: black'

            def color_roe(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val >= target_roe else 'background-color: #f8d7da; color: black'

            def color_der(val):
                if pd.isna(val): return ''
                return 'background-color: #d4edda; color: black' if val <= target_der else 'background-color: #f8d7da; color: black'

            # Apply Style
            styled_df = df.style.applymap(color_pe, subset=['P/E Ratio (x)']) \
                                .applymap(color_ps, subset=['P/S Ratio (x)']) \
                                .applymap(color_roe, subset=['ROE (%)']) \
                                .applymap(color_der, subset=['DER (%)']) \
                                .format("{:.2f}", subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)'])

            st.dataframe(
                styled_df,
                column_config=column_config,
                use_container_width=True,
                height=600,
                hide_index=True
            )
            
            # Penjelasan Warna
            st.info("""
            **Cara Baca Tabel:**
            * 🟩 **Hijau:** Angka masuk dalam kriteria yang kamu ketik di sidebar.
            * 🟥 **Merah:** Angka tidak lolos kriteria kamu.
            * **Skor 4/4:** Artinya saham ini sempurna sesuai keinginanmu.
            """)
            
        else:
            st.error("Data tidak ditemukan.")
