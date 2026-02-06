import pandas as pd
import yfinance as yf

# ==========================================
# 1. LIST SAHAM (BISA DITAMBAH SESUKANYA)
# ==========================================
# Pastikan pakai akhiran .JK untuk saham Indonesia
daftar_saham = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',  # Bank
    'ASII.JK', 'TLKM.JK',                        # Blue Chip Lain
    'ADRO.JK', 'PTBA.JK', 'ITMG.JK',             # Batubara (Biasanya PE Rendah)
    'UNVR.JK', 'ICBP.JK', 'MYOR.JK',             # Consumer (Biasanya PE Tinggi)
    'GOTO.JK', 'BUKA.JK'                         # Tech (Seringkali PE Negatif/Rug)
]

print(f"Sedang mengambil data untuk {len(daftar_saham)} saham. Mohon tunggu...")

data_list = []

for ticker in daftar_saham:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Ambil data point penting
        # Gunakan .get() agar tidak error jika data kosong
        price = info.get('currentPrice', 0)
        pe_ratio = info.get('trailingPE', None) # Bisa None jika rugi
        revenue = info.get('totalRevenue', 0)
        market_cap = info.get('marketCap', 0)
        
        # Nama Perusahaan (opsional, biar tidak bingung)
        short_name = info.get('shortName', ticker)

        data_list.append({
            'Kode': ticker.replace('.JK', ''),
            'Nama': short_name,
            'Harga': price,
            'P/E Ratio': pe_ratio,
            'Revenue (Raw)': revenue, # Disimpan mentah dulu untuk sorting
            'Market Cap': market_cap
        })
        print(f"✅ {ticker} berhasil.")
        
    except Exception as e:
        print(f"❌ {ticker} gagal: {e}")

# Buat DataFrame
df = pd.DataFrame(data_list)

# ==========================================
# 2. BERSIH-BERSIH DATA & FORMATTING
# ==========================================

# Fungsi untuk mengubah angka besar jadi Triliun (T) atau Miliar (M)
def format_angka_besar(angka):
    if not angka or angka == 0:
        return "0"
    if angka >= 1_000_000_000_000: # Triliun
        return f"{angka / 1_000_000_000_000:.2f} T"
    elif angka >= 1_000_000_000:   # Miliar
        return f"{angka / 1_000_000_000:.2f} M"
    else:
        return f"{angka:,.0f}"

# Terapkan format ke kolom baru untuk display
df['Revenue (Display)'] = df['Revenue (Raw)'].apply(format_angka_besar)
df['Market Cap (Display)'] = df['Market Cap'].apply(format_angka_besar)

# Urutkan berdasarkan Market Cap terbesar (Opsional)
df = df.sort_values(by='Market Cap', ascending=False)

# Siapkan kolom final untuk Excel
cols_final = ['Kode', 'Nama', 'Harga', 'P/E Ratio', 'Revenue (Display)', 'Market Cap (Display)']
df_final = df[cols_final]

# ==========================================
# 3. EXPORT KE EXCEL DENGAN WARNA
# ==========================================
filename = 'Rasio_PE_Revenue_Saham.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')
df_final.to_excel(writer, sheet_name='Analisa', index=False)

workbook = writer.book
worksheet = writer.sheets['Analisa']

# Format Warna
# Hijau untuk PE Rendah (< 10) -> Sering dianggap murah (Value Stock)
green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})

# Merah untuk PE Tinggi (> 25) -> Sering dianggap mahal (Growth Stock/Overvalued)
red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

# Kuning untuk PE Minus (Rugi) atau None
yellow_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

# Format Header
header_format = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})
for col_num, value in enumerate(df_final.columns.values):
    worksheet.write(0, col_num, value, header_format)

# Loop baris untuk Conditional Formatting Kolom P/E (Kolom D / Index 3)
(max_row, max_col) = df_final.shape
pe_col_idx = 3 # Index kolom P/E (0=Kode, 1=Nama, 2=Harga, 3=PE)
pe_col_letter = 'D' # Kolom D di Excel

for row in range(1, max_row + 1):
    # Ambil nilai PE dari DataFrame (row-1 karena df index mulai 0)
    pe_val = df_final.iloc[row-1]['P/E Ratio']
    
    cell_loc = f"{pe_col_letter}{row+1}" # Misal D2, D3
    
    if pd.isna(pe_val) or pe_val < 0:
        # Jika Rugi (PE Minus) atau Data Kosong
        worksheet.write(row, pe_col_idx, "N/A (Rugi)", yellow_format)
    elif pe_val < 10:
        # Murah (Hijau)
        worksheet.write(row, pe_col_idx, pe_val, green_format)
    elif pe_val > 25:
        # Mahal (Merah)
        worksheet.write(row, pe_col_idx, pe_val, red_format)
    else:
        # Netral (Tulis biasa)
        worksheet.write(row, pe_col_idx, pe_val)

# Auto-adjust lebar kolom biar rapi
worksheet.set_column(0, 0, 10) # Kode
worksheet.set_column(1, 1, 25) # Nama
worksheet.set_column(4, 5, 15) # Revenue & Market Cap

writer.close()
print(f"\nSelesai! File '{filename}' telah dibuat.")
