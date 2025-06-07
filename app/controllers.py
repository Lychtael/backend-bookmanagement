# app/controllers.py

from app.models import db, Book, Category, Member, Loan # Pastikan db diimpor dari app.models
from flask import jsonify, request, abort # Import abort untuk respons HTTP yang lebih baik
from datetime import date
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Impor Pydantic Models Anda (jika Anda akan menggunakannya untuk validasi)
# from app.models import BookCreate, BookUpdate, CategoryCreate, MemberCreate, MemberUpdate, LoanCreate, LoanReturn

# --- Authentication Controllers ---
def register_member_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    # Contoh penggunaan Pydantic untuk validasi input registrasi
    # try:
    #     member_data = MemberCreate(**data)
    # except ValueError as e:
    #     return jsonify({"message": f"Invalid registration data: {e.errors()}"}), 400

    # Menggunakan validasi manual jika tidak memakai Pydantic di sini
    required_fields = ['name', 'email', 'password']
    if not all(k in data for k in required_fields):
        return jsonify({"message": f"Missing required fields: {', '.join(f for f in required_fields if f not in data)}"}), 400

    if Member.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Member with this email already exists"}), 409

    try:
        new_member = Member(name=data['name'], email=data['email'])
        new_member.set_password(data['password'])
        db.session.add(new_member)
        db.session.commit()
        return jsonify({"message": "Member registered successfully", "member": new_member.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        return jsonify({"message": "Internal server error during registration"}), 500


def login_member_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ['email', 'password']
    if not all(k in data for k in required_fields):
        return jsonify({"message": f"Missing required fields: {', '.join(f for f in required_fields if f not in data)}"}), 400

    member = Member.query.filter_by(email=data['email']).first()
    if not member or not member.check_password(data['password']):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(member.id)) # Identitas adalah string ID member
    return jsonify(access_token=access_token, member_id=member.id), 200 # Tambahkan member_id untuk frontend


# --- Book Controllers ---
def get_all_books_controller():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

def get_book_by_id_controller(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"message": f"Book with ID {book_id} not found"}), 404

@jwt_required()
def create_book_controller():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    # Contoh penggunaan Pydantic untuk validasi input buku
    # try:
    #     book_data = BookCreate(**data)
    # except ValueError as e:
    #     return jsonify({"message": f"Invalid book data: {e.errors()}"}), 400

    # Menggunakan validasi manual
    required_fields = ['title', 'author']
    if not all(k in data for k in required_fields):
        return jsonify({"message": f"Missing required fields: {', '.join(f for f in required_fields if f not in data)}"}), 400

    # Opsional: Validasi category_id jika disediakan
    category_id = data.get('category_id')
    if category_id:
        if not Category.query.get(category_id):
            return jsonify({"message": f"Category with ID {category_id} not found"}), 400

    try:
        new_book = Book(
            title=data['title'],
            author=data['author'],
            year=data.get('year'),
            category_id=category_id,
            status=data.get('status', 'available')
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book created successfully", "book": new_book.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating book: {e}")
        return jsonify({"message": "Internal server error while creating book"}), 500


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
        category_id = data['category_id']
        if category_id is not None and not Category.query.get(category_id):
            return jsonify({"message": f"Category with ID {category_id} not found"}), 400
        book.category_id = category_id
    if 'status' in data:
        if data['status'] in ['available', 'borrowed']:
            book.status = data['status']
        else:
            return jsonify({"message": "Invalid status value. Must be 'available' or 'borrowed'"}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Book updated successfully", "book": book.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating book: {e}")
        return jsonify({"message": "Internal server error while updating book"}), 500


@jwt_required()
def delete_book_controller(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": f"Book with ID {book_id} not found"}), 404

    if Loan.query.filter_by(book_id=book_id, return_date=None).first():
        return jsonify({"message": "Cannot delete book: it is currently borrowed"}), 400

    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting book: {e}")
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

@jwt_required()
def create_category_controller():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"message": "Category name is required"}), 400
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({"message": "Category with this name already exists"}), 409

    try:
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": "Category created successfully", "category": new_category.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating category: {e}")
        return jsonify({"message": "Internal server error while creating category"}), 500


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
    try:
        db.session.commit()
        return jsonify({"message": "Category updated successfully", "category": category.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating category: {e}")
        return jsonify({"message": "Internal server error while updating category"}), 500


@jwt_required()
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
        print(f"Error deleting category: {e}")
        return jsonify({"message": "Internal server error while deleting category"}), 500


# --- Member Controllers ---
def get_all_members_controller():
    members = Member.query.all()
    # Jangan kembalikan password_hash
    return jsonify([member.to_dict() for member in members]), 200

def get_member_by_id_controller(member_id):
    member = Member.query.get(member_id)
    if member:
        return jsonify(member.to_dict()), 200
    return jsonify({"message": f"Member with ID {member_id} not found"}), 404

@jwt_required()
def update_member_controller(member_id):
    # current_user_id dari JWT adalah string, member_id dari URL adalah int. Konversi!
    current_user_id = int(get_jwt_identity())
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
    if 'password' in data:
        member.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify({"message": "Member updated successfully", "member": member.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating member: {e}")
        return jsonify({"message": "Internal server error while updating member"}), 500


@jwt_required()
def delete_member_controller(member_id):
    current_user_id = int(get_jwt_identity())
    # Hanya izinkan admin atau pengguna itu sendiri untuk menghapus
    # Jika hanya pengguna sendiri, cek `current_user_id != member_id`
    # Untuk admin, Anda perlu sistem role, yang tidak ada di sini.
    if current_user_id != member_id:
        return jsonify({"message": "You are not authorized to delete this member"}), 403


    member = Member.query.get(member_id)
    if not member:
        return jsonify({"message": f"Member with ID {member_id} not found"}), 404
    if Loan.query.filter_by(member_id=member_id, return_date=None).first():
        return jsonify({"message": "Cannot delete member: they have active loans"}), 400

    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting member: {e}")
        return jsonify({"message": "Internal server error while deleting member"}), 500


# --- Loan Controllers ---
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
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ['book_id', 'member_id'] # loan_date bisa diatur otomatis
    if not all(k in data for k in required_fields):
        return jsonify({"message": f"Missing required fields: {', '.join(f for f in required_fields if f not in data)}"}), 400

    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({"message": f"Book with ID {data['book_id']} not found"}), 404
    if book.status == 'borrowed':
        return jsonify({"message": f"Book '{book.title}' is currently borrowed"}), 400

    member = Member.query.get(data['member_id'])
    if not member:
        return jsonify({"message": f"Member with ID {data['member_id']} not found"}), 404

    loan_date_str = data.get('loan_date')
    if loan_date_str:
        try:
            loan_date = date.fromisoformat(loan_date_str)
        except ValueError:
            return jsonify({"message": "Invalid loan_date format. Use YYYY-MM-DD"}), 400
    else:
        loan_date = date.today() # Default to today if not provided

    try:
        new_loan = Loan(
            book_id=data['book_id'],
            member_id=data['member_id'],
            loan_date=loan_date
        )
        db.session.add(new_loan)
        book.status = 'borrowed'
        db.session.commit()
        return jsonify({"message": "Loan created successfully", "loan": new_loan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating loan: {e}")
        return jsonify({"message": "Internal server error while creating loan"}), 500


@jwt_required()
def return_book_controller(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"message": f"Loan with ID {loan_id} not found"}), 404
    if loan.return_date:
        return jsonify({"message": "Book already returned for this loan"}), 400

    try:
        loan.return_date = date.today()
        # Pastikan book terkait ada sebelum mengubah statusnya
        if loan.book:
            loan.book.status = 'available'
        db.session.commit()
        return jsonify({"message": "Book returned successfully", "loan": loan.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error returning book: {e}")
        return jsonify({"message": "Internal server error while returning book"}), 500


@jwt_required()
def delete_loan_controller(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"message": f"Loan with ID {loan_id} not found"}), 404

    try:
        # Jika buku belum dikembalikan, kembalikan status buku ke 'available'
        if loan.book and not loan.return_date:
            loan.book.status = 'available'
        db.session.delete(loan)
        db.session.commit()
        return jsonify({"message": "Loan deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting loan: {e}")
        return jsonify({"message": "Internal server error while deleting loan"}), 500