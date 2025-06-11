# app/controllers.py (Corrected and Cleaned)

from flask import jsonify, request
from app.models import db, Book, Category, User, Borrow, Role, Session
from datetime import date, timedelta, datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

# Import the correct Pydantic Models from your models file
from app.models import BookCreate, BookUpdate, CategoryCreate, UserRegister, BorrowCreate, BorrowReturn

# --- Helper function for role-based access control ---
def role_required(role_name):
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.role or user.role.name != role_name:
                return jsonify({"message": f"'{role_name}' role required"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# --- Authentication Controllers ---
def register_user_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    try:
        user_data = UserRegister(**data)
    except Exception as e:
        return jsonify({"message": f"Invalid registration data: {e.errors() if hasattr(e, 'errors') else str(e)}"}), 400
    
    if User.query.filter_by(email=user_data.email).first():
        return jsonify({"message": "User with this email already exists"}), 409

    role = Role.query.get(user_data.role_id)
    if not role:
        return jsonify({"message": f"Role with ID {user_data.role_id} not found"}), 400

    try:
        new_user = User(name=user_data.name, email=user_data.email, role_id=user_data.role_id)
        new_user.set_password(user_data.password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error during registration"}), 500

def login_user_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ['email', 'password']
    if not all(k in data for k in required_fields):
        return jsonify({"message": f"Missing required fields: {', '.join(f for f in required_fields if f not in data)}"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify(access_token=access_token, user_id=user.id, role=user.role.name), 200

# --- Book Controllers ---
def get_all_books_controller():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

def get_book_by_id_controller(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"message": f"Book with ID {book_id} not found"}), 404

@role_required('Admin')
def create_book_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
    try:
        book_data = BookCreate(**data)
    except Exception as e:
        return jsonify({"message": f"Invalid book data: {e.errors() if hasattr(e, 'errors') else str(e)}"}), 400

    if book_data.category_id:
        if not Category.query.get(book_data.category_id):
            return jsonify({"message": f"Category with ID {book_data.category_id} not found"}), 400

    try:
        new_book = Book(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            description=book_data.description,
            imageUrl=book_data.imageUrl,
            isAvailable=book_data.isAvailable,
            category_id=book_data.category_id
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book created successfully", "book": new_book.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while creating book"}), 500

@role_required('Admin')
def update_book_controller(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400
    try:
        book_data = BookUpdate(**data)
    except Exception as e:
        return jsonify({"message": f"Invalid book data: {e.errors() if hasattr(e, 'errors') else str(e)}"}), 400

    if book_data.title is not None: book.title = book_data.title
    if book_data.author is not None: book.author = book_data.author
    if book_data.year is not None: book.year = book_data.year
    if book_data.description is not None: book.description = book_data.description
    if book_data.imageUrl is not None: book.imageUrl = book_data.imageUrl
    if book_data.isAvailable is not None: book.isAvailable = book_data.isAvailable
    if book_data.category_id is not None:
        if not Category.query.get(book_data.category_id):
            return jsonify({"message": f"Category with ID {book_data.category_id} not found"}), 400
        book.category_id = book_data.category_id
    
    try:
        db.session.commit()
        return jsonify({"message": "Book updated successfully", "book": book.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while updating book"}), 500

@role_required('Admin')
def delete_book_controller(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    if Borrow.query.filter_by(book_id=book_id, return_date=None).first():
        return jsonify({"message": "Cannot delete book: it is currently borrowed"}), 400

    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while deleting book"}), 500

# --- Category Controllers ---
def get_all_categories_controller():
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200

def get_category_by_id_controller(category_id):
    category = Category.query.get(category_id)
    if category:
        return jsonify(category.to_dict()), 200
    return jsonify({"message": f"Category with ID {category_id} not found"}), 404

@role_required('Admin')
def create_category_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    try:
        category_data = CategoryCreate(**data)
    except Exception as e:
        return jsonify({"message": f"Invalid category data: {e.errors() if hasattr(e, 'errors') else str(e)}"}), 400

    if Category.query.filter_by(name=category_data.name).first():
        return jsonify({"message": "Category with this name already exists"}), 409

    try:
        new_category = Category(name=category_data.name)
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": "Category created successfully", "category": new_category.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while creating category"}), 500

@role_required('Admin')
def update_category_controller(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": f"Category with ID {category_id} not found"}), 404
    
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"message": "No data provided for update"}), 400

    if Category.query.filter_by(name=data['name']).first() and data['name'] != category.name:
        return jsonify({"message": "Category with this name already exists"}), 409
    
    category.name = data['name']
    try:
        db.session.commit()
        return jsonify({"message": "Category updated successfully", "category": category.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while updating category"}), 500

@role_required('Admin')
def delete_category_controller(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": f"Category with ID {category_id} not found"}), 404
    if Book.query.filter_by(category_id=category_id).first():
        return jsonify({"message": "Cannot delete category: books are associated with it"}), 400

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while deleting category"}), 500

# --- User Controllers ---
@role_required('Admin')
def get_all_users_controller():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@jwt_required()
def get_user_by_id_controller(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": f"User with ID {user_id} not found"}), 404
    return jsonify(user.to_dict()), 200

def update_user_controller(user_id):
    # Placeholder for future implementation
    return jsonify({"message": "Update user not implemented"}), 501

def delete_user_controller(user_id):
    # Placeholder for future implementation
    return jsonify({"message": "Delete user not implemented"}), 501
    
# --- Borrow Controllers ---
@jwt_required()
def get_all_borrows_controller():
    borrows = Borrow.query.all()
    return jsonify([borrow.to_dict() for borrow in borrows]), 200

@jwt_required()
def get_borrow_by_id_controller(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if borrow:
        return jsonify(borrow.to_dict()), 200
    return jsonify({"message": f"Borrow with ID {borrow_id} not found"}), 404

@jwt_required()
def create_borrow_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    try:
        borrow_data = BorrowCreate(**data)
    except Exception as e:
        return jsonify({"message": f"Invalid borrow data: {e.errors() if hasattr(e, 'errors') else str(e)}"}), 400
    
    book = Book.query.get(borrow_data.book_id)
    if not book:
        return jsonify({"message": f"Book with ID {borrow_data.book_id} not found"}), 404
    if not book.isAvailable:
        return jsonify({"message": f"Book '{book.title}' is currently not available"}), 400
    
    user = User.query.get(borrow_data.user_id)
    if not user:
        return jsonify({"message": f"User with ID {borrow_data.user_id} not found"}), 404
    
    if borrow_data.loan_date and borrow_data.due_date <= borrow_data.loan_date:
        return jsonify({"message": "Due date must be after loan date"}), 400

    try:
        new_borrow = Borrow(
            book_id=borrow_data.book_id,
            user_id=borrow_data.user_id,
            loan_date=borrow_data.loan_date,
            due_date=borrow_data.due_date
        )
        db.session.add(new_borrow)
        book.isAvailable = False
        db.session.commit()
        return jsonify({"message": "Borrow created successfully", "borrow": new_borrow.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while creating borrow"}), 500

@jwt_required()
def return_book_controller(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if not borrow:
        return jsonify({"message": f"Borrow with ID {borrow_id} not found"}), 404
    if borrow.return_date:
        return jsonify({"message": "Book already returned for this borrow"}), 400

    try:
        borrow_data = BorrowReturn(**request.get_json() or {})
        borrow.return_date = borrow_data.return_date
        borrow.status = 'RETURNED'
        if borrow.book:
            borrow.book.isAvailable = True
        db.session.commit()
        return jsonify({"message": "Book returned successfully", "borrow": borrow.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while returning book"}), 500

@role_required('Admin')
def delete_borrow_controller(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if not borrow:
        return jsonify({"message": f"Borrow with ID {borrow_id} not found"}), 404
    
    try:
        if not borrow.return_date and borrow.book:
            borrow.book.isAvailable = True
        
        db.session.delete(borrow)
        db.session.commit()
        return jsonify({"message": "Borrow record deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Internal server error while deleting borrow"}), 500