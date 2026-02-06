import pandas as pd
import numpy as np
from xlsxwriter.utility import xl_col_to_name

# ==========================================
# 1. SETUP DATA (SIMULASI 3 TAHUN / 12 KUARTAL)
# ==========================================
# Saya gunakan data dummy agar tabel PASTI terisi penuh dan warna terlihat.
# Jika pakai Yahoo Finance gratis, seringkali datanya bolong/cuma 4 kuartal.

quarters = [
    'Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023',
    'Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024',
    'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025'
]

tickers = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII']

# Bikin Data Frame Revenue (Angka dalam Triliunan biar ringkas)
df_revenue = pd.DataFrame(
    np.random.randint(10, 50, size=(len(tickers), len(quarters))),
    columns=quarters, index=tickers
)

# Bikin Data Frame EPS (Angka satuan Rupiah)
df_eps = pd.DataFrame(
    np.random.randint(50, 500, size=(len(tickers), len(quarters))),
    columns=quarters, index=tickers
)

# ==========================================
# 2. FUNGSI PEMBUAT FORMATTING EXCEL
# ==========================================
def save_formatted_excel(filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book

    # Format Warna
    green_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    red_fmt   = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})

    # Loop untuk memproses setiap DataFrame ke Sheet berbeda
    dfs_to_write = {'Revenue': df_revenue, 'EPS': df_eps}

    for sheet_name, df in dfs_to_write.items():
        df.to_excel(writer, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]
        
        (max_row, max_col) = df.shape
        
        # Percantik Header
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, header_fmt)

        # LOGIKA UTAMA PEWARNAAN (LOOP KOLOM)
        # Mulai dari kolom ke-2 (Index 2, karena 0=Ticker, 1=Q1 2023)
        # Kita bandingkan Col saat ini vs Col sebelumnya
        
        first_data_col = 1 # Kolom B (Data Q1)
        
        for i in range(first_data_col + 1, max_col + 1):
            # i adalah index kolom saat ini (misal 2 = Kolom C)
            # i-1 adalah index kolom sebelumnya (misal 1 = Kolom B)
            
            curr_col_letter = xl_col_to_name(i)       # Misal "C"
            prev_col_letter = xl_col_to_name(i - 1)   # Misal "B"
            
            # Rumus Excel: =C2>B2 (Tanpa tanda $ agar relatif ke bawah)
            rule_up   = f'={curr_col_letter}2>{prev_col_letter}2'
            rule_down = f'={curr_col_letter}2<{prev_col_letter}2'
            
            # Terapkan ke seluruh baris data (dari baris 1 s/d max_row)
            # Conditional format range: (first_row, first_col, last_row, last_col)
            
            # Aturan Hijau (Naik)
            worksheet.conditional_format(1, i, max_row, i, {
                'type': 'formula',
                'criteria': rule_up,
                'format': green_fmt
            })
            
            # Aturan Merah (Turun)
            worksheet.conditional_format(1, i, max_row, i, {
                'type': 'formula',
                'criteria': rule_down,
                'format': red_fmt
            })

    writer.close()
    print(f"File '{filename}' berhasil dibuat! Cek folder Anda.")

# ==========================================
# 3. EKSEKUSI
# ==========================================
save_formatted_excel('Laporan_Revenue_EPS_3Tahun.xlsx')
