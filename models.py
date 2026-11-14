from multiprocessing import Value


class Barang:
    """ Model Data Barang dengan penerapan Encapsulation (Atribut Private & Getter/Setter)."""
    def __init__(self, kode_barang:str, nama_barang:str, stok:int, harga:float, id_barang:int = None):
        self.__id = id_barang
        self.__kode_barang = kode_barang
        self.__nama_barang = nama_barang
        self.__stok = stok
        self.__harga = harga
        
    def get_id(self):
        return self.__id
    
    def get_kode_barang(self):
        return self.__kode_barang
    
    def get_nama_barang(self):
        return self.__nama_barang
    
    def get_stok(self):
        return self.__stok
    
    def get_harga(self):
        return self.__harga
    
    def set_stok(self, stok_baru:int):
        if stok_baru >= 0:
            self.__stok = stok_baru
        else:
            raise ValueError("Stok tidak boleh bernilai negatif!")
        
    def set_harga(self, harga_baru: float):
        if harga_baru > 0:
            self.__harga = harga_baru
        else:
            raise ValueError("Harga barang harus lebih dari Rp.0!")
        