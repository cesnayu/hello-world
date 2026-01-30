"""
Super Stock Dashboard - Improved Version
Aplikasi analisis saham Indonesia dengan fitur lengkap
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# KONFIGURASI & KONSTANTA
# ============================================================================

st.set_page_config(
    layout="wide",
    page_title="Super Stock Dashboard",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

DB_FILE = "stock_database.json"

# Daftar ticker saham (lebih terorganisir)
GRID_TICKERS = [
    # Banking & Financial Services
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BBTN.JK", "BDMN.JK", "BJBR.JK", 
    "BRIS.JK", "BTPN.JK", "MEGA.JK", "NISP.JK", "PNBN.JK",
    
    # Technology & Telecom
    "GOTO.JK", "TLKM.JK", "EXCL.JK", "ISAT.JK", "BUKA.JK",
    
    # Energy & Mining
    "ADRO.JK", "PTBA.JK", "ANTM.JK", "INCO.JK", "TINS.JK", "ITMG.JK", "BUMI.JK",
    
    # Consumer Goods
    "UNVR.JK", "ICBP.JK", "INDF.JK", "HMSP.JK", "KLBF.JK", "GGRM.JK", "MYOR.JK",
    
    # Property & Construction
    "ASRI.JK", "BSDE.JK", "CTRA.JK", "SMRA.JK", "PWON.JK", "ADHI.JK", "WIKA.JK",
    "WSKT.JK", "PTPP.JK",
    
    # Retail & Distribution
    "ACES.JK", "AMRT.JK", "HERO.JK", "LPPF.JK", "MAPI.JK", "RALS.JK",
    
    # Transportation & Logistics
    "BIRD.JK", "GIAA.JK", "JSMR.JK", "SHIP.JK", "TAXI.JK",
    
    # Agriculture & Plantations
    "AALI.JK", "LSIP.JK", "SGRO.JK", "SIMP.JK",
    
    # Media & Entertainment
    "MNCN.JK", "SCMA.JK", "EMTK.JK",
]

# Period mapping
PERIOD_MAP = {
    "1 Hari": "1d",
    "1 Minggu": "5d", 
    "1 Bulan": "1mo",
    "3 Bulan": "3mo",
    "6 Bulan": "6mo",
    "1 Tahun": "1y",
    "2 Tahun": "2y",
    "5 Tahun": "5y",
    "YTD": "ytd",
    "Max": "max"
}

MONTH_MAP = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agust", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
}

# ============================================================================
# DATABASE & SESSION MANAGEMENT
# ============================================================================

class DataManager:
    """Mengelola persistensi data dan session state"""
    
    @staticmethod
    def load_data() -> Optional[Dict]:
        """Load data dari file JSON"""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                return None
        return None

    @staticmethod
    def save_data():
        """Save data ke file JSON"""
        try:
            data = {
                "watchlist": st.session_state.get("watchlist", []),
                "vol_watchlist": st.session_state.get("vol_watchlist", []),
                "vol_saved_tickers": st.session_state.get("vol_saved_tickers", [])
            }
            with open(DB_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    @staticmethod
    def initialize_session():
        """Inisialisasi session state"""
        saved_data = DataManager.load_data()
        
        defaults = {
            'watchlist': saved_data.get("watchlist", ["BBCA.JK", "GOTO.JK", "BBRI.JK"]) if saved_data else ["BBCA.JK", "GOTO.JK", "BBRI.JK"],
            'vol_watchlist': saved_data.get("vol_watchlist", ["GOTO.JK", "BBRI.JK"]) if saved_data else ["GOTO.JK", "BBRI.JK"],
            'vol_saved_tickers': saved_data.get("vol_saved_tickers", []) if saved_data else [],
            'picked_stocks': [],
            'page': 1
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

# ============================================================================
# DATA FETCHING & PROCESSING
# ============================================================================

class StockDataFetcher:
    """Class untuk mengambil data saham dari yfinance"""
    
    @staticmethod
    @st.cache_data(ttl=600, show_spinner=False)
    def get_bulk_history(tickers: List[str], period: str = "3mo") -> pd.DataFrame:
        """Download data historis untuk multiple tickers"""
        if not tickers:
            return pd.DataFrame()
        
        interval = "5m" if period == "1d" else "1d"
        
        try:
            data = yf.download(
                tickers,
                period=period,
                interval=interval,
                group_by='ticker',
                progress=False,
                auto_adjust=False
            )
            return data
        except Exception as e:
            logger.error(f"Error fetching bulk data: {e}")
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def get_single_stock(ticker: str, period: str) -> Optional[pd.DataFrame]:
        """Download data untuk single ticker"""
        if not ticker:
            return None
        
        interval = "5m" if period == "1d" else "1d"
        
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
            
            if df.empty:
                return None
            
            # Cleanup multi-index columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Standardize column names
            if 'Close' not in df.columns and 'Adj Close' in df.columns:
                df = df.rename(columns={'Adj Close': 'Close'})
            
            df = df.reset_index()
            
            # Standardize date column
            if 'Date' not in df.columns and 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'Date'})
            
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            return None

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_fundamental_info(ticker: str) -> Optional[Dict]:
        """Get fundamental info untuk ticker"""
        try:
            info = yf.Ticker(ticker).info
            return {
                "pbv": info.get('priceToBook'),
                "per": info.get('trailingPE'),
                "eps": info.get('trailingEps'),
                "mkt_cap": info.get('marketCap'),
                "sector": info.get('industry', '-')
            }
        except Exception as e:
            logger.error(f"Error fetching fundamental for {ticker}: {e}")
            return None

    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def get_latest_snapshot(tickers: List[str]) -> Dict:
        """Get snapshot harga & volume terkini"""
        if not tickers:
            return {}
        
        try:
            data = yf.download(tickers, period="1d", group_by='ticker', progress=False, auto_adjust=False)
            snapshot = {}
            
            for t in tickers:
                try:
                    if len(tickers) == 1:
                        df = data
                    else:
                        if isinstance(data.columns, pd.MultiIndex):
                            if t in data.columns.levels[0]:
                                df = data[t]
                            else:
                                continue
                        else:
                            continue
                    
                    if not df.empty:
                        col_close = 'Close' if 'Close' in df.columns else 'Adj Close'
                        last_price = float(df[col_close].iloc[-1])
                        last_vol = float(df['Volume'].iloc[-1])
                        
                        snapshot[t] = {
                            'price': last_price,
                            'volume_share': last_vol,
                            'volume_lot': last_vol / 100,
                            'value': last_price * last_vol
                        }
                except Exception as e:
                    logger.error(f"Error processing snapshot for {t}: {e}")
                    continue
                    
            return snapshot
            
        except Exception as e:
            logger.error(f"Error getting snapshot: {e}")
            return {}

# ============================================================================
# VISUALIZATION
# ============================================================================

class ChartBuilder:
    """Class untuk membuat visualisasi chart"""
    
    @staticmethod
    def create_mini_chart(df: pd.DataFrame, ticker: str, period_code: str, show_ma: bool = True) -> go.Figure:
        """Buat mini chart untuk grid view"""
        fig = go.Figure()
        
        if len(df) < 2:
            return fig
        
        # Calculate MA
        if show_ma and period_code != "1d" and len(df) >= 20:
            ma20 = df['Close'].rolling(window=20).mean()
        else:
            ma20 = None
        
        # Determine color
        last_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        color = '#00C805' if float(last_p) >= float(prev_p) else '#FF333A'
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            line=dict(color=color, width=1.5),
            name='Price'
        ))
        
        # Add MA
        if ma20 is not None:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=ma20,
                mode='lines',
                line=dict(color='#FF9800', width=1),
                name='MA20'
            ))
        
        # Add monthly marker for 3mo view
        if period_code == "3mo":
            one_month_ago = datetime.now() - timedelta(days=30)
            fig.add_vline(
                x=one_month_ago.timestamp() * 1000,
                line_width=1,
                line_dash="dot",
                line_color="blue"
            )
        
        fig.update_layout(
            title=dict(text=ticker, font=dict(size=12), x=0.5, xanchor='center'),
            margin=dict(l=0, r=0, t=30, b=0),
            height=150,
            showlegend=False,
            xaxis=dict(showticklabels=False, fixedrange=True),
            yaxis=dict(showticklabels=False, fixedrange=True)
        )
        
        return fig

    @staticmethod
    def create_detail_chart(df: pd.DataFrame, ticker: str, df_financials: pd.DataFrame = None) -> go.Figure:
        """Buat detailed chart dengan candlestick, volume, dan financials"""
        
        # Determine row heights based on data availability
        has_financials = df_financials is not None and not df_financials.empty
        
        if has_financials:
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.2, 0.3],
                subplot_titles=(f"Price Action: {ticker}", "Volume", "Revenue & Net Income")
            )
        else:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.7, 0.3],
                subplot_titles=(f"Price Action: {ticker}", "Volume")
            )
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price",
            showlegend=False
        ), row=1, col=1)
        
        # MA20
        if len(df) > 20:
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Close'].rolling(20).mean(),
                line=dict(color='orange', width=1),
                name="MA 20"
            ), row=1, col=1)
        
        # Volume bars
        colors = ['#00C805' if c >= o else '#FF333A' for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            marker_color=colors,
            name="Volume",
            showlegend=False
        ), row=2, col=1)
        
        # Financial data
        if has_financials:
            rev_col = next((c for c in df_financials.columns if 'Revenue' in c or 'revenue' in c), None)
            inc_col = next((c for c in df_financials.columns if 'Net Income' in c or 'netIncome' in c), None)
            
            if rev_col:
                fig.add_trace(go.Bar(
                    x=df_financials.index,
                    y=df_financials[rev_col],
                    name="Revenue",
                    marker_color='blue',
                    opacity=0.6
                ), row=3, col=1)
            
            if inc_col:
                fig.add_trace(go.Bar(
                    x=df_financials.index,
                    y=df_financials[inc_col],
                    name="Net Income",
                    marker_color='green',
                    opacity=0.8
                ), row=3, col=1)
        
        fig.update_layout(
            height=800 if has_financials else 600,
            xaxis_rangeslider_visible=False,
            hovermode="x unified"
        )
        
        return fig

# ============================================================================
# UI COMPONENTS
# ============================================================================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def render_metrics(last_row: pd.Series, prev_row: pd.Series, fund_info: Optional[Dict] = None):
        """Render metric cards"""
        change = last_row['Close'] - prev_row['Close']
        pct_change = (change / prev_row['Close']) * 100
        
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Harga", f"Rp {last_row['Close']:,.0f}", f"{pct_change:+.2f}%")
        m2.metric("Volume", f"{last_row['Volume']:,.0f}")
        m3.metric("High", f"Rp {last_row['High']:,.0f}")
        m4.metric("Low", f"Rp {last_row['Low']:,.0f}")
        
        if fund_info:
            f1, f2, f3, f4 = st.columns(4)
            
            f1.metric("PER (TTM)", f"{fund_info['per']:.2f}x" if fund_info['per'] else "-")
            f2.metric("PBV", f"{fund_info['pbv']:.2f}x" if fund_info['pbv'] else "-")
            f3.metric("EPS (TTM)", f"Rp {fund_info['eps']:.2f}" if fund_info['eps'] else "-")
            f4.metric("Market Cap", f"Rp {fund_info['mkt_cap']:,.0f}" if fund_info['mkt_cap'] else "-")

    @staticmethod
    def parse_ticker_input(raw_input: str) -> List[str]:
        """Parse dan clean ticker input dari user"""
        clean_input = raw_input.replace('\n', ',').replace(' ', ',')
        tickers = []
        
        for t in clean_input.split(','):
            item = t.strip().upper()
            if item:
                # Auto-add .JK suffix if needed
                if len(item) == 4 and item.isalpha():
                    item += ".JK"
                tickers.append(item)
        
        return list(set(tickers))

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize session
    DataManager.initialize_session()
    
    # Sidebar
    st.sidebar.title("📊 Super Stock Dashboard")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Pilih Menu:",
        [
            "📊 Grid Overview",
            "⚖️ Bandingkan",
            "🔊 Analisa Volume",
            "⭐ Watchlist",
            "🔎 Detail Saham",
            "🔄 Cycle Analysis",
            "💎 Fundamental",
            "🚀 Performa",
            "🎲 Win/Loss Stats"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tips**: Gunakan filter untuk mempersempit pencarian saham")
    
    # Main content area
    st.title("📈 Super Stock Dashboard")
    st.markdown("Dashboard analisis saham Indonesia yang komprehensif")
    st.markdown("---")
    
    # Route to appropriate page
    if menu == "📊 Grid Overview":
        render_grid_page()
    elif menu == "⚖️ Bandingkan":
        render_compare_page()
    elif menu == "🔊 Analisa Volume":
        render_volume_page()
    elif menu == "⭐ Watchlist":
        render_watchlist_page()
    elif menu == "🔎 Detail Saham":
        render_detail_page()
    elif menu == "🔄 Cycle Analysis":
        render_cycle_page()
    elif menu == "💎 Fundamental":
        render_fundamental_page()
    elif menu == "🚀 Performa":
        render_performance_page()
    elif menu == "🎲 Win/Loss Stats":
        render_winloss_page()

# ============================================================================
# PAGE RENDERERS
# ============================================================================

def render_grid_page():
    """Render grid overview page"""
    st.header("📊 Grid Overview")
    st.write("Pilih saham untuk dimasukkan ke menu 'Bandingkan'.")
    
    # Filters
    with st.expander("🔍 Filter Grid (Harga & Volume)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            min_price = st.number_input("Min Harga (Rp)", value=0, step=50, key="min_price_filter")
        with c2:
            max_price = st.number_input("Max Harga (Rp)", value=100000, step=50, key="max_price_filter")
        with c3:
            min_value_b = st.number_input("Min Transaksi (Miliar Rp)", value=0, step=1, key="min_value_filter")
        with c4:
            min_volume_lot = st.number_input("Min Volume (Lot)", value=0, step=1000, key="min_vol_filter")
    
    # Period selection
    c_period, c_page = st.columns([2, 4])
    with c_period:
        period_label = st.selectbox(
            "Rentang Waktu:",
            ["1 Hari", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun", "YTD"],
            index=2,
            key="grid_period"
        )
        selected_period = PERIOD_MAP[period_label]
    
    # Apply filters
    final_tickers = GRID_TICKERS.copy()
    is_filtering = (max_price < 100000) or (min_price > 0) or (min_value_b > 0) or (min_volume_lot > 0)
    
    if is_filtering:
        with st.spinner("🔄 Memfilter saham..."):
            snapshot = StockDataFetcher.get_latest_snapshot(GRID_TICKERS)
            filtered_list = []
            
            for ticker, stats in snapshot.items():
                price = stats['price']
                value_billion = stats['value'] / 1_000_000_000
                volume_lot = stats['volume_lot']
                
                if (min_price <= price <= max_price and 
                    value_billion >= min_value_b and 
                    volume_lot >= min_volume_lot):
                    filtered_list.append(ticker)
            
            final_tickers = filtered_list
            st.success(f"✅ Ditemukan {len(final_tickers)} saham sesuai filter")
    
    if not final_tickers:
        st.warning("⚠️ Tidak ada saham yang sesuai filter")
        return
    
    # Pagination
    items_per_page = 16
    total_pages = math.ceil(len(final_tickers) / items_per_page)
    
    with c_page:
        current_page = st.number_input(
            "Halaman",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.get('page', 1),
            key="grid_page_num"
        )
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    batch_tickers = final_tickers[start_idx:end_idx]
    
    # Display grid
    with st.spinner("📊 Memuat grafik..."):
        data_grid = StockDataFetcher.get_bulk_history(batch_tickers, period=selected_period)
        
        if not data_grid.empty:
            cols = st.columns(4)
            
            for i, ticker in enumerate(batch_tickers):
                col_idx = i % 4
                
                with cols[col_idx]:
                    try:
                        # Extract dataframe for ticker
                        df_target = pd.DataFrame()
                        
                        if isinstance(data_grid.columns, pd.MultiIndex):
                            if ticker in data_grid.columns.levels[0]:
                                df_target = data_grid[ticker].copy()
                        else:
                            if len(batch_tickers) == 1:
                                df_target = data_grid.copy()
                        
                        if df_target.empty:
                            st.caption(f"❌ {ticker}")
                            continue
                        
                        # Standardize columns
                        if 'Close' not in df_target.columns and 'Adj Close' in df_target.columns:
                            df_target = df_target.rename(columns={'Adj Close': 'Close'})
                        
                        df_target = df_target.dropna()
                        
                        min_length = 5 if selected_period != "1d" else 2
                        
                        if len(df_target) >= min_length:
                            fig = ChartBuilder.create_mini_chart(df_target, ticker, selected_period)
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            
                            # Checkbox for selection
                            is_checked = ticker in st.session_state.picked_stocks
                            
                            if st.checkbox(
                                f"✅ Pilih {ticker}",
                                value=is_checked,
                                key=f"chk_{ticker}_{current_page}"
                            ):
                                if ticker not in st.session_state.picked_stocks:
                                    st.session_state.picked_stocks.append(ticker)
                            else:
                                if ticker in st.session_state.picked_stocks:
                                    st.session_state.picked_stocks.remove(ticker)
                        else:
                            st.caption(f"⚠️ {ticker} (data kurang)")
                            
                    except Exception as e:
                        logger.error(f"Error rendering {ticker}: {e}")
                        st.caption(f"⚠️ {ticker} (error)")
    
    st.divider()
    st.info(f"🛒 **Keranjang Pilihan**: {len(st.session_state.picked_stocks)} saham terpilih")

def render_compare_page():
    """Render comparison page"""
    st.header("⚖️ Bandingkan & Eliminasi")
    
    picked = st.session_state.picked_stocks
    
    if not picked:
        st.warning("⚠️ Belum ada saham yang dipilih dari Menu '📊 Grid Overview'.")
        st.info("💡 Kembali ke Grid Overview dan pilih saham yang ingin dibandingkan")
        return
    
    st.success(f"Membandingkan **{len(picked)}** saham")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🗑️ Hapus Semua Pilihan", use_container_width=True):
            st.session_state.picked_stocks = []
            st.rerun()
    
    st.divider()
    
    with st.spinner("📊 Mengambil data detail..."):
        comp_data = StockDataFetcher.get_bulk_history(picked, period="6mo")
        
        if comp_data.empty:
            st.error("Gagal mengambil data")
            return
        
        comp_cols = st.columns(3)
        
        for i, ticker in enumerate(picked):
            col_idx = i % 3
            
            with comp_cols[col_idx]:
                st.subheader(ticker)
                
                try:
                    df_c = pd.DataFrame()
                    
                    if isinstance(comp_data.columns, pd.MultiIndex):
                        if ticker in comp_data.columns.levels[0]:
                            df_c = comp_data[ticker].copy()
                    else:
                        if len(picked) == 1:
                            df_c = comp_data.copy()
                    
                    if not df_c.empty:
                        # Standardize
                        if 'Close' not in df_c.columns and 'Adj Close' in df_c.columns:
                            df_c = df_c.rename(columns={'Adj Close': 'Close'})
                        
                        df_c = df_c.dropna()
                        
                        # Chart
                        fig = ChartBuilder.create_mini_chart(df_c, ticker, "6mo")
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        # Stats
                        if len(df_c) >= 2:
                            last_price = df_c['Close'].iloc[-1]
                            first_price = df_c['Close'].iloc[0]
                            change_pct = ((last_price - first_price) / first_price) * 100
                            
                            st.metric(
                                "Performa 6 Bulan",
                                f"Rp {last_price:,.0f}",
                                f"{change_pct:+.2f}%"
                            )
                        
                        # Remove button
                        if st.button(f"❌ Hapus {ticker}", key=f"del_{ticker}", use_container_width=True):
                            st.session_state.picked_stocks.remove(ticker)
                            st.rerun()
                    else:
                        st.error(f"Data tidak tersedia untuk {ticker}")
                        
                except Exception as e:
                    logger.error(f"Error rendering {ticker}: {e}")
                    st.error(f"Gagal memuat {ticker}")
                
                st.divider()

def render_volume_page():
    """Render volume analysis page"""
    st.header("🔊 Analisis Volume")
    st.write("Cari volume saham spesifik atau lihat Top 20 dari saham populer")
    
    # Placeholder - simplified version
    st.info("Volume analysis page - Under construction")
    st.write("Feature: Analisis volume trading dan nilai transaksi")

def render_watchlist_page():
    """Render watchlist page"""
    st.header("⭐ Watchlist Saya")
    
    # Add ticker
    col_input, col_button = st.columns([3, 1])
    
    with col_input:
        new_ticker = st.text_input("Tambah Kode Saham:", key="new_watchlist_ticker").strip().upper()
    
    with col_button:
        st.write("")
        st.write("")
        if st.button("➕ Tambah", use_container_width=True):
            if new_ticker:
                if len(new_ticker) == 4 and new_ticker.isalpha():
                    new_ticker += ".JK"
                
                if new_ticker not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_ticker)
                    DataManager.save_data()
                    st.success(f"✅ {new_ticker} ditambahkan")
                    st.rerun()
                else:
                    st.warning(f"⚠️ {new_ticker} sudah ada di watchlist")
    
    current_watchlist = st.session_state.watchlist
    
    if not current_watchlist:
        st.info("💡 Watchlist kosong. Tambahkan saham favorit Anda!")
        return
    
    # Manage watchlist
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🗑️ Hapus Semua", use_container_width=True):
            st.session_state.watchlist = []
            DataManager.save_data()
            st.rerun()
    
    st.divider()
    
    # Edit watchlist
    edited_watchlist = st.multiselect(
        "Edit Watchlist:",
        options=current_watchlist,
        default=current_watchlist,
        key="edit_watchlist"
    )
    
    if len(edited_watchlist) != len(current_watchlist):
        st.session_state.watchlist = edited_watchlist
        DataManager.save_data()
        st.rerun()
    
    st.divider()
    
    # Display charts
    with st.spinner("📊 Memuat data watchlist..."):
        data_watchlist = StockDataFetcher.get_bulk_history(current_watchlist, period="3mo")
        
        if not data_watchlist.empty:
            cols = st.columns(4)
            
            for i, ticker in enumerate(current_watchlist):
                col_idx = i % 4
                
                with cols[col_idx]:
                    try:
                        df_w = pd.DataFrame()
                        
                        if isinstance(data_watchlist.columns, pd.MultiIndex):
                            if ticker in data_watchlist.columns.levels[0]:
                                df_w = data_watchlist[ticker].copy()
                        else:
                            if len(current_watchlist) == 1:
                                df_w = data_watchlist.copy()
                        
                        if not df_w.empty:
                            # Standardize
                            if 'Close' not in df_w.columns and 'Adj Close' in df_w.columns:
                                df_w = df_w.rename(columns={'Adj Close': 'Close'})
                            
                            df_w = df_w.dropna()
                            
                            fig = ChartBuilder.create_mini_chart(df_w, ticker, "3mo")
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            
                            # Quick stats
                            if len(df_w) >= 2:
                                last = df_w['Close'].iloc[-1]
                                prev = df_w['Close'].iloc[-2]
                                chg = ((last - prev) / prev) * 100
                                st.metric("", f"Rp {last:,.0f}", f"{chg:+.2f}%")
                        
                    except Exception as e:
                        logger.error(f"Error rendering watchlist {ticker}: {e}")
                        st.caption(f"⚠️ {ticker}")

def render_detail_page():
    """Render detail analysis page"""
    st.header("🔎 Analisa Saham Mendalam")
    
    col_search, col_period = st.columns([2, 3])
    
    with col_search:
        default_ticker = st.session_state.watchlist[0] if st.session_state.watchlist else "BBCA.JK"
        detail_ticker = st.text_input(
            "Ketik Kode Saham:",
            value=default_ticker,
            key="detail_ticker_input"
        ).strip().upper()
    
    with col_period:
        period_options = ["1d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        period_labels_map = {
            "1d": "1 Hari", "1mo": "1 Bulan", "3mo": "3 Bulan",
            "6mo": "6 Bulan", "1y": "1 Tahun", "2y": "2 Tahun",
            "5y": "5 Tahun", "max": "Sejak IPO"
        }
        
        selected_period = st.select_slider(
            "Pilih Rentang Waktu:",
            options=period_options,
            value="1y",
            format_func=lambda x: period_labels_map[x],
            key="detail_period"
        )
    
    st.divider()
    
    if not detail_ticker:
        st.warning("⚠️ Masukkan kode saham")
        return
    
    with st.spinner(f"📊 Mengambil data untuk {detail_ticker}..."):
        # Get price data
        df_detail = StockDataFetcher.get_single_stock(detail_ticker, selected_period)
        
        if df_detail is None or df_detail.empty:
            st.error(f"❌ Data untuk {detail_ticker} tidak ditemukan")
            return
        
        # Get fundamental data
        fund_info = StockDataFetcher.get_fundamental_info(detail_ticker)
        
        # Display metrics
        if len(df_detail) >= 2:
            last_row = df_detail.iloc[-1]
            prev_row = df_detail.iloc[-2]
            
            UIComponents.render_metrics(last_row, prev_row, fund_info)
        
        st.divider()
        
        # Create and display chart
        fig = ChartBuilder.create_detail_chart(df_detail, detail_ticker)
        st.plotly_chart(fig, use_container_width=True)

def render_cycle_page():
    """Render cycle analysis page"""
    st.header("🔄 Cycle Analysis")
    st.info("Seasonal pattern analysis - Under construction")

def render_fundamental_page():
    """Render fundamental screener page"""
    st.header("💎 Fundamental Screener")
    st.info("Fundamental analysis & screening - Under construction")

def render_performance_page():
    """Render performance matrix page"""
    st.header("🚀 Matriks Performa")
    st.info("Performance comparison matrix - Under construction")

def render_winloss_page():
    """Render win/loss statistics page"""
    st.header("🎲 Statistik Win/Loss")
    st.info("Win/Loss probability analysis - Under construction")

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
