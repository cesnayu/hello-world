import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockAnalyzer:
    def __init__(self, stock_list):
        """
        Initialize dengan list saham yang mau dianalisis
        
        Parameters:
        stock_list (list): List ticker saham (contoh: ['BBCA.JK', 'BBRI.JK', 'TLKM.JK'])
        """
        self.stock_list = stock_list
        self.results = []
    
    def get_stock_returns(self):
        """
        Ambil data return 5 hari terakhir untuk setiap saham
        """
        print("Mengambil data saham...\n")
        
        for ticker in self.stock_list:
            try:
                # Download data 10 hari terakhir (buffer untuk memastikan ada 5 hari trading)
                stock = yf.Ticker(ticker)
                df = stock.history(period="10d")
                
                if len(df) < 2:
                    print(f"❌ {ticker}: Data tidak cukup")
                    continue
                
                # Ambil 6 hari terakhir (untuk hitung 5 hari return)
                df = df.tail(6)
                
                # Hitung return harian (%)
                returns = []
                dates = []
                
                for i in range(1, len(df)):
                    daily_return = ((df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1]) * 100
                    returns.append(daily_return)
                    dates.append(df.index[i].strftime('%Y-%m-%d'))
                
                # Hitung total return 5 hari
                total_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                
                # Simpan hasil
                result = {
                    'Ticker': ticker,
                    'Total_Gain_5D': round(total_return, 2)
                }
                
                # Tambahkan return per hari
                for i, (date, ret) in enumerate(zip(dates, returns), 1):
                    result[f'Day_{i}'] = round(ret, 2)
                    result[f'Date_{i}'] = date
                
                result['Current_Price'] = round(df['Close'].iloc[-1], 2)
                
                self.results.append(result)
                print(f"✓ {ticker}: Berhasil diambil")
                
            except Exception as e:
                print(f"❌ {ticker}: Error - {str(e)}")
        
        return self.results
    
    def display_results(self, sort_by='Total_Gain_5D', ascending=False):
        """
        Tampilkan hasil dengan sorting
        
        Parameters:
        sort_by (str): Kolom untuk sorting (default: 'Total_Gain_5D')
        ascending (bool): True untuk ascending, False untuk descending
        """
        if not self.results:
            print("Tidak ada data untuk ditampilkan")
            return None
        
        # Convert ke DataFrame
        df = pd.DataFrame(self.results)
        
        # Sort berdasarkan total gain
        df = df.sort_values(by=sort_by, ascending=ascending)
        
        print("\n" + "="*100)
        print("ANALISIS RETURN SAHAM - 5 HARI TERAKHIR")
        print("="*100)
        
        # Tampilkan summary
        print(f"\nTotal Saham Dianalisis: {len(df)}")
        print(f"Gainers (Total > 0): {len(df[df['Total_Gain_5D'] > 0])}")
        print(f"Losers (Total < 0): {len(df[df['Total_Gain_5D'] < 0])}")
        
        # Tampilkan detail per saham
        print("\n" + "-"*100)
        for idx, row in df.iterrows():
            status = "🟢 GAINER" if row['Total_Gain_5D'] > 0 else "🔴 LOSER"
            print(f"\n{status} - {row['Ticker']}")
            print(f"Harga Sekarang: Rp {row['Current_Price']:,.2f}")
            print(f"Total Gain 5 Hari: {row['Total_Gain_5D']:+.2f}%")
            print("Return Harian:")
            
            for i in range(1, 6):
                if f'Day_{i}' in row:
                    day_return = row[f'Day_{i}']
                    date = row[f'Date_{i}']
                    arrow = "📈" if day_return > 0 else "📉" if day_return < 0 else "➡️"
                    print(f"  {arrow} Hari {i} ({date}): {day_return:+.2f}%")
            print("-"*100)
        
        return df
    
    def get_top_gainers(self, n=5):
        """Ambil top N gainers"""
        df = pd.DataFrame(self.results)
        return df.nlargest(n, 'Total_Gain_5D')
    
    def get_top_losers(self, n=5):
        """Ambil top N losers"""
        df = pd.DataFrame(self.results)
        return df.nsmallest(n, 'Total_Gain_5D')


def main():
    # ISI DAFTAR SAHAM DISINI
    # Untuk saham Indonesia, tambahkan .JK di belakang
    # Contoh: BBCA.JK, BBRI.JK, TLKM.JK
    
    stock_list = [
        'BBCA.JK',  # Bank Central Asia
        'BBRI.JK',  # Bank Rakyat Indonesia
        'TLKM.JK',  # Telkom Indonesia
        'ASII.JK',  # Astra International
        'UNVR.JK',  # Unilever Indonesia
        # Tambahkan saham lainnya disini
    ]
    
    # Buat analyzer
    analyzer = StockAnalyzer(stock_list)
    
    # Ambil data return
    analyzer.get_stock_returns()
    
    # Tampilkan hasil (sorted by Total Gain descending)
    df_results = analyzer.display_results(sort_by='Total_Gain_5D', ascending=False)
    
    # Optional: Tampilkan top 3 gainers dan losers
    if df_results is not None and len(df_results) > 0:
        print("\n" + "="*100)
        print("🏆 TOP 3 GAINERS")
        print("="*100)
        top_gainers = analyzer.get_top_gainers(3)
        for idx, row in top_gainers.iterrows():
            print(f"{row['Ticker']}: {row['Total_Gain_5D']:+.2f}%")
        
        print("\n" + "="*100)
        print("⚠️  TOP 3 LOSERS")
        print("="*100)
        top_losers = analyzer.get_top_losers(3)
        for idx, row in top_losers.iterrows():
            print(f"{row['Ticker']}: {row['Total_Gain_5D']:+.2f}%")
        
        # Save ke CSV (optional)
        df_results.to_csv('stock_analysis_results.csv', index=False)
        print("\n✓ Hasil disimpan ke: stock_analysis_results.csv")


if __name__ == "__main__":
    main()
