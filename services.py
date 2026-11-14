from db_config import get_connection
from models import Barang

class GudangService:
    """ Service layer untuk mengelola operasi CRUD inventaris di databse PostgreSQL."""
    
    def tambah_barang(self, barang:Barang) -> bool:
        """Menambahkan data barang baru ke database."""
        query = """
        INSERT INTO tb_inventaris_pgn (kode_barang, nama_barang, stok, harga)
        VALUES (%s,%s,%s,%s);
        """
        
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (
                barang.get_kode_barang(),
                barang.get_nama_barang(),
                barang.get_stok(),
                barang.get_harga()
            ))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"[ERROR] Gagal menambah barang: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def ambil_semua_barang(self) -> list:
        """Mengambil seluruh dafatar barang dari database dan mengembalikannya sebagai list Objek Barang."""
        query = "SELECT id, Kode_barang, nama_barang, stok, harga FROM tb_inventaris_pgn ORDER BY id ASC;"
        conn = get_connection()
        daftar_barang = []
        
        if not conn:
            return daftar_barang        
        
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            for row in rows:
                barang = Barang(
                    id_barang=row[0],
                    kode_barang=row[1],
                    nama_barang=row[2],
                    stok=row[3],
                    harga=float(row[4]),
                )
                daftar_barang.append(barang)
                
            
        except Exception as e:
            print(f"[ERROR] Gagal mengambil data barang: {e}")
        finally:
            conn.close()
        
        return daftar_barang
    
    def update_stok(self, kode_barang:str, stok_baru:int) -> bool:
        """Mengubah jumlah stok barang berdasarkan kode barang."""
        query = "UPDATE tb_inventaris_pgn SET stok = %s WHERE kode_barang = %s,"
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (stok_baru, kode_barang))
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        except Exception as e:
            print(f"[ERROR] Gagal mengupdate stok: {e}")
            conn.rollback()
            return False
        finally:
            conn.close
    
    def hapus_barang(self, kode_barang: str) -> bool:
        """Menghapus baris data barang dari database berdasarkan kode barang."""
        query = "DELETE FROM tb_inventaris_pgn WHERE kode_barang = %s;"
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query,(kode_barang,))
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        except Exception as e:
            print(f"[ERROR] Gagal menghapus barang: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def cari_barang(self, keyword: str) -> list:
        """Mencari barang berdasarkan potongan kode atau nama barang (case-insensitive)."""
        query = """
        SELECT id, kode_barang, nama_barang, stok, harga 
        FROM tb_inventaris_pgn 
        WHERE kode_barang ILIKE %s OR nama_barang ILIKE %s 
        ORDER BY id ASC;
        """
        conn = get_connection()
        hasil_pencarian = []

        if not conn:
            return hasil_pencarian

        try:
            cursor = conn.cursor()
            pola = f"%{keyword}%"
            cursor.execute(query, (pola, pola))
            rows = cursor.fetchall()
            cursor.close()

            for row in rows:
                barang = Barang(
                    id_barang=row[0],
                    kode_barang=row[1],
                    nama_barang=row[2],
                    stok=row[3],
                    harga=float(row[4])
                )
                hasil_pencarian.append(barang)
        except Exception as e:
            print(f"[ERROR] Gagal mencari barang: {e}")
        finally:
            conn.close()

        return hasil_pencarian

    def laporan_aset(self) -> dict:
        """Menghitung ringkasan jumlah jenis barang, total unit fisik, dan total nilai aset."""
        query = """
        SELECT 
            COUNT(id), 
            COALESCE(SUM(stok), 0), 
            COALESCE(SUM(stok * harga), 0) 
        FROM tb_inventaris_pgn;
        """
        conn = get_connection()
        ringkasan = {"total_jenis": 0, "total_unit": 0, "total_nilai": 0.0}

        if not conn:
            return ringkasan

        try:
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()

            if row:
                ringkasan["total_jenis"] = row[0]
                ringkasan["total_unit"] = row[1]
                ringkasan["total_nilai"] = float(row[2])
        except Exception as e:
            print(f"[ERROR] Gagal menghitung laporan aset: {e}")
        finally:
            conn.close()

        return ringkasan

    def catat_transaksi_stok(self, kode_barang: str, jenis: str, jumlah: int, keterangan: str = "-") -> bool:
        """Mengubah stok sekaligus mencatat riwayat transaksi dalam satu transaksi atomik."""
        jenis = jenis.upper()
        if jenis not in ("MASUK", "KELUAR") or jumlah <= 0:
            return False

        conn = get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # 1. Cek ketersediaan barang dan stok saat ini
            cursor.execute("SELECT stok FROM tb_inventaris_pgn WHERE kode_barang = %s;", (kode_barang,))
            hasil = cursor.fetchone()

            if not hasil:
                print(f"[GAGAL] Barang dengan kode '{kode_barang}' tidak ditemukan.")
                return False

            stok_sekarang = hasil[0]

            # 2. Validasi jika barang keluar melebihi stok gudang
            if jenis == "KELUAR" and stok_sekarang < jumlah:
                print(f"[GAGAL] Stok tidak mencukupi! Stok tersedia: {stok_sekarang}")
                return False

            stok_baru = stok_sekarang + jumlah if jenis == "MASUK" else stok_sekarang - jumlah

            # 3. Jalankan UPDATE stok & INSERT riwayat secara bersamaan
            cursor.execute(
                "UPDATE tb_inventaris_pgn SET stok = %s WHERE kode_barang = %s;",
                (stok_baru, kode_barang)
            )
            cursor.execute(
                """
                INSERT INTO tb_transaksi_pgn (kode_barang, jenis_transaksi, jumlah, keterangan)
                VALUES (%s, %s, %s, %s);
                """,
                (kode_barang, jenis, jumlah, keterangan)
            )

            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"[ERROR] Transaksi stok gagal: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def ambil_riwayat_transaksi(self) -> list:
        """Mengambil 20 riwayat transaksi terbaru beserta nama barangnya (SQL JOIN)."""
        query = """
        SELECT t.id, t.tanggal, t.kode_barang, b.nama_barang, t.jenis_transaksi, t.jumlah, t.keterangan
        FROM tb_transaksi_pgn t
        JOIN tb_inventaris_pgn b ON t.kode_barang = b.kode_barang
        ORDER BY t.tanggal DESC
        LIMIT 20;
        """
        conn = get_connection()
        riwayat = []

        if not conn:
            return riwayat

        try:
            cursor = conn.cursor()
            cursor.execute(query)
            riwayat = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"[ERROR] Gagal mengambil riwayat transaksi: {e}")
        finally:
            conn.close()

        return riwayat