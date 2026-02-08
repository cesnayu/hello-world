import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Stock Comparison Dashboard", layout="wide")

st.title("⚖️ Stock Perbandingan Fundamental")
st.markdown("Bandingkan **P/E, P/S, ROE, DER, dan EPS** dari banyak saham sekaligus dengan filter custom.")

# --- INPUT SAHAM ---
default_tickers = "BREN, BBCA, DSSA, BBRI, TPIA, DCII, BYAN, AMMN, BMRI, TLKM, ASII, MORA, SRAJ, CUAN, BRPT, BBNI, PANI, BNLI, BRMS, CDIA, DNET, IMPC, FILM, MPRO, BRIS, ICBP, HMSP, BUMI, EMAS, UNTR, ANTM, NCKL, SMMA, ADMR, CASA, UNVR, RISE, CPIN, MLPT, AMRT, MDKA, ISAT, MBMA, GOTO, INCO, AADI, INDF, PTRO, BELI, ADRO, EXCL, TCPI, KLBF, EMTK, MYOR, PGAS, INKP, PGUN, PGEO, GEMS, MTEL, BNGA, CMRY, ARCI, TBIG, MEGA, SILO, MEDC, GIAA, SOHO, VKTR, CBDK, MIKA, NISP, JPFA, GGRM, TOWR, BBHI, ENRG, TAPG, SUPA, BUVA, PTBA, BINA, COIN, AVIA, JSMR, AKRA, NSSS, PNBN, ITMG, BDMN, ARKO, MDIY, TINS, BSIM, INTP, JARR, BKSL, BTPN, ARTO, FAPA, MKPI, RMKE, SRTG, TKIM, MAPA, MSIN, MAPI, RLCO, HEAL, BSDE, KPIG, CITA, PWON, BNBR, APIC, BBTN, SMGR, RAJA, POLU, LIFE, BNII, INDY, CTRA, SMAR, SCMA, SSMS, CARE, ULTJ, SIDO, DSNG, BBSI, BUKA, AALI, RATU, BBKP, HRUM, CMNT, SGRO, PSAB, JRPT, YUPI, STAA, STTP, GOOD, MCOL, WIFI, AUTO, TSPC"
input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", value=default_tickers, height=100)

# --- FILTER SECTION ---
st.sidebar.header("🎯 Filter Kriteria Saham")
st.sidebar.markdown("*Kosongkan filter yang tidak ingin dipakai*")

with st.sidebar:
    st.subheader("📊 P/E Ratio")
    col1, col2 = st.columns(2)
    with col1:
        pe_min = st.number_input("Min P/E", value=None, min_value=0.0, step=1.0, help="Contoh: 0")
    with col2:
        pe_max = st.number_input("Max P/E", value=None, min_value=0.0, step=1.0, help="Contoh: 50")
    
    st.subheader("📊 P/S Ratio")
    col1, col2 = st.columns(2)
    with col1:
        ps_min = st.number_input("Min P/S", value=None, min_value=0.0, step=0.1, help="Contoh: 0")
    with col2:
        ps_max = st.number_input("Max P/S", value=None, min_value=0.0, step=0.1, help="Contoh: 5")
    
    st.subheader("📈 ROE (%)")
    col1, col2 = st.columns(2)
    with col1:
        roe_min = st.number_input("Min ROE", value=None, min_value=-100.0, step=1.0, help="Contoh: 15")
    with col2:
        roe_max = st.number_input("Max ROE", value=None, min_value=-100.0, step=1.0, help="Contoh: 100")
    
    st.subheader("💰 DER (%)")
    col1, col2 = st.columns(2)
    with col1:
        der_min = st.number_input("Min DER", value=None, min_value=0.0, step=10.0, help="Contoh: 0")
    with col2:
        der_max = st.number_input("Max DER", value=None, min_value=0.0, step=10.0, help="Contoh: 150")
    
    st.subheader("💵 EPS (Rp)")
    col1, col2 = st.columns(2)
    with col1:
        eps_min = st.number_input("Min EPS", value=None, step=10.0, help="Contoh: 0")
    with col2:
        eps_max = st.number_input("Max EPS", value=None, step=10.0, help="Contoh: 1000")
    
    st.subheader("💲 Harga Saham")
    col1, col2 = st.columns(2)
    with col1:
        price_min = st.number_input("Min Harga", value=None, min_value=0.0, step=100.0, help="Contoh: 0")
    with col2:
        price_max = st.number_input("Max Harga", value=None, min_value=0.0, step=100.0, help="Contoh: 10000")
    
    st.divider()
    if st.button("🔄 Reset Semua Filter", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.markdown("### 💡 Tips Filter:")
    st.markdown("""
    **Kriteria Saham Bagus:**
    - P/E: 0 - 15 (murah)
    - P/S: 0 - 2 (murah)
    - ROE: 15 - 100 (tinggi)
    - DER: 0 - 100 (rendah)
    - EPS: > 0 (profit)
    """)

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=3600)  # Cache selama 1 jam
def get_fundamental_data(tickers_raw):
    tickers_list = [x.strip().upper() for x in tickers_raw.split(',')]
    tickers_fixed = [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers_list]
    
    data = []
    progress_bar = st.progress(0, text="Mengambil data fundamental...")
    
    for i, ticker in enumerate(tickers_fixed):
        try:
            progress_bar.progress(int((i / len(tickers_fixed)) * 100), text=f"Menganalisa {ticker}...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            name = info.get('shortName', ticker)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # Ambil data (Default None jika gagal)
            pe = info.get('trailingPE')
            ps = info.get('priceToSalesTrailing12Months')
            roe = info.get('returnOnEquity')
            der = info.get('debtToEquity')
            eps = info.get('trailingEps')
            
            # Konversi ROE ke Persen jika ada
            if roe is not None: 
                roe = roe * 100

            data.append({
                'Kode': ticker.replace('.JK', ''),
                'Nama': name,
                'Harga': price,
                'P/E Ratio (x)': pe,
                'P/S Ratio (x)': ps,
                'ROE (%)': roe,
                'DER (%)': der,
                'EPS (Rp)': eps
            })
            
        except Exception:
            continue

    progress_bar.empty()
    return pd.DataFrame(data)

# --- FUNGSI FILTER DATA ---
def apply_filters(df):
    """Apply custom filters to dataframe"""
    filtered_df = df.copy()
    original_count = len(filtered_df)
    
    # Filter P/E
    if pe_min is not None:
        filtered_df = filtered_df[(filtered_df['P/E Ratio (x)'].isna()) | (filtered_df['P/E Ratio (x)'] >= pe_min)]
    if pe_max is not None:
        filtered_df = filtered_df[(filtered_df['P/E Ratio (x)'].isna()) | (filtered_df['P/E Ratio (x)'] <= pe_max)]
    
    # Filter P/S
    if ps_min is not None:
        filtered_df = filtered_df[(filtered_df['P/S Ratio (x)'].isna()) | (filtered_df['P/S Ratio (x)'] >= ps_min)]
    if ps_max is not None:
        filtered_df = filtered_df[(filtered_df['P/S Ratio (x)'].isna()) | (filtered_df['P/S Ratio (x)'] <= ps_max)]
    
    # Filter ROE
    if roe_min is not None:
        filtered_df = filtered_df[(filtered_df['ROE (%)'].isna()) | (filtered_df['ROE (%)'] >= roe_min)]
    if roe_max is not None:
        filtered_df = filtered_df[(filtered_df['ROE (%)'].isna()) | (filtered_df['ROE (%)'] <= roe_max)]
    
    # Filter DER
    if der_min is not None:
        filtered_df = filtered_df[(filtered_df['DER (%)'].isna()) | (filtered_df['DER (%)'] >= der_min)]
    if der_max is not None:
        filtered_df = filtered_df[(filtered_df['DER (%)'].isna()) | (filtered_df['DER (%)'] <= der_max)]
    
    # Filter EPS
    if eps_min is not None:
        filtered_df = filtered_df[(filtered_df['EPS (Rp)'].isna()) | (filtered_df['EPS (Rp)'] >= eps_min)]
    if eps_max is not None:
        filtered_df = filtered_df[(filtered_df['EPS (Rp)'].isna()) | (filtered_df['EPS (Rp)'] <= eps_max)]
    
    # Filter Harga
    if price_min is not None:
        filtered_df = filtered_df[(filtered_df['Harga'].isna()) | (filtered_df['Harga'] >= price_min)]
    if price_max is not None:
        filtered_df = filtered_df[(filtered_df['Harga'].isna()) | (filtered_df['Harga'] <= price_max)]
    
    filtered_count = len(filtered_df)
    
    return filtered_df, original_count, filtered_count

# --- TOMBOL PROSES ---
if st.button("🚀 Bandingkan Sekarang", type="primary", use_container_width=True):
    if not input_saham:
        st.warning("⚠️ Masukkan kode saham dulu.")
    else:
        df = get_fundamental_data(input_saham)
        
        if not df.empty:
            # --- BERSIHKAN DATA ---
            cols_to_numeric = ['Harga', 'P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']
            for col in cols_to_numeric:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # --- APPLY FILTERS ---
            filtered_df, original_count, filtered_count = apply_filters(df)
            
            # --- INFO CARDS ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Saham", original_count)
            with col2:
                st.metric("✅ Lolos Filter", filtered_count)
            with col3:
                st.metric("❌ Tidak Lolos", original_count - filtered_count)
            with col4:
                filter_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
                st.metric("📈 Persentase", f"{filter_pct:.1f}%")
            
            st.divider()
            
            if filtered_count == 0:
                st.warning("⚠️ Tidak ada saham yang memenuhi kriteria filter. Coba sesuaikan filter di sidebar.")
            else:
                st.success(f"✅ Berhasil menemukan {filtered_count} saham yang sesuai kriteria!")
                
                # --- TAMPILAN TABEL ---
                st.subheader("📋 Tabel Perbandingan (Heatmap)")

                # Konfigurasi Tampilan
                column_config = {
                    "Kode": st.column_config.TextColumn("Ticker", width="small"),
                    "Nama": st.column_config.TextColumn("Perusahaan", width="medium"),
                    "Harga": st.column_config.NumberColumn("Harga", format="Rp %d"),
                    "P/E Ratio (x)": st.column_config.NumberColumn("P/E Ratio", format="%.2fx"),
                    "P/S Ratio (x)": st.column_config.NumberColumn("P/S Ratio", format="%.2fx"),
                    "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                    "DER (%)": st.column_config.NumberColumn("Debt/Eq", format="%.2f%%"),
                    "EPS (Rp)": st.column_config.NumberColumn("EPS", format="Rp %.2f"),
                }

                # --- STYLING ---
                styled_df = filtered_df.style\
                    .background_gradient(subset=['ROE (%)', 'EPS (Rp)'], cmap='RdYlGn', vmin=0)\
                    .background_gradient(subset=['P/E Ratio (x)', 'P/S Ratio (x)', 'DER (%)'], cmap='RdYlGn_r', vmin=0)

                st.dataframe(
                    styled_df,
                    column_config=column_config,
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )
                
                # --- DOWNLOAD BUTTON ---
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name=f'filtered_stocks_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
                
                # --- STATISTIK ---
                st.divider()
                st.subheader("📊 Statistik Saham Terfilter")
                
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                
                with stats_col1:
                    st.markdown("**Rata-rata Metrik:**")
                    for col in ['P/E Ratio (x)', 'P/S Ratio (x)', 'ROE (%)', 'DER (%)', 'EPS (Rp)']:
                        avg_val = filtered_df[col].mean()
                        if not pd.isna(avg_val):
                            st.write(f"• {col}: {avg_val:.2f}")
                
                with stats_col2:
                    st.markdown("**Nilai Tertinggi:**")
                    for col in ['ROE (%)', 'EPS (Rp)']:
                        if col in filtered_df.columns:
                            max_row = filtered_df.loc[filtered_df[col].idxmax()] if filtered_df[col].notna().any() else None
                            if max_row is not None:
                                st.write(f"• {col}: **{max_row['Kode']}** ({max_row[col]:.2f})")
                
                with stats_col3:
                    st.markdown("**Nilai Terendah:**")
                    for col in ['P/E Ratio (x)', 'DER (%)']:
                        if col in filtered_df.columns:
                            min_row = filtered_df.loc[filtered_df[col].idxmin()] if filtered_df[col].notna().any() else None
                            if min_row is not None:
                                st.write(f"• {col}: **{min_row['Kode']}** ({min_row[col]:.2f})")
                
                # --- GRAFIK ---
                st.divider()
                st.subheader("📊 Visualisasi Grafik")
                
                tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "📈 Scatter Plot", "🎯 Top 10"])
                
                with tab1:
                    metric_choice = st.selectbox("Pilih Metrik:", ['P/E Ratio (x)', 'ROE (%)', 'DER (%)', 'P/S Ratio (x)', 'EPS (Rp)'])
                    chart_df = filtered_df[['Kode', metric_choice]].dropna().set_index('Kode')
                    st.bar_chart(chart_df, height=400)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_axis = st.selectbox("X-Axis:", ['P/E Ratio (x)', 'P/S Ratio (x)', 'DER (%)'], key='x')
                    with col2:
                        y_axis = st.selectbox("Y-Axis:", ['ROE (%)', 'EPS (Rp)', 'P/E Ratio (x)'], key='y')
                    
                    scatter_df = filtered_df[[x_axis, y_axis]].dropna()
                    if not scatter_df.empty:
                        st.scatter_chart(scatter_df, x=x_axis, y=y_axis, height=400)
                    else:
                        st.info("Tidak ada data untuk scatter plot.")
                
                with tab3:
                    top_metric = st.selectbox("Urutkan berdasarkan:", ['ROE (%)', 'EPS (Rp)', 'P/E Ratio (x)', 'P/S Ratio (x)'], key='top')
                    ascending = st.checkbox("Urutkan dari terkecil", value=False)
                    
                    top_df = filtered_df[['Kode', 'Nama', top_metric]].dropna().sort_values(top_metric, ascending=ascending).head(10)
                    
                    if not top_df.empty:
                        st.dataframe(
                            top_df.reset_index(drop=True),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Tidak ada data untuk ditampilkan.")
                
        else:
            st.error("❌ Data tidak ditemukan atau koneksi bermasalah.")

# --- FOOTER ---
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>💡 <b>Tips:</b> Gunakan filter di sidebar untuk menemukan saham yang sesuai kriteria investasi kamu</p>
    <p>Data dari Yahoo Finance • Update real-time</p>
</div>
""", unsafe_allow_html=True)
