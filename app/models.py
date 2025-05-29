# models.py

from app import db # Asumsi 'db' sudah diinisialisasi dari SQLAlchemy
# from sqlalchemy import func # Tidak dibutuhkan untuk struktur dasar ini, kecuali untuk timestamp otomatis

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.Enum('available', 'borrowed'), default='available')

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True) # diasumsikan email harus unik

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    loan_date = db.Column(db.Date)
    return_date = db.Column(db.Date)