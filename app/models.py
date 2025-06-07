# app/models.py

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# Inisialisasi db di sini untuk definisi model, tapi akan diinisialisasi ulang di create_app
db = SQLAlchemy()

# --- SQLAlchemy Models ---
class Category(db.Model):
    __tablename__ = 'categories' # Pastikan nama tabel konsisten
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Tambahkan unique=True

    # Relasi balik ke Book jika diperlukan. Gunakan `lazy='dynamic'` untuk query yang lebih fleksibel.
    books = db.relationship('Book', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.Enum('available', 'borrowed'), default='available')

    # Relasi ke Category didefinisikan di atas (backref='category')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "category_id": self.category_id,
            "status": self.status,
            "category_name": self.category.name if self.category else None # Mengakses nama kategori
        }

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    # Gunakan 'username' atau 'name' secara konsisten. Anda punya `name` di SQLAlchemy dan `username` di Flask-JWT-Extended (login controller).
    # Saya akan pakai 'name' di model ini agar konsisten dengan `to_dict` Anda.
    # Jika Anda ingin 'username' untuk login, pastikan field ini juga unik.
    name = db.Column(db.String(100), nullable=False, unique=True) # Diasumsikan nama juga unik untuk login
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
            # Do NOT include password_hash for security reasons
        }

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    loan_date = db.Column(db.Date, nullable=False, default=date.today) # loan_date tidak boleh null
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

# --- Pydantic Models for API Input/Output ---
# Ini digunakan untuk validasi data dari request body dan serialisasi response
# Pastikan ini berada di luar definisi kelas SQLAlchemy Model
class BookSchema(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    year: Optional[int] = None
    category_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True # Di Pydantic v2+, orm_mode diganti dengan from_attributes

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

class CategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True # Di Pydantic v2+, orm_mode diganti dengan from_attributes

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)

# Tambahkan Pydantic Models lainnya sesuai kebutuhan
class MemberSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$") # Validasi email sederhana
    password: str = Field(..., min_length=6)

class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: Optional[str] = Field(None, min_length=6)

class LoanSchema(BaseModel):
    id: int
    book_id: int
    member_id: int
    loan_date: date # Menggunakan type `date` dari datetime module
    return_date: Optional[date] = None
    book_title: Optional[str] = None # Untuk respons yang lebih informatif
    member_name: Optional[str] = None # Untuk respons yang lebih informatif

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    loan_date: Optional[date] = Field(default_factory=date.today) # Default hari ini

class LoanReturn(BaseModel):
    return_date: Optional[date] = Field(default_factory=date.today) # Default hari ini