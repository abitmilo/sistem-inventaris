from pydantic import BaseModel, Field

class BarangCreate(BaseModel):
    kode_barang: str = Field(..., min_length=2, max_length=20, examples=["BRG003"])
    nama_barang: str = Field(..., min_length=2, max_length=100, examples=["Meteran Gas Digital"])
    stok: int = Field(..., ge=0, examples=[25])
    harga: float = Field(..., gt=0, examples=[1250000.0])

class TransaksiCreate(BaseModel):
    kode_barang: str = Field(..., min_length=2, max_length=20, examples=["BRG001"])
    jenis_transaksi: str = Field(..., pattern="^(MASUK|KELUAR)$", examples=["MASUK"])
    jumlah: int = Field(..., gt=0, examples=[10])
    keterangan: str = Field(default="-", max_length=150, examples=["Pengadaan Gudang Pusat"])