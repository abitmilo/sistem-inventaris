import os 
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    """Membuat dan mengembalikan objek koneksi database PostgreSQL."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return connection
    except OperationalError as e:
        print(f"[ERROR] Gagal terhubung ke database PostgreSQL: {e}")
        return None
    
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("[TES KONEKSI SUKSES] Berhasil membaca .env dan terhubung ke PostgreSQL.")