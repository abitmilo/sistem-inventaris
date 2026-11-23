import pytest
from fastapi.testclient import TestClient
from api import app, service

client = TestClient(app)
KODE_TEST = "TEST-PGN-999"

@pytest.fixture(scope="module", autouse=True)
def bersihkan_data_uji():
    """ Memastikan data uji coba selalu bersih sebelum dan sesuadah pengujian dijalankan."""
    service.hapus_barang(KODE_TEST)
    yield
    service.hapus_barang(KODE_TEST)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    
def test_tambah_barang_sukses():
    payload = {
        "kode_barang": KODE_TEST,
        "nama_barang": "Regulator gas uji coba",
        "stok":10,
        "harga": 350000.00
    }
    response = client.post("/api/v1/barang", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["kode_barang"] == KODE_TEST
    
def test_tambah_barang_duplikat_ditolak():
    payload= {
        "kode_barang": KODE_TEST,
        "nama_barang": "Regulator Duplikat",
        "stok": 5,
        "harga": 100000.0
    }
    response = client.post("/api/v1/barang", json=payload)
    assert response.status_code == 400
    
def test_validasi_pydantic_stok_negatif():
    payload = {
        "kode_barang": "TEST-INVALID",
        "nama_barang": "Barang stok minus",
        "stok": -5,
        "harga": 50000.0
    }
    response = client.post(f"/api/v1/barang", json=payload)
    assert response.status_code == 422
    
def test_cari_barang_terdaftar():
    response = client.get(f"/api/v1/barang?search={KODE_TEST}")
    assert response.status_code == 200
    body = response.json()
    assert body["total_data"] == 1
    assert body["data"][0]["stok"] == 10
    
def test_transaksi_stok_masuk_sukses():
    payload = {
        "kode_barang": KODE_TEST,
        "jenis_transaksi": "MASUK",
        "jumlah": 5,
        "keterangan": "Pengujian stok masuk Pytest"
    }
    response = client.post("/api/v1/transaksi", json=payload)
    assert response.status_code == 201

    # Verifikasi stok bertambah dari 10 menjadi 15
    cek = client.get(f"/api/v1/barang?search={KODE_TEST}")
    assert cek.json()["data"][0]["stok"] == 15

def test_transaksi_stok_keluar_melebihi_batas_ditolak():
    payload = {
        "kode_barang": KODE_TEST,
        "jenis_transaksi": "KELUAR",
        "jumlah": 9999,
        "keterangan": "Pengujian penolakan stok kurang"
    }
    response = client.post("/api/v1/transaksi", json=payload)
    assert response.status_code == 400

def test_riwayat_transaksi_dan_laporan_aset():
    res_riwayat = client.get("/api/v1/transaksi")
    assert res_riwayat.status_code == 200
    assert res_riwayat.json()["total_data"] >= 1

    res_laporan = client.get("/api/v1/laporan/aset")
    assert res_laporan.status_code == 200
    assert "total_nilai" in res_laporan.json()

def test_hapus_barang_dan_validasi_not_found():
    # Penghapusan pertama harus berhasil (200 OK)
    res_hapus = client.delete(f"/api/v1/barang/{KODE_TEST}")
    assert res_hapus.status_code == 200

    # Penghapusan kedua pada kode yang sama harus ditolak (404 Not Found)
    res_ulang = client.delete(f"/api/v1/barang/{KODE_TEST}")
    assert res_ulang.status_code == 404