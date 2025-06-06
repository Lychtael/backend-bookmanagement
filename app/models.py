
# app/models.py (Pastikan ini ada di file models.py Anda)

from app import db # Ini mengacu pada objek db dari __init__.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# --- SQLAlchemy Models ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    # Relasi balik ke Book jika diperlukan
    books = db.relationship('Book', backref='category', lazy=True)
=======
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy() # Ini akan diinisialisasi di __init__.py, tapi perlu di sini untuk definisi model

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100))
    year = db.Column(db.Integer) # Menggunakan 'year' sesuai dengan model Anda
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.Enum('available', 'borrowed'), default='available')


    # Relasi ke Category
    category = db.relationship('Category', backref='books')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "category_id": self.category_id,
            "status": self.status,
            "category_name": self.category.name if self.category else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Tambahkan unique=True untuk nama kategori

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False) # diasumsikan email harus unik dan tidak boleh null
    password_hash = db.Column(db.String(255), nullable=False) # Kolom untuk menyimpan hash password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
            # Do NOT include password_hash in to_dict for security reasons
        }

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    loan_date = db.Column(db.Date)

    return_date = db.Column(db.Date)

# --- Pydantic Models for API Input/Output ---
# Ini digunakan untuk validasi data dari request body dan serialisasi response
class BookSchema(BaseModel):
    id: int
    title: str
    author: Optional[str]
    year: Optional[int]
    category_id: Optional[int]
    status: str

    class Config:
        orm_mode = True # Penting untuk mengkonversi SQLAlchemy ORM object ke Pydantic

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    author: Optional[str] = Field(None, max_length=64)
    year: Optional[int] = None
    category_id: Optional[int] = None
    status: Optional[str] = 'available'

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    author: Optional[str] = Field(None, max_length=64)
    year: Optional[int] = None
    category_id: Optional[int] = None
    status: Optional[str] = None

# Anda bisa menambahkan Pydantic Schema untuk Category, Member, Loan juga
class CategorySchema(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
=======
    return_date = db.Column(db.Date, nullable=True) # return_date bisa null jika buku belum dikembalikan

    # Relasi ke Book dan Member
    book = db.relationship('Book', backref='loans')
    member = db.relationship('Member', backref='loans')

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "loan_date": self.loan_date.isoformat() if self.loan_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "book_title": self.book.title if self.book else None,
            "member_name": self.member.name if self.member else None
        }

