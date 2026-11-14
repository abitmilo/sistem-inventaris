from typing import Optional
from fastapi import FastAPI, HTTPException, status
from models import Barang
from services import GudangService
from schemas import BarangCreate, TransaksiCreate

app = FastAPI(
    title="Sistem Inventaris Gudang PGN API",
    description="REST API manajemen inventaris dan riwayat mutasi stok berbasis PostgreSQL.",
    version="1.0.0"
)

service = GudangService()

def serialize_barang(item: Barang) -> dict:
    """Mengubah objek Barang (atribut privat) menjadi dictionary agar bisa dikirim sebagai JSON."""
    return {
        "id": item.get_id(),
        "kode_barang": item.get_kode_barang(),
        "nama_barang": item.get_nama_barang(),
        "stok": item.get_stok(),
        "harga": item.get_harga()
    }

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "service": "Sistem Inventaris Gudang PGN API",
        "docs_url": "/docs"
    }

# 1. GET ALL & SEARCH BARANG (?search=pipa)
@app.get("/api/v1/barang", tags=["Inventaris"])
def get_daftar_barang(search: Optional[str] = None):
    if search:
        hasil = service.cari_barang(search.strip())
    else:
        hasil = service.ambil_semua_barang()

    return {
        "total_data": len(hasil),
        "data": [serialize_barang(item) for item in hasil]
    }

# 2. TAMBAH BARANG BARU
@app.post("/api/v1/barang", status_code=status.HTTP_201_CREATED, tags=["Inventaris"])
def tambah_barang(payload: BarangCreate):
    kode = payload.kode_barang.strip().upper()
    barang_baru = Barang(
        kode_barang=kode,
        nama_barang=payload.nama_barang.strip(),
        stok=payload.stok,
        harga=payload.harga
    )

    sukses = service.tambah_barang(barang_baru)
    if not sukses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal menyimpan barang. Kode '{kode}' mungkin sudah terdaftar."
        )

    return {
        "message": f"Barang '{kode}' berhasil ditambahkan.",
        "data": serialize_barang(barang_baru)
    }

# 3. CATAT TRANSAKSI STOK (MASUK / KELUAR)
@app.post("/api/v1/transaksi", status_code=status.HTTP_201_CREATED, tags=["Transaksi Stok"])
def catat_transaksi(payload: TransaksiCreate):
    kode = payload.kode_barang.strip().upper()
    sukses = service.catat_transaksi_stok(
        kode_barang=kode,
        jenis=payload.jenis_transaksi,
        jumlah=payload.jumlah,
        keterangan=payload.keterangan.strip()
    )

    if not sukses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaksi ditolak. Pastikan kode '{kode}' terdaftar dan stok mencukupi untuk transaksi KELUAR."
        )

    return {
        "message": f"Transaksi {payload.jenis_transaksi} sebanyak {payload.jumlah} unit untuk '{kode}' berhasil dicatat."
    }

# 4. LIHAT RIWAYAT TRANSAKSI (SQL JOIN)
@app.get("/api/v1/transaksi", tags=["Transaksi Stok"])
def get_riwayat_transaksi():
    rows = service.ambil_riwayat_transaksi()
    data_riwayat = [
        {
            "id": row[0],
            "tanggal": row[1],
            "kode_barang": row[2],
            "nama_barang": row[3],
            "jenis_transaksi": row[4],
            "jumlah": row[5],
            "keterangan": row[6]
        }
        for row in rows
    ]
    return {
        "total_data": len(data_riwayat),
        "data": data_riwayat
    }

# 5. LAPORAN RINGKASAN ASET (SQL AGGREGATION)
@app.get("/api/v1/laporan/aset", tags=["Laporan"])
def get_laporan_aset():
    return service.laporan_aset()

# 6. HAPUS BARANG
@app.delete("/api/v1/barang/{kode_barang}", tags=["Inventaris"])
def hapus_barang(kode_barang: str):
    kode = kode_barang.strip().upper()
    sukses = service.hapus_barang(kode)

    if not sukses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Barang dengan kode '{kode}' tidak ditemukan."
        )

    return {"message": f"Barang '{kode}' beserta riwayat transaksinya berhasil dihapus."}