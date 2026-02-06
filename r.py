import pandas as pd
import numpy as np

# 1. Buat Data Dummy (Contoh Profit dalam Miliar)
# Kita buat data acak supaya terlihat perubahannya
np.random.seed(42)
data = {
    'Ticker': ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII'],
    'Q1 2024': np.random.randint(5000, 10000, 5),
    'Q2 2024': np.random.randint(5000, 10000, 5),
    'Q3 2024': np.random.randint(5000, 10000, 5),
    'Q4 2024': np.random.randint(5000, 10000, 5),
    'Q1 2025': np.random.randint(5000, 10000, 5),
    'Q2 2025': np.random.randint(5000, 10000, 5),
    'Q3 2025': np.random.randint(5000, 10000, 5),
    'Q4 2025': np.random.randint(5000, 10000, 5),
}

df = pd.DataFrame(data)

# Set Ticker sebagai index agar rapi
df.set_index('Ticker', inplace=True)

# 2. Setup Excel Writer dengan engine XlsxWriter
writer = pd.ExcelWriter('Laporan_Saham_Warna.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')

# 3. Akses Workbook dan Worksheet untuk modifikasi
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# 4. Definisikan Format Warna (Hijau & Merah)
green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
red_format   = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

# 5. Loop untuk menerapkan Conditional Formatting
# Kita mulai dari kolom ke-2 (Index 2 di Excel, karena Index 0=Ticker, 1=Q1 2024)
# Kita bandingkan kolom saat ini dengan kolom sebelumnya (col - 1)

(max_row, max_col) = df.shape

# Loop setiap kolom data (mulai dari kolom ke-2 sampai terakhir)
for col_num in range(1, max_col): # range 1 karena kita skip kolom pertama (Q1) sbg base
    # Konversi index kolom ke huruf Excel (Misal 1 -> B, 2 -> C)
    # Karena ada index Ticker di kolom A, maka data pertama (Q1) ada di B.
    # Data Q2 ada di C. Kita mau bandingkan C lawan B.
    
    # Excel column index di xlsxwriter dimulai dari 0 (A=0, B=1, C=2)
    # Ticker = col 0
    # Q1 2024 = col 1
    # Q2 2024 = col 2 (Ini yg mulai dikasih warna)
    
    current_excel_col = col_num + 1 # +1 karena ada kolom index Ticker
    prev_excel_col_letter = chr(65 + current_excel_col - 1) # Huruf kolom sebelumnya (misal 'B')
    curr_excel_col_letter = chr(65 + current_excel_col)     # Huruf kolom sekarang (misal 'C')
    
    # Terapkan Kondisi di Kolom tersebut
    # Baris data dimulai dari baris 1 (karena baris 0 adalah Header)
    
    # ATURAN HIJAU (Naik): Cell Ini > Cell Sebelah Kiri
    worksheet.conditional_format(1, current_excel_col, max_row, current_excel_col, {
        'type':     'formula',
        'criteria': f'={curr_excel_col_letter}2>{prev_excel_col_letter}2',
        'format':   green_format
    })

    # ATURAN MERAH (Turun): Cell Ini < Cell Sebelah Kiri
    worksheet.conditional_format(1, current_excel_col, max_row, current_excel_col, {
        'type':     'formula',
        'criteria': f'={curr_excel_col_letter}2<{prev_excel_col_letter}2',
        'format':   red_format
    })

# 6. Simpan File
writer.close()

print("File 'Laporan_Saham_Warna.xlsx' berhasil dibuat! Cek folder Anda.")
