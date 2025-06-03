from flask import Blueprint, jsonify, request, abort
from app import db # Mengimpor objek db SQLAlchemy Anda
from app.models import Book, Category # Mengimpor model Book dan Category Anda

bp = Blueprint('routes', __name__)

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