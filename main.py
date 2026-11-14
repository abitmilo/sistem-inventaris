import sys
from models import Barang
from services import GudangService

def tampilkan_menu():
    print("\n" + "=" * 52)
    print("   SISTEM INVENTARIS GUDANG PGN (ENTERPRISE CLI)")
    print("=" * 52)
    print("1. Lihat Seluruh Barang")
    print("2. Cari Barang (Kode / Nama)")
    print("3. Tambah Barang Baru")
    print("4. Catat Transaksi Stok (Masuk / Keluar)")
    print("5. Lihat Riwayat Transaksi Stok")
    print("6. Laporan Ringkasan Aset Gudang")
    print("7. Hapus Barang")
    print("8. Keluar Aplikasi")
    print("=" * 52)

def cetak_tabel_barang(daftar_barang: list):
    """Fungsi pembantu agar format tabel barang bisa dipakai ulang di Menu 1 dan Menu 2."""
    print(f"{'ID':<5} | {'KODE':<10} | {'NAMA BARANG':<22} | {'STOK':<8} | {'HARGA (Rp)':<14}")
    print("-" * 70)
    for item in daftar_barang:
        print(
            f"{item.get_id():<5} | "
            f"{item.get_kode_barang():<10} | "
            f"{item.get_nama_barang():<22} | "
            f"{item.get_stok():<8} | "
            f"{item.get_harga():<14,.2f}"
        )

def main():
    service = GudangService()

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-8): ").strip()

        # MENU 1: LIHAT SELURUH BARANG
        if pilihan == "1":
            print("\n--- DAFTAR INVENTARIS BARANG ---")
            daftar = service.ambil_semua_barang()
            if not daftar:
                print("[INFO] Belum ada data barang di database.")
            else:
                cetak_tabel_barang(daftar)

        # MENU 2: CARI BARANG (ILIKE)
        elif pilihan == "2":
            print("\n--- PENCARIAN BARANG ---")
            keyword = input("Masukkan kata kunci kode atau nama barang: ").strip()
            if not keyword:
                print("[INPUT ERROR] Kata kunci pencarian tidak boleh kosong!")
                continue

            hasil = service.cari_barang(keyword)
            if not hasil:
                print(f"[INFO] Tidak ditemukan barang dengan kata kunci '{keyword}'.")
            else:
                print(f"\nDitemukan {len(hasil)} barang:")
                cetak_tabel_barang(hasil)

        # MENU 3: TAMBAH BARANG BARU
        elif pilihan == "3":
            print("\n--- TAMBAH BARANG BARU ---")
            try:
                kode = input("Masukkan Kode Barang (cth: BRG001): ").strip().upper()
                nama = input("Masukkan Nama Barang: ").strip()
                stok = int(input("Masukkan Stok Awal: "))
                harga = float(input("Masukkan Harga Satuan (Rp): "))

                if not kode or not nama:
                    print("[INPUT ERROR] Kode dan Nama Barang tidak boleh kosong!")
                    continue

                if stok < 0 or harga <= 0:
                    print("[INPUT ERROR] Stok minimal 0 dan Harga harus lebih dari Rp0!")
                    continue

                barang_baru = Barang(kode_barang=kode, nama_barang=nama, stok=stok, harga=harga)
                
                if service.tambah_barang(barang_baru):
                    print("[SUKSES] Barang berhasil tersimpan ke database!")
                else:
                    print("[GAGAL] Gagal menyimpan barang. Pastikan Kode Barang belum terdaftar.")
            except ValueError:
                print("[INPUT ERROR] Stok harus angka bulat dan Harga harus berupa angka!")

        # MENU 4: CATAT TRANSAKSI STOK (MASUK / KELUAR)
        elif pilihan == "4":
            print("\n--- CATAT TRANSAKSI STOK ---")
            kode = input("Masukkan Kode Barang: ").strip().upper()
            jenis = input("Jenis Transaksi (MASUK / KELUAR): ").strip().upper()

            if jenis not in ("MASUK", "KELUAR"):
                print("[INPUT ERROR] Jenis transaksi hanya boleh 'MASUK' atau 'KELUAR'!")
                continue

            try:
                jumlah = int(input("Masukkan Jumlah Unit: "))
                if jumlah <= 0:
                    print("[INPUT ERROR] Jumlah unit harus lebih dari 0!")
                    continue

                keterangan = input("Keterangan (cth: Pengadaan Proyek / Pemakaian Lapangan): ").strip()
                if not keterangan:
                    keterangan = "-"

                if service.catat_transaksi_stok(kode, jenis, jumlah, keterangan):
                    print(f"[SUKSES] Transaksi {jenis} sebanyak {jumlah} unit untuk '{kode}' berhasil dicatat!")
            except ValueError:
                print("[INPUT ERROR] Jumlah unit harus berupa angka bulat!")

        # MENU 5: LIHAT RIWAYAT TRANSAKSI (SQL JOIN)
        elif pilihan == "5":
            print("\n--- 20 RIWAYAT TRANSAKSI TERBARU ---")
            riwayat = service.ambil_riwayat_transaksi()
            if not riwayat:
                print("[INFO] Belum ada catatan transaksi stok.")
            else:
                print(f"{'ID':<4} | {'WAKTU':<16} | {'KODE':<8} | {'NAMA BARANG':<18} | {'TIPE':<7} | {'JML':<5} | {'KETERANGAN'}")
                print("-" * 92)
                for row in riwayat:
                    waktu_str = row[1].strftime("%Y-%m-%d %H:%M")
                    print(
                        f"{row[0]:<4} | "
                        f"{waktu_str:<16} | "
                        f"{row[2]:<8} | "
                        f"{row[3]:<18} | "
                        f"{row[4]:<7} | "
                        f"{row[5]:<5} | "
                        f"{row[6]}"
                    )

        # MENU 6: LAPORAN RINGKASAN ASET (SQL AGGREGATION)
        elif pilihan == "6":
            print("\n--- LAPORAN RINGKASAN ASET GUDANG PGN ---")
            laporan = service.laporan_aset()
            print(f"Total Jenis Item Terdaftar : {laporan['total_jenis']} jenis barang")
            print(f"Total Fisik Keseluruhan  : {laporan['total_unit']:,} unit")
            print(f"Total Nilai Aset Gudang    : Rp {laporan['total_nilai']:,.2f}")

        # MENU 7: HAPUS BARANG
        elif pilihan == "7":
            print("\n--- HAPUS BARANG ---")
            kode = input("Masukkan Kode Barang yang ingin dihapus: ").strip().upper()
            konfirmasi = input(f"Hapus '{kode}' beserta seluruh riwayat transaksinya? (y/n): ").strip().lower()
            
            if konfirmasi == 'y':
                if service.hapus_barang(kode):
                    print(f"[SUKSES] Data barang '{kode}' berhasil dihapus dari database!")
                else:
                    print(f"[GAGAL] Barang dengan kode '{kode}' tidak ditemukan.")

        # MENU 8: KELUAR
        elif pilihan == "8":
            print("\nTerima kasih telah menggunakan Sistem Inventaris PGN!")
            sys.exit(0)

        else:
            print("[ERROR] Pilihan tidak valid, silakan masukkan angka 1-8.")

if __name__ == "__main__":
    main()