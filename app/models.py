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

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(64))
    year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status = db.Column(db.String(20), default='available')

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
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