import csv
import time
import requests
from bs4 import BeautifulSoup

# Base URL target
base_url = "https://www.bgn.go.id/operasional-sppg"
search_query = "DAERAH ISTIMEWA YOGYAKARTA"

# Nama file hasil export
output_file = "sppg_diy_lengkap.csv"

# Buka file CSV untuk menulis data
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Sesuaikan header kolom dengan yang ada di website BGN
    # Contoh: No, Provinsi, Kab/Kota, Kecamatan, Kelurahan, Alamat, Nama SPPG
    writer.writerow(
        [
            "No",
            "Provinsi",
            "Kab_Kota",
            "Kecamatan",
            "Kelurahan_Desa",
            "Alamat",
            "Nama_SPPG",
        ]
    )

    # Looping dari halaman 1 sampai 47
    for page in range(1, 48):
        print(
            f"Sedang mengambil data dari halaman {page}..."
        )  # Log progress

        params = {"page": page, "search": search_query}

        try:
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Cari tabel data di halaman web
                table = soup.find("table")
                if table:
                    rows = table.find_all("tr")

                    # Ambil data dari baris tabel (skip header baris pertama jika ada)
                    for row in rows[1:]:
                        cols = [
                            col.text.strip() for col in row.find_all(["td"])
                        ]
                        if cols:
                            writer.writerow(cols)
                else:
                    print(f"Tabel tidak ditemukan di halaman {page}")
            else:
                print(
                    f"Gagal akses halaman {page}. Status code: {response.status_code}"
                )

        except Exception as e:
            print(f"Terjadi error pada halaman {page}: {e}")

        # Beri jeda 1 detik per halaman agar tidak membebani server web BGN
        time.sleep(1)

print(f"Selesai! Semua data telah disimpan di file: {output_file}")
