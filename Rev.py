]

st.set_page_config(layout="wide")
st.title("📊 Personal Stock Weekly Dashboard")

# 2. PENGATURAN TANGGAL (Senin - Jumat minggu ini)
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())  # Mendapatkan hari Senin
days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

def get_stock_data(tickers):
    all_data = []
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        # Ambil data 7 hari terakhir untuk memastikan coverage 1 minggu penuh
        df = stock.history(period="7d")
        
        if df.empty:
            continue
            
        current_price = df['Close'].iloc[-1]
        row = {"Ticker": ticker, "Current Price": f"{current_price:.2f}"}
        
        weekly_returns = []
        weekly_volumes = []
        gain_count = 0
        
        # Iterasi Senin sampai Jumat
        for i in range(5):
            target_date = (start_of_week + timedelta(days=i)).date()
            day_name = days_names[i]
            
            # Cek apakah data untuk tanggal tersebut ada
            # Filter data yang cocok dengan tanggal (mengabaikan jam)
            day_data = df[df.index.date == target_date]
            
            if not day_data.empty:
                # Hitung Return (%) = ((Close - Open) / Open) * 100
                daily_return = ((day_data['Close'][0] - day_data['Open'][0]) / day_data['Open'][0]) * 100
                volume = day_data['Volume'][0]
                
                row[f"{day_name} Ret (%)"] = round(daily_return, 2)
                row[f"{day_name} Vol"] = f"{volume:,.0f}"
                
                weekly_returns.append(daily_return)
                if daily_return > 0:
                    gain_count += 1
            else:
                # Jika market tutup atau belum sampai harinya
                row[f"{day_name} Ret (%)"] = "-"
                row[f"{day_name} Vol"] = "-"
        
        # Akumulasi & Statistik
        row["Weekly Acc (%)"] = round(sum(weekly_returns), 2) if weekly_returns else 0
        row["Gain Days (5d)"] = f"{gain_count} / 5"
        
        all_data.append(row)
    
    return pd.DataFrame(all_data)

# Jalankan Query
with st.spinner('Fetching market data...'):
    final_df = get_stock_data(LIST_SAHAM)

# 3. TAMPILAN DASHBOARD
st.dataframe(
    final_df.style.map(lambda x: 'color: green' if isinstance(x, float) and x > 0 
                       else ('color: red' if isinstance(x, float) and x < 0 else ''),
                       subset=[c for c in final_df.columns if "Ret" in c or "Acc" in c]),
    use_container_width=True
)

st.caption(f"Data diupdate otomatis berdasarkan minggu dari tanggal: {start_of_week.strftime('%Y-%m-%d')}")

