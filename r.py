import pandas as pd
import yfinance as yf
import sys

# ==========================================
# 1. LIST SAHAM
# ==========================================
daftar_saham = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',
    'ASII.JK', 'TLKM.JK',
    'ADRO.JK', 'PTBA.JK', 'ITMG.JK',
    'UNVR.JK', 'ICBP.JK', 'MYOR.JK',
    'GOTO.JK', 'BUKA.JK'
]

print(f"Sedang mengambil data untuk {len(daftar_saham)} saham...")

data_list = []

for ticker in daftar_saham:
    try:
        stock = yf.Ticker(ticker)
        # Menggunakan fast_info (lebih cepat & stabil dibanding .info biasa)
        # fast_info seringkali lebih ampuh menembus limitasi yfinance
        price = stock.fast_info.last_price
        market_cap = stock.fast_info.market_cap
        
        # Untuk PE dan Revenue, kita tetap butuh .info (data fundamental)
        # Kita bungkus try-except lagi di sini khusus fetching info
        try:
            info = stock.info
            pe_ratio = info.get('trailingPE', None)
            revenue = info.get('totalRevenue', 0)
            short_name = info.get('shortName', ticker)
        except:
            # Jika gagal ambil info detail, isi dummy/default
            pe_ratio = None
            revenue = 0
            short_name = ticker

        # Pastikan data masuk hanya jika Harga ada (valid)
        if price:
            data_list.append({
                'Kode': ticker.replace('.JK', ''),
                'Nama': short_name,
                'Harga': price,
                'P/E Ratio': pe_ratio,
                'Revenue (Raw)': revenue,
                'Market Cap': market_cap
            })
            print(f"✅ {ticker} berhasil.")
        else:
            print(f"⚠️ {ticker} data kosong (skip).")
            
    except Exception as e:
        print(f"❌ {ticker} gagal total: {e}")

# ==========================================
# 2. PENGECEKAN KEAMANAN (PENTING!)
# ==========================================
if len(data_list) == 0:
    print("\n[ERROR FATAL] Tidak ada data yang berhasil diambil sama sekali.")
    print("Kemungkinan IP Address Anda diblokir sementara oleh Yahoo Finance atau koneksi bermasalah.")
    sys.exit() # Berhenti di sini, jangan lanjut ke bawah

# Buat DataFrame
df = pd.DataFrame(data_list)

# ==========================================
# 3. FORMATTING & EXPORT
# ==========================================
def format_angka_besar(angka):
    if not angka or pd.isna(angka) or angka == 0:
        return "0"
    if angka >= 1_000_000_000_000:
        return f"{angka / 1_000_000_000_000:.2f} T"
    elif angka >= 1_000_000_000:
        return f"{angka / 1_000_000_000:.2f} M"
    else:
        return f"{angka:,.0f}"

# Terapkan format (Gunakan .get agar aman jika kolom entah kenapa hilang)
df['Revenue (Display)'] = df.get('Revenue (Raw)', pd.Series([0]*len(df))).apply(format_angka_besar)
df['Market Cap (Display)'] = df.get('Market Cap', pd.Series([0]*len(df))).apply(format_angka_besar)

# Sorting
if 'Market Cap' in df.columns:
    df = df.sort_values(by='Market Cap', ascending=False)

# Export
filename = 'Rasio_PE_Revenue_Saham_Fixed.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')
df.to_excel(writer, sheet_name='Analisa', index=False)

# Format Excel (Warna-warni)
workbook = writer.book
worksheet = writer.sheets['Analisa']
green_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
red_fmt   = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
yellow_fmt = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

# Cari index kolom P/E Ratio
try:
    pe_col_idx = df.columns.get_loc("P/E Ratio")
    # Loop baris data
    for row_num in range(len(df)):
        cell_val = df.iloc[row_num, pe_col_idx]
        
        # Logic Warna
        excel_row = row_num + 1 # +1 karena header
        if pd.isna(cell_val) or cell_val < 0:
            worksheet.write(excel_row, pe_col_idx, "N/A", yellow_fmt)
        elif cell_val < 10:
            worksheet.write(excel_row, pe_col_idx, cell_val, green_fmt)
        elif cell_val > 25:
            worksheet.write(excel_row, pe_col_idx, cell_val, red_fmt)
        else:
            worksheet.write(excel_row, pe_col_idx, cell_val)
except KeyError:
    pass # Skip coloring if column missing

writer.close()
print(f"\nSelesai! File '{filename}' berhasil dibuat.")
