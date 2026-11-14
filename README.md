# Sistem Manajemen Inventaris Gudang PGN (CLI & REST API)

Sistem manajemen inventaris aset dan audit mutasi stok berbasis **Clean Architecture** menggunakan Python, PostgreSQL, dan FastAPI. Proyek ini menyediakan dua antarmuka sekaligus—**Command-Line Interface (CLI)** dan **REST API**—yang berbagi satu *service layer* dan database relasional yang sama.

## Fitur Utama
- **Dual Interface (CLI & REST API):** Mendukung operasional terminal interaktif (`main.py`) maupun integrasi HTTP JSON (`api.py`) dengan dokumentasi interaktif Swagger UI.
- **OOP Encapsulation & Validasi Berlapis:** Isolasi atribut privat pada model domain (`models.py`) serta validasi *payload* JSON otomatis menggunakan Pydantic (`schemas.py`).
- **Transaksi Atomik & Integritas Relasional:** Pencatatan mutasi stok (`MASUK`/`KELUAR`) yang terikat *Foreign Key* dengan mekanisme `commit` dan `rollback`.
- **Pencarian & Pelaporan SQL:** Pencarian *case-insensitive* (`ILIKE`), riwayat audit mutasi (`SQL JOIN`), dan agregasi nilai aset (`SUM` & `COALESCE`).
- **Keamanan Kredensial:** Isolasi konfigurasi database melalui `.env` serta perlindungan query menggunakan *parameterized queries* (`%s`).

## Struktur Proyek
```text
proyek_inventory_pgn/
├── .env                # Kredensial database (diabaikan Git)
├── .gitignore          # Daftar pengecualian file/folder Git
├── requirements.txt    # Daftar dependensi library Python
├── db_config.py        # Manajemen koneksi PostgreSQL
├── models.py           # Model data Barang (OOP Encapsulation)
├── services.py         # Layer logika bisnis & eksekusi query SQL
├── main.py             # Antarmuka menu CLI interaktif
├── schemas.py          # Skema validasi request JSON (Pydantic)
└── api.py              # Layer endpoint REST API (FastAPI)