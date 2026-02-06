import yfinance as yf
import pandas as pd

# 1. List Saham (Tambahkan .JK untuk saham Indonesia)
tickers = ['BBCA.JK', 'BBRI.JK', 'TLKM.JK', 'ASII.JK']

# 2. Container untuk data
all_data = []

print("Sedang mengambil data...")

for ticker in tickers:
    stock = yf.Ticker(ticker)
    
    # Ambil data keuangan kuartalan
    # quarter_financials biasanya mereturn 4-5 kuartal terakhir.
    # Untuk data lebih lama (2024), kadang yfinance membatasi akses gratis.
    q_financials = stock.quarterly_income_stmt
    
    if q_financials is not None and not q_financials.empty:
        # Transpose agar Tanggal jadi baris
        df = q_financials.transpose()
        
        # Filter kolom yang diinginkan (Misal: Net Income)
        # Nama kolom di yfinance: 'Net Income', 'Total Revenue'
        try:
            target_col = df[['Net Income']]
        except KeyError:
            continue # Skip jika data tidak ada

        target_col.columns = ['Net Profit'] # Rename
        target_col['Ticker'] = ticker.replace('.JK', '')
        
        # Reset index agar tanggal jadi kolom biasa
        target_col.reset_index(inplace=True)
        target_col.rename(columns={'index': 'Date'}, inplace=True)
        
        all_data.append(target_col)

# 3. Gabungkan semua data
if all_data:
    final_df = pd.concat(all_data)
    
    # Konversi Date ke format Q1/Q2
    final_df['Date'] = pd.to_datetime(final_df['Date'])
    final_df['Quarter'] = final_df['Date'].dt.to_period('Q').astype(str)
    
    # 4. Pivot Table (Agar bentuknya Ticker di kiri, Kuartal di atas)
    pivot_table = final_df.pivot_table(
        index='Ticker', 
        columns='Quarter', 
        values='Net Profit'
    )
    
    # Urutkan kolom (Q1 2024 - Q4 2025)
    cols = sorted(pivot_table.columns)
    pivot_table = pivot_table[cols]
    
    print(pivot_table)
    
    # Export ke Excel jika mau
    # pivot_table.to_excel("Laporan_Q1_24_to_Q4_25.xlsx")
else:
    print("Data tidak ditemukan.")
