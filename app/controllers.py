# app/controllers.py

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app import db # Mengimpor objek db SQLAlchemy Anda
from .models import Book, Category, Member, Loan # Mengimpor model-model Anda

# --- Pydantic Models (Asumsi ini ada di app/models.py atau app/schemas.py) ---
# Saya mengulang definisi ini di sini untuk konteks,
# tapi idealnya Anda mengimpornya dari app/models.py atau app/schemas.py
# agar tidak terjadi duplikasi.

from pydantic import BaseModel, Field
from datetime import date

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    author: Optional[str] = Field(None, max_length=64)
    year: Optional[int] = None
    category_id: Optional[int] = None
    status: Optional[str] = 'available' # Default status

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    author: Optional[str] = Field(None, max_length=64)
    year: Optional[int] = None
    category_id: Optional[int] = None
    status: Optional[str] = None

# --- Controller untuk Book (Buku) ---

def get_all_books() -> List[Book]:
    """
    Mengambil semua buku dari database.
    """
    try:
        return db.session.query(Book).all()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error fetching all books: {e}")
        return [] # Atau raise HTTPException di routes jika lebih suka

def get_book_by_id(book_id: int) -> Optional[Book]:
    """
    Mengambil detail satu buku berdasarkan ID-nya.
    """
    try:
        return db.session.query(Book).filter_by(id=book_id).first()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error fetching book by ID {book_id}: {e}")
        return None

def create_book(book_data: BookCreate) -> Optional[Book]:
    """
    Menambahkan buku baru ke database.
    Menerima data sebagai Pydantic model (BookCreate).
    """
    try:
        # Periksa apakah category_id valid jika disediakan
        if book_data.category_id:
            category = db.session.query(Category).filter_by(id=book_data.category_id).first()
            if not category:
                # Ini bisa jadi HTTPException di routes, atau ditangani di sini
                print(f"Category with ID {book_data.category_id} not found.")
                return None

        new_book = Book(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            category_id=book_data.category_id,
            status=book_data.status
        )
        db.session.add(new_book)
        db.session.commit() # Simpan perubahan ke database
        db.session.refresh(new_book) # Refresh objek untuk mendapatkan ID yang di-generate DB
        return new_book
    except SQLAlchemyError as e:
        db.session.rollback() # Gulirkan kembali transaksi jika ada kesalahan
        print(f"Error creating book: {e}")
        return None

def update_book(book_id: int, book_data: BookUpdate) -> Optional[Book]:
    """
    Memperbarui detail buku yang sudah ada.
    Menerima data sebagai Pydantic model (BookUpdate).
    """
    try:
        book = db.session.query(Book).filter_by(id=book_id).first()
        if not book:
            return None # Buku tidak ditemukan

        # Periksa apakah category_id valid jika disediakan
        if book_data.category_id is not None:
            category = db.session.query(Category).filter_by(id=book_data.category_id).first()
            if not category:
                print(f"Category with ID {book_data.category_id} not found for update.")
                return None

        # Perbarui field yang ada di book_data
        for field, value in book_data.dict(exclude_unset=True).items():
            setattr(book, field, value)

        db.session.commit() # Simpan perubahan ke database
        db.session.refresh(book)
        return book
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating book {book_id}: {e}")
        return None

def delete_book(book_id: int) -> bool:
    """
    Menghapus buku dari database berdasarkan ID-nya.
    Mengembalikan True jika berhasil dihapus, False jika buku tidak ditemukan.
    """
    try:
        book = db.session.query(Book).filter_by(id=book_id).first()
        if not book:
            return False # Buku tidak ditemukan

        db.session.delete(book)
        db.session.commit() # Simpan perubahan ke database
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting book {book_id}: {e}")
        return False

# --- Controller untuk Category (Contoh Sederhana) ---
# Anda bisa mengembangkan ini lebih lanjut dengan CRUD untuk Category juga

def get_all_categories() -> List[Category]:
    """
    Mengambil semua kategori dari database.
    """
    try:
        return db.session.query(Category).all()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error fetching all categories: {e}")
        return []

def get_category_by_id(category_id: int) -> Optional[Category]:
    """
    Mengambil detail satu kategori berdasarkan ID-nya.
    """
    try:
        return db.session.query(Category).filter_by(id=category_id).first()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error fetching category by ID {category_id}: {e}")
        return None

# --- Controller untuk Member dan Loan (sebagai placeholder) ---
# Anda akan mengisi ini dengan logika CRUD serupa untuk Member dan Loan
# ...