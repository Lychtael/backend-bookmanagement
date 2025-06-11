import os

class Config:
    # Mengambil variabel lingkungan untuk koneksi MySQL
    # Pastikan variabel ini (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
    # sudah ada di file .env Anda atau di lingkungan sistem Anda.
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password' # Sesuaikan dengan password root MySQL Anda
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'perpus'

    # Ini adalah URL koneksi utama yang akan digunakan SQLAlchemy dan Flask-Migrate
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disarankan untuk False untuk performa
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super_secret_jwt_key'