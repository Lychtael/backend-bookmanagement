
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
=======
from app.models import db, Book, Category, Member, Loan
from flask import jsonify, request
from datetime import date
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# --- Authentication Controllers ---
# --- Authentication Controllers ---
def register_member_controller(): # <--- ENSURE THIS FUNCTION IS HERE
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({"message": "Name, email, and password are required fields"}), 400

    if Member.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Member with this email already exists"}), 409

    new_member = Member(name=data['name'], email=data['email'])
    new_member.set_password(data['password'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Member registered successfully", "member": new_member.to_dict()}), 201

def login_member_controller(): # <--- AND THIS ONE
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({"message": "Email and password are required fields"}), 400

    member = Member.query.filter_by(email=data['email']).first()
    if not member or not member.check_password(data['password']):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(member.id))
    return jsonify(access_token=access_token), 200

# --- Book Controllers ---
# The existing book controllers can remain the same, but you might want to add @jwt_required
# to protect them if they are for authenticated users only.
# For example:
# @jwt_required()
def get_all_books_controller():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# Add @jwt_required() to controllers that need authentication
def get_book_by_id_controller(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"message": f"Book with ID {book_id} not found"}), 404

@jwt_required()
def create_book_controller():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'author')):
        return jsonify({"message": "Title and author are required fields"}), 400

    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data.get('year'),
        category_id=data.get('category_id'),
        status=data.get('status', 'available')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book created successfully", "book": new_book.to_dict()}), 201

@jwt_required()
def update_book_controller(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    if 'category_id' in data:
        book.category_id = data['category_id']
    if 'status' in data:
        if data['status'] in ['available', 'borrowed']:
            book.status = data['status']
        else:
            return jsonify({"message": "Invalid status value. Must be 'available' or 'borrowed'"}), 400

    db.session.commit()
    return jsonify({"message": "Book updated successfully", "book": book.to_dict()}), 200

@jwt_required()
def delete_book_controller(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    # Cek apakah buku sedang dipinjam
    if Loan.query.filter_by(book_id=book_id, return_date=None).first():
        return jsonify({"message": "Cannot delete book: it is currently borrowed"}), 400

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

# --- Category Controllers ---
def get_all_categories_controller():
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200

def get_category_by_id_controller(category_id):
    category = Category.query.get(category_id)
    if category:
        return jsonify(category.to_dict()), 200
    return jsonify({"message": f"Category with ID {category_id} not found"}), 404

@jwt_required()
def create_category_controller():
    data = request.get_json()
    if not data or not 'name' in data:
        return jsonify({"message": "Category name is required"}), 400
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({"message": "Category with this name already exists"}), 409 # Conflict

    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created successfully", "category": new_category.to_dict()}), 201

@jwt_required()
def update_category_controller(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": f"Category with ID {category_id} not found"}), 404
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"message": "Category name is required for update"}), 400
    if Category.query.filter_by(name=data['name']).first() and data['name'] != category.name:
        return jsonify({"message": "Category with this name already exists"}), 409

    category.name = data['name']
    db.session.commit()
    return jsonify({"message": "Category updated successfully", "category": category.to_dict()}), 200

@jwt_required()
def delete_category_controller(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": f"Category with ID {category_id} not found"}), 404
    # Cek apakah ada buku yang terkait dengan kategori ini
    if Book.query.filter_by(category_id=category_id).first():
        return jsonify({"message": "Cannot delete category: books are associated with it"}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200

# --- Member Controllers ---
# Member controllers might have public read access, but creation/update/deletion protected
def get_all_members_controller():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members]), 200

def get_member_by_id_controller(member_id):
    member = Member.query.get(member_id)
    if member:
        return jsonify(member.to_dict()), 200
    return jsonify({"message": f"Member with ID {member_id} not found"}), 404

# Register is handled by register_member_controller, so create_member_controller is removed or adapted.
# update_member_controller and delete_member_controller should be protected by JWT.
@jwt_required()
def update_member_controller(member_id):
    # Optional: check if the authenticated user is updating their own profile
    current_user_id = get_jwt_identity()
    if current_user_id != member_id:
        return jsonify({"message": "You are not authorized to update this member's profile"}), 403

    member = Member.query.get(member_id)
    if not member:
        return jsonify({"message": f"Member with ID {member_id} not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    if 'name' in data:
        member.name = data['name']
    if 'email' in data:
        if Member.query.filter_by(email=data['email']).first() and data['email'] != member.email:
            return jsonify({"message": "Member with this email already exists"}), 409
        member.email = data['email']
    if 'password' in data: # Allow password change
        member.set_password(data['password'])

    db.session.commit()
    return jsonify({"message": "Member updated successfully", "member": member.to_dict()}), 200

@jwt_required()
def delete_member_controller(member_id):
    current_user_id = get_jwt_identity()
    if current_user_id != member_id:
        return jsonify({"message": "You are not authorized to delete this member"}), 403

    member = Member.query.get(member_id)
    if not member:
        return jsonify({"message": f"Member with ID {member_id} not found"}), 404
    # Cek apakah member memiliki pinjaman aktif
    if Loan.query.filter_by(member_id=member_id, return_date=None).first():
        return jsonify({"message": "Cannot delete member: they have active loans"}), 400

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted successfully"}), 200

# --- Loan Controllers ---
# Loan controllers should also be protected by JWT.
@jwt_required()
def get_all_loans_controller():
    loans = Loan.query.all()
    return jsonify([loan.to_dict() for loan in loans]), 200

@jwt_required()
def get_loan_by_id_controller(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        return jsonify(loan.to_dict()), 200
    return jsonify({"message": f"Loan with ID {loan_id} not found"}), 404

@jwt_required()
def create_loan_controller():
    data = request.get_json()
    if not data or not all(k in data for k in ('book_id', 'member_id', 'loan_date')):
        return jsonify({"message": "book_id, member_id, and loan_date are required fields"}), 400

    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({"message": f"Book with ID {data['book_id']} not found"}), 404
    if book.status == 'borrowed':
        return jsonify({"message": f"Book '{book.title}' is currently borrowed"}), 400

    member = Member.query.get(data['member_id'])
    if not member:
        return jsonify({"message": f"Member with ID {data['member_id']} not found"}), 404

    try:
        loan_date = date.fromisoformat(data['loan_date'])
    except ValueError:
        return jsonify({"message": "Invalid loan_date format. Use YYYY-MM-DD"}), 400

    new_loan = Loan(
        book_id=data['book_id'],
        member_id=data['member_id'],
        loan_date=loan_date
    )
    db.session.add(new_loan)
    book.status = 'borrowed' # Update status buku menjadi 'borrowed'
    db.session.commit()
    return jsonify({"message": "Loan created successfully", "loan": new_loan.to_dict()}), 201

@jwt_required()
def return_book_controller(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"message": f"Loan with ID {loan_id} not found"}), 404
    if loan.return_date:
        return jsonify({"message": "Book already returned for this loan"}), 400

    loan.return_date = date.today() # Set tanggal kembali ke hari ini
    loan.book.status = 'available' # Update status buku menjadi 'available'
    db.session.commit()
    return jsonify({"message": "Book returned successfully", "loan": loan.to_dict()}), 200

@jwt_required()
def delete_loan_controller(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"message": f"Loan with ID {loan_id} not found"}), 404
    
    # Jika buku belum dikembalikan, kembalikan status buku ke 'available'
    if loan.book and not loan.return_date:
        loan.book.status = 'available'

    db.session.delete(loan)
    db.session.commit()
    return jsonify({"message": "Loan deleted successfully"}), 200

