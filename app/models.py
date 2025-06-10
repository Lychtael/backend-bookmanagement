# app/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
import uuid # Import uuid for generating IDs

db = SQLAlchemy()

# --- SQLAlchemy Models ---

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship('Book', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class User(db.Model):
    __tablename__ = 'users'
    # Use VARCHAR(50) for id as per your new schema
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')
    sessions = db.relationship('Session', backref='user', lazy='dynamic')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role_id": self.role_id,
            "role_name": self.role.name if self.role else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Book(db.Model):
    __tablename__ = 'books'
    # Use VARCHAR(50) for id
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=False)
    imageUrl = db.Column(db.String(500), nullable=False)
    isAvailable = db.Column(db.Boolean, nullable=False, default=True) # Renamed from 'status'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic') # Updated relationship name

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "description": self.description,
            "imageUrl": self.imageUrl,
            "isAvailable": self.isAvailable,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Borrow(db.Model): # Renamed from Loan
    __tablename__ = 'borrows'
    # Use VARCHAR(50) for id
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = db.Column(db.String(50), db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('BORROWED', 'RETURNED', 'OVERDUE'), nullable=False, default='BORROWED')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "loan_date": self.loan_date.isoformat() if self.loan_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "status": self.status,
            "book_title": self.book.title if self.book else None,
            "user_name": self.user.name if self.user else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.String(500), primary_key=True) # PASTIKAN INI SUDAH 500
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    expires_at = db.Column(db.TIMESTAMP, nullable=False)
    # ...
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }

# --- Pydantic Models for API Input/Output ---

class BookSchema(BaseModel):
    id: str
    title: str
    author: str
    year: Optional[int] = None
    description: str
    imageUrl: str
    isAvailable: bool
    category_id: Optional[int] = None
    category_name: Optional[str] = None # Added for more informative response

    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: Optional[int] = None
    description: str = Field(..., min_length=1)
    imageUrl: str = Field(..., min_length=1)
    isAvailable: Optional[bool] = True
    category_id: Optional[int] = None

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1)
    imageUrl: Optional[str] = Field(None, min_length=1)
    isAvailable: Optional[bool] = None
    category_id: Optional[int] = None

class CategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class RoleSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: str
    name: str
    email: str
    role_id: int
    role_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserRegister(BaseModel): # Renamed for clarity in registration
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=6)
    role_id: Optional[int] = 2 # Default to User role

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None

class BorrowSchema(BaseModel): # Renamed from LoanSchema
    id: str
    book_id: str
    user_id: str
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    book_title: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class BorrowCreate(BaseModel): # Renamed from LoanCreate
    book_id: str
    user_id: str
    loan_date: Optional[date] = Field(default_factory=date.today)
    due_date: date

class BorrowReturn(BaseModel): # Renamed from LoanReturn
    return_date: Optional[date] = Field(default_factory=date.today)

class SessionSchema(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }