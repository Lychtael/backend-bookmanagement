
from flask import Blueprint, jsonify, request, abort
from app import db # Mengimpor objek db SQLAlchemy Anda
from app.models import Book, Category # Mengimpor model Book dan Category Anda


from flask import Blueprint
from app.controllers import (
    # Authentication Controllers
    register_member_controller, # <--- ENSURE THIS IS CORRECT
    login_member_controller,
    # Book Controllers
    get_all_books_controller, get_book_by_id_controller,
    create_book_controller, update_book_controller, delete_book_controller,
    # Category Controllers
    get_all_categories_controller, get_category_by_id_controller,
    create_category_controller, update_category_controller, delete_category_controller,
    # Member Controllers
    get_all_members_controller, get_member_by_id_controller,
    update_member_controller, delete_member_controller,
    # Loan Controllers
    get_all_loans_controller, get_loan_by_id_controller,
    create_loan_controller, return_book_controller, delete_loan_controller
)
from flask_jwt_extended import jwt_required


# --- CRUD untuk Buku (Book) ---

@bp.route('/books', methods=['GET'])
def get_books():
    """
    Mengambil semua buku.
    """
    books = Book.query.all()
    # Serialisasi manual objek Book ke dictionary
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'author': b.author,
        'year': b.year,
        'category_id': b.category_id, # Sertakan category_id
        'status': b.status
    } for b in books])

@bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Mengambil satu buku berdasarkan ID.
    """
    book = Book.query.get(book_id) # Menggunakan .get() untuk primary key
    if book is None:
        abort(404, description="Book not found") # Mengembalikan 404 Not Found
    
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'category_id': book.category_id,
        'status': book.status
    })

@bp.route('/books', methods=['POST'])
def add_book():
    """
    Menambahkan buku baru.
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()

    # Validasi input sederhana (Anda bisa membuatnya lebih kuat)
    if not data or 'title' not in data:
        abort(400, description="Title is required")

    # Opsional: Periksa apakah category_id valid jika disediakan
    category_id = data.get('category_id')
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            abort(400, description=f"Category with ID {category_id} not found.")

    new_book = Book(
        title=data['title'],
        author=data.get('author'), # Gunakan .get() agar tidak error jika field tidak ada
        year=data.get('year'),
        category_id=category_id,
        status=data.get('status', 'available') # Default status
    )

    try:
        db.session.add(new_book)
        db.session.commit() # Simpan ke database
        return jsonify({
            'id': new_book.id,
            'title': new_book.title,
            'author': new_book.author,
            'year': new_book.year,
            'category_id': new_book.category_id,
            'status': new_book.status
        }), 201 # Kode status 201 Created
    except Exception as e:
        db.session.rollback() # Rollback jika ada error DB
        print(f"Error adding book: {e}") # Log error ke console server
        abort(500, description="Internal server error while adding book.")


@bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book_route(book_id):
    """
    Memperbarui buku yang sudah ada.
    """
    book = Book.query.get(book_id)
    if book is None:
        abort(404, description="Book not found")

    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()

    # Perbarui field jika ada dalam data yang diterima
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    if 'status' in data:
        book.status = data['status']
    
    # Perbarui category_id jika ada
    if 'category_id' in data:
        category_id = data.get('category_id')
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                abort(400, description=f"Category with ID {category_id} not found.")
        book.category_id = category_id # Bisa jadi None jika category_id dihilangkan

    try:
        db.session.commit() # Simpan perubahan
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'category_id': book.category_id,
            'status': book.status
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating book {book_id}: {e}")
        abort(500, description="Internal server error while updating book.")

@bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book_route(book_id):
    """
    Menghapus buku.
    """
    book = Book.query.get(book_id)
    if book is None:
        abort(404, description="Book not found")

    try:
        db.session.delete(book)
        db.session.commit() # Simpan perubahan
        return '', 204 # Kode status 204 No Content untuk penghapusan berhasil (tanpa body)
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting book {book_id}: {e}")
        abort(500, description="Internal server error while deleting book.")

# --- CRUD Sederhana untuk Kategori (Category) ---
# Anda bisa menambahkan lebih banyak logika CRUD di sini sesuai kebutuhan

@bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Mengambil semua kategori.
    """
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name
    } for c in categories])

@bp.route('/categories', methods=['POST'])
def add_category():
    """
    Menambahkan kategori baru.
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Category name is required.")
    
    new_category = Category(name=data['name'])
    
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            'id': new_category.id,
            'name': new_category.name
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding category: {e}")
        abort(500, description="Internal server error while adding category.")
=======
api_bp = Blueprint('api', __name__)

# --- Authentication Routes ---
@api_bp.route('/register', methods=['POST'])
def register_member():
    return register_member_controller()

@api_bp.route('/login', methods=['POST'])
def login_member():
    return login_member_controller()

# --- Book Routes ---
@api_bp.route('/books', methods=['GET'])
def get_books():
    return get_all_books_controller()

@api_bp.route('/books/<int:book_id>', methods=['GET'])
def get_single_book(book_id):
    return get_book_by_id_controller(book_id)

@api_bp.route('/books', methods=['POST'])
@jwt_required() # Protect this route
def create_book():
    return create_book_controller()

@api_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required() # Protect this route
def update_book(book_id):
    return update_book_controller(book_id)

@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required() # Protect this route
def delete_book(book_id):
    return delete_book_controller(book_id)

# --- Category Routes ---
@api_bp.route('/categories', methods=['GET'])
def get_categories():
    return get_all_categories_controller()

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_single_category(category_id):
    return get_category_by_id_controller(category_id)

@api_bp.route('/categories', methods=['POST'])
@jwt_required() # Protect this route
def create_category():
    return create_category_controller()

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required() # Protect this route
def update_category(category_id):
    return update_category_controller(category_id)

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required() # Protect this route
def delete_category(category_id):
    return delete_category_controller(category_id)

# --- Member Routes ---
@api_bp.route('/members', methods=['GET'])
def get_members():
    return get_all_members_controller()

@api_bp.route('/members/<int:member_id>', methods=['GET'])
def get_single_member(member_id):
    return get_member_by_id_controller(member_id)

# The old create_member route is replaced by /register
# @api_bp.route('/members', methods=['POST'])
# def create_member():
#     return create_member_controller() # No longer needed, handled by register

@api_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required() # Protect this route
def update_member(member_id):
    return update_member_controller(member_id)

@api_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required() # Protect this route
def delete_member(member_id):
    return delete_member_controller(member_id)

# --- Loan Routes ---
@api_bp.route('/loans', methods=['GET'])
@jwt_required() # Protect this route
def get_loans():
    return get_all_loans_controller()

@api_bp.route('/loans/<int:loan_id>', methods=['GET'])
@jwt_required() # Protect this route
def get_single_loan(loan_id):
    return get_loan_by_id_controller(loan_id)

@api_bp.route('/loans', methods=['POST'])
@jwt_required() # Protect this route
def create_loan():
    return create_loan_controller()

@api_bp.route('/loans/<int:loan_id>/return', methods=['PUT'])
@jwt_required() # Protect this route
def return_book(loan_id):
    return return_book_controller(loan_id)

@api_bp.route('/loans/<int:loan_id>', methods=['DELETE'])
@jwt_required() # Protect this route
def delete_loan(loan_id):
    return delete_loan_controller(loan_id)

