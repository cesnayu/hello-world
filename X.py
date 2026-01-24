import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="IHSG Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Daftar saham IHSG
STOCK_LIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK',
    'ASII.JK', 'UNVR.JK', 'ICBP.JK', 'INDF.JK', 'KLBF.JK',
    'CPIN.JK', 'ADRO.JK', 'PTBA.JK', 'ANTM.JK', 'INCO.JK',
    'ITMG.JK', 'SMGR.JK', 'INTP.JK', 'WIKA.JK', 'WSKT.JK',
    'PTPP.JK', 'JSMR.JK', 'PGAS.JK', 'ELSA.JK', 'EXCL.JK',
    'ISAT.JK', 'BSDE.JK', 'PWON.JK', 'CTRA.JK', 'SMRA.JK',
    'MNCN.JK', 'SCMA.JK', 'GGRM.JK', 'HMSP.JK', 'WIIM.JK',
    'TOWR.JK', 'TBIG.JK', 'ESSA.JK', 'MAPI.JK', 'ERAA.JK',
    'MDKA.JK', 'AMRT.JK', 'ACES.JK', 'BUKA.JK', 'GOTO.JK',
    'EMTK.JK', 'BRPT.JK', 'AKRA.JK', 'UNTR.JK', 'MEDC.JK'
]

# Initialize session state for watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

@st.cache_data(ttl=3600)
def get_stock_data(ticker, period='3mo'):
    """Ambil data saham dari Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return None

@st.cache_data(ttl=3600)
def calculate_performance(stock_list):
    """Hitung performa saham untuk berbagai periode"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(stock_list):
        try:
            status_text.text(f"Mengambil data {ticker}... ({idx+1}/{len(stock_list)})")
            data = get_stock_data(ticker, period='3mo')
            
            if data is None or len(data) < 2:
                continue
            
            current_price = data['Close'].iloc[-1]
            volume_today = data['Volume'].iloc[-1]
            volume_week = data['Volume'].tail(5).mean() if len(data) >= 5 else volume_today
            
            day_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) >= 2 else 0
            week_change = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100 if len(data) >= 6 else 0
            month_change = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100 if len(data) >= 21 else 0
            month3_change = ((current_price - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100 if len(data) >= 60 else 0
            
            results.append({
                'Ticker': ticker.replace('.JK', ''),
                'TickerFull': ticker,
                'Harga': current_price,
                'Volume': volume_today,
                'Volume Week': volume_week,
                'Hari Ini': day_change,
                '1 Minggu': week_change,
                '1 Bulan': month_change,
                '3 Bulan': month3_change,
                'Data': data
            })
            
            progress_bar.progress((idx + 1) / len(stock_list))
            
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def create_price_chart_with_1month_line(data, ticker, change_pct):
    """Buat grafik harga dengan garis 1 bulan"""
    color = 'green' if change_pct > 0 else 'red'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=ticker,
        line=dict(color=color, width=2)
    ))
    
    # Garis 1 bulan
    if len(data) >= 21:
        one_month_ago = data.index[-21]
        fig.add_vline(
            x=one_month_ago,
            line_dash="dash",
            line_color="blue",
            annotation_text="1 bulan lalu",
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f"{ticker} - Rp {data['Close'].iloc[-1]:,.0f}",
        xaxis_title="Tanggal",
        yaxis_title="Harga",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_mini_charts(df, title):
    """Buat mini charts untuk top stocks"""
    n_stocks = min(len(df), 20)
    rows = (n_stocks + 3) // 4
    
    fig = make_subplots(
        rows=rows,
        cols=4,
        subplot_titles=[f"{row['Ticker']}" for _, row in df.head(n_stocks).iterrows()],
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    for idx, (_, row) in enumerate(df.head(n_stocks).iterrows()):
        r = (idx // 4) + 1
        c = (idx % 4) + 1
        
        data = row['Data']
        color = 'green' if row['Hari Ini'] > 0 else 'red'
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                line=dict(color=color, width=2),
                showlegend=False
            ),
            row=r, col=c
        )
        
        # Garis 1 bulan
        if len(data) >= 21:
            one_month_ago = data.index[-21]
            y_min = data['Close'].min()
            y_max = data['Close'].max()
            
            fig.add_trace(
                go.Scatter(
                    x=[one_month_ago, one_month_ago],
                    y=[y_min, y_max],
                    mode='lines',
                    line=dict(color='blue', width=1, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=r, col=c
            )
        
        fig.update_xaxes(showticklabels=False, row=r, col=c)
        fig.update_yaxes(title_text="", row=r, col=c)
    
    fig.update_layout(
        title_text=title,
        height=300 * rows,
        showlegend=False
    )
    
    return fig

# Main App
st.title("📊 Dashboard IHSG - Top Gainers & Losers")
st.markdown(f"*Terakhir diupdate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Edit Daftar Saham")
    st.markdown("Edit `STOCK_LIST` di kode untuk menambah/mengurangi saham")

# Load data
with st.spinner("Mengambil data dari Yahoo Finance..."):
    df_all = calculate_performance(STOCK_LIST)

if len(df_all) == 0:
    st.error("❌ Tidak ada data yang berhasil diambil!")
    st.stop()

st.success(f"✅ Berhasil mengambil data {len(df_all)} saham")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⭐ Watchlist Saya",
    "📈 Top Gainers", 
    "📉 Top Losers",
    "📊 Top Volume",
    "📅 5 Hari Terakhir"
])

# TAB 1: WATCHLIST
with tab1:
    st.header("⭐ Watchlist Saya")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search = st.text_input("🔍 Cari saham (contoh: BBCA, BBRI)", "")
        
        if search:
            filtered = df_all[df_all['Ticker'].str.contains(search.upper())]
            
            if len(filtered) > 0:
                st.markdown("**Hasil pencarian:**")
                for _, row in filtered.iterrows():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    with col_a:
                        st.write(f"**{row['Ticker']}** - Rp {row['Harga']:,.0f}")
                    with col_b:
                        change_color = "green" if row['Hari Ini'] > 0 else "red"
                        st.markdown(f":{change_color}[{row['Hari Ini']:+.2f}%]")
                    with col_c:
                        if row['Ticker'] in st.session_state.watchlist:
                            if st.button("⭐", key=f"remove_{row['Ticker']}"):
                                st.session_state.watchlist.remove(row['Ticker'])
                                st.rerun()
                        else:
                            if st.button("☆", key=f"add_{row['Ticker']}"):
                                st.session_state.watchlist.append(row['Ticker'])
                                st.rerun()
            else:
                st.info("Tidak ada saham yang cocok")
    
    with col2:
        st.markdown("**Saham di Watchlist:**")
        if st.session_state.watchlist:
            for ticker in st.session_state.watchlist:
                if st.button(f"❌ {ticker}", key=f"del_{ticker}", use_container_width=True):
                    st.session_state.watchlist.remove(ticker)
                    st.rerun()
        else:
            st.info("Belum ada saham di watchlist")
    
    st.markdown("---")
    
    # Display watchlist charts
    if st.session_state.watchlist:
        st.subheader("📊 Grafik Saham di Watchlist")
        
        for ticker in st.session_state.watchlist:
            stock_data = df_all[df_all['Ticker'] == ticker]
            if len(stock_data) > 0:
                row = stock_data.iloc[0]
                fig = create_price_chart_with_1month_line(row['Data'], row['Ticker'], row['Hari Ini'])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Gunakan search box di atas untuk mencari dan menambahkan saham ke watchlist")

# TAB 2: TOP GAINERS
with tab2:
    st.header("📈 Top 20 Gainers")
    
    period = st.radio(
        "Pilih periode:",
        ["Hari Ini", "1 Minggu", "1 Bulan", "3 Bulan"],
        horizontal=True,
        key="gainers_period"
    )
    
    period_map = {
        "Hari Ini": "Hari Ini",
        "1 Minggu": "1 Minggu",
        "1 Bulan": "1 Bulan",
        "3 Bulan": "3 Bulan"
    }
    
    df_gainers = df_all.nlargest(20, period_map[period]).reset_index(drop=True)
    
    # Tabel
    st.dataframe(
        df_gainers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].style.format({
            'Harga': 'Rp {:,.0f}',
            'Hari Ini': '{:+.2f}%',
            '1 Minggu': '{:+.2f}%',
            '1 Bulan': '{:+.2f}%',
            '3 Bulan': '{:+.2f}%'
        }).background_gradient(subset=['Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan'], cmap='RdYlGn'),
        use_container_width=True,
        height=600
    )
    
    # Charts
    st.subheader(f"Grafik Top 20 Gainers - {period}")
    fig = create_mini_charts(df_gainers, f"Top 20 Gainers - {period} (Garis biru = 1 bulan lalu)")
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: TOP LOSERS
with tab3:
    st.header("📉 Top 20 Losers")
    
    period = st.radio(
        "Pilih periode:",
        ["Hari Ini", "1 Minggu", "1 Bulan", "3 Bulan"],
        horizontal=True,
        key="losers_period"
    )
    
    period_map = {
        "Hari Ini": "Hari Ini",
        "1 Minggu": "1 Minggu",
        "1 Bulan": "1 Bulan",
        "3 Bulan": "3 Bulan"
    }
    
    df_losers = df_all.nsmallest(20, period_map[period]).reset_index(drop=True)
    
    # Tabel
    st.dataframe(
        df_losers[['Ticker', 'Harga', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].style.format({
            'Harga': 'Rp {:,.0f}',
            'Hari Ini': '{:+.2f}%',
            '1 Minggu': '{:+.2f}%',
            '1 Bulan': '{:+.2f}%',
            '3 Bulan': '{:+.2f}%'
        }).background_gradient(subset=['Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan'], cmap='RdYlGn'),
        use_container_width=True,
        height=600
    )
    
    # Charts
    st.subheader(f"Grafik Top 20 Losers - {period}")
    fig = create_mini_charts(df_losers, f"Top 20 Losers - {period} (Garis biru = 1 bulan lalu)")
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: TOP VOLUME
with tab4:
    st.header("📊 Top 20 Volume")
    
    volume_type = st.radio(
        "Pilih tipe:",
        ["Hari Ini", "Rata-rata 1 Minggu"],
        horizontal=True,
        key="volume_type"
    )
    
    if volume_type == "Hari Ini":
        df_volume = df_all.nlargest(20, 'Volume').reset_index(drop=True)
        vol_col = 'Volume'
    else:
        df_volume = df_all.nlargest(20, 'Volume Week').reset_index(drop=True)
        vol_col = 'Volume Week'
    
    # Tabel
    st.dataframe(
        df_volume[['Ticker', 'Harga', 'Volume', 'Volume Week', 'Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan']].style.format({
            'Harga': 'Rp {:,.0f}',
            'Volume': '{:,.0f}',
            'Volume Week': '{:,.0f}',
            'Hari Ini': '{:+.2f}%',
            '1 Minggu': '{:+.2f}%',
            '1 Bulan': '{:+.2f}%',
            '3 Bulan': '{:+.2f}%'
        }).background_gradient(subset=['Hari Ini', '1 Minggu', '1 Bulan', '3 Bulan'], cmap='RdYlGn'),
        use_container_width=True,
        height=600
    )

# TAB 5: 5 HARI TERAKHIR
with tab5:
    st.header("📅 Top 20 Gainers - 5 Hari Terakhir")
    
    with st.spinner("Menghitung data harian..."):
        daily_results = {}
        
        for ticker in STOCK_LIST:
            try:
                data = get_stock_data(ticker, period='1mo')
                if data is None or len(data) < 6:
                    continue
                
                recent_data = data.tail(6)
                
                for i in range(1, len(recent_data)):
                    date = recent_data.index[i].strftime('%Y-%m-%d')
                    price_prev = recent_data['Close'].iloc[i-1]
                    price_curr = recent_data['Close'].iloc[i]
                    change = ((price_curr - price_prev) / price_prev) * 100
                    
                    if date not in daily_results:
                        daily_results[date] = []
                    
                    daily_results[date].append({
                        'Ticker': ticker.replace('.JK', ''),
                        'Perubahan': change,
                        'Harga': price_curr
                    })
            except:
                continue
    
    dates = sorted(daily_results.keys(), reverse=True)[:5]
    
    for date in dates:
        st.subheader(f"📅 {date}")
        df_day = pd.DataFrame(daily_results[date])
        df_day = df_day.nlargest(20, 'Perubahan').reset_index(drop=True)
        df_day.index = df_day.index + 1
        
        st.dataframe(
            df_day[['Ticker', 'Harga', 'Perubahan']].style.format({
                'Harga': 'Rp {:,.0f}',
                'Perubahan': '{:+.2f}%'
            }).background_gradient(subset=['Perubahan'], cmap='RdYlGn'),
            use_container_width=True
        )
        st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Cara Deploy ke Streamlit Cloud (Gratis):
1. Upload kode ini ke GitHub repository
2. Buka [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub dan pilih repo kamu
4. Deploy! Dashboard bisa diakses dari mana aja

### 📱 Akses dari HP:
- Setelah deploy, akan dapat link seperti: `https://username-app.streamlit.app`
- Bisa dibuka dari browser HP kapan aja
- Watchlist tersimpan selama session aktif
""")
