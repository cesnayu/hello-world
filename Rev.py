
]

st.set_page_config(layout="wide")
st.title("📊 Personal Stock Weekly Dashboard")

today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


# ==============================
# 2. CACHING (ANTI RATE LIMIT)
# ==============================

@st.cache_data(ttl=300)  # Cache 5 menit
def download_data(tickers, start_date, end_date):
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True
    )
    return data


# ==============================
# 3. PROCESSING FUNCTION
# ==============================

def get_stock_data(tickers):

    start_date = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    data = download_data(tickers, start_date, end_date)

    all_data = []

    for ticker in tickers:
        try:
            df = data[ticker].dropna().copy()
        except:
            continue

        if df.empty:
            continue

        df["Return"] = df["Close"].pct_change() * 100
        df["Date"] = df.index.date

        current_price = df["Close"].iloc[-1]
        today_return = df["Return"].iloc[-1]

        row = {
            "Ticker": ticker,
            "Current Price": round(current_price, 2),
            "Today Return (%)": round(today_return, 2)
        }

        weekly_returns = []
        gain_count = 0

        for i in range(5):
            target_date = (start_of_week + timedelta(days=i)).date()
            day_name = days_names[i]

            day_data = df[df["Date"] == target_date]

            if not day_data.empty:
                daily_return = day_data["Return"].iloc[0]
                row[f"{day_name} Ret (%)"] = round(daily_return, 2)

                if daily_return > 0:
                    gain_count += 1

                weekly_returns.append(daily_return)
            else:
                row[f"{day_name} Ret (%)"] = "-"

        row["Weekly Acc (%)"] = round(sum(weekly_returns), 2) if weekly_returns else 0
        row["Gain Days (5d)"] = f"{gain_count} / 5"

        all_data.append(row)

    final_df = pd.DataFrame(all_data)

    # Sort Top Gainer Hari Ini
    final_df = final_df.sort_values(
        by="Today Return (%)",
        ascending=False
    )

    return final_df


# ==============================
# 4. RUN DASHBOARD
# ==============================

with st.spinner("Fetching market data..."):
    final_df = get_stock_data(LIST_SAHAM)

st.subheader("🔥 Top Gainer Today")
st.dataframe(final_df.head(3), use_container_width=True)

st.subheader("📊 Weekly Overview")
st.dataframe(
    final_df.style.map(
        lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0
        else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
        subset=[c for c in final_df.columns if "Ret" in c or "Acc" in c]
    ),
    use_container_width=True
)

st.caption(f"Data minggu dimulai: {start_of_week.strftime('%Y-%m-%d')}")
