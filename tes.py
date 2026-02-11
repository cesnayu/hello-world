import streamlit as st
import yfinance as yf
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Market Movers Dashboard", layout="wide")

st.title("🏆 Market Movers: Gainers & Losers")
st.markdown("Dashboard ini memantau pergerakan harga saham LQ45 secara Real-Time.")

# --- 1. DAFTAR SAHAM (BISA DITAMBAH) ---
# Kita pakai LQ45 sebagai sampel agar loading tidak terlalu lama
LIST_SAHAM = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", 
    "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", 
    "BUKA.JK", "CPIN.JK", "EMTK.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", "HRUM.JK", 
    "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ITMG.JK", "JPFA.JK", 
    "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MERK.JK", "MIKA.JK", 
    "MTEL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", 
    "TBIG.JK", "TINS.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
]

# --- 2. FUNGSI AMBIL DATA MASSAL ---
@st.cache_data(ttl=300) # Cache data 5 menit biar gak lemot
def get_market_data(tickers):
    # Download data 5 hari terakhir untuk dapat Closing Price kemarin & hari ini
    data = yf.download(tickers, period="5d", group_by='ticker', progress=False)
    
    results = []
    
    for ticker in tickers:
        try:
            # Handling MultiIndex Dataframe
            if len(tickers) > 1:
                df = data[ticker]
            else:
                df = data
            
            # Pastikan data tidak kosong
            df = df.dropna()
            if len(df) < 2:
                continue
                
            # Ambil Harga Terakhir & Sebelumnya
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            
            # Hitung Persentase Perubahan
            change_pct = ((last_price - prev_price) / prev_price) * 100
            volume = df['Volume'].iloc[-1]
            
            results.append({
                "Ticker": ticker.replace(".JK", ""),
                "Harga": last_price,
                "Change (%)": change_pct,
                "Volume": volume
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(results)

# --- 3. SIDEBAR KONTROL ---
st.sidebar.header("⚙️ Pengaturan Tampilan")

# A. Slider Jumlah Baris (Ini jawaban dari request kamu)
# Kamu bisa geser dari 5 sampai Total Saham
jumlah_tampil = st.sidebar.slider(
    "Jumlah Saham Ditampilkan:", 
    min_value=5, 
    max_value=len(LIST_SAHAM), 
    value=10  # Default 10, tapi bisa digeser mentok kanan
)

# B. Pilihan Sortir
sort_option = st.sidebar.radio(
    "Urutkan Berdasarkan:",
    ["🚀 Top Gainers (Tertinggi)", "🔻 Top Losers (Terendah)", "🔤 Abjad (A-Z)"]
)

# --- 4. EKSEKUSI & TAMPILAN ---
if st.button("🔄 Refresh Data Pasar"):
    st.cache_data.clear() # Tombol reset cache untuk ambil data terbaru

with st.spinner("Sedang memindai pasar..."):
    df_market = get_market_data(LIST_SAHAM)

if not df_market.empty:
    # Logic Sorting
    if sort_option == "🚀 Top Gainers (Tertinggi)":
        df_sorted = df_market.sort_values(by="Change (%)", ascending=False)
    elif sort_option == "🔻 Top Losers (Terendah)":
        df_sorted = df_market.sort_values(by="Change (%)", ascending=True)
    else:
        df_sorted = df_market.sort_values(by="Ticker", ascending=True)
    
    # Logic Limiting (Potong Data sesuai Slider)
    df_final = df_sorted.head(jumlah_tampil).reset_index(drop=True)
    
    # --- TAMPILAN DATAFRAME CANTIK ---
    st.subheader(f"Menampilkan {jumlah_tampil} Saham - {sort_option}")
    
    # Fungsi pewarnaan (Hijau Positif, Merah Negatif)
    def highlight_change(val):
        color = '#d4f7d4' if val > 0 else '#f7d4d4' if val < 0 else ''
        return f'background-color: {color}'

    st.dataframe(
        df_final.style.format({
            "Harga": "Rp {:,.0f}",
            "Change (%)": "{:+.2f}%",
            "Volume": "{:,.0f}"
        }).applymap(highlight_change, subset=['Change (%)']),
        use_container_width=True,
        height=(35 * jumlah_tampil) + 40 # Tinggi tabel menyesuaikan jumlah data
    )
    
else:
    st.error("Gagal mengambil data pasar. Coba refresh.")
