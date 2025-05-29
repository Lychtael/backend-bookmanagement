from flask import Flask, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # --- PENTING: Impor model Anda di sini ---
    # Ini memastikan Flask-Migrate 'melihat' semua model Anda
    from app import models # Mengimpor modul models
    # Atau, jika Anda ingin mengimpor kelas spesifik:
    # from app.models import Category, Book, Member, Loan
    # ----------------------------------------

    # Blueprint `main` akan diimpor dari app.routes.py, BUKAN didefinisikan di sini
    # from .routes import main as main_blueprint # Asumsi Anda punya blueprint bernama `main` di app/routes.py
    # app.register_blueprint(main_blueprint)

    # --- Placeholder untuk rute yang sudah ada, ini harusnya ada di app/routes.py ---
    # Jika `routes.py` Anda adalah Blueprint, pastikan Anda mendaftarkannya.
    # Untuk contoh ini, saya akan tetap sertakan bagian `main` Blueprint ini untuk kesederhanaan,
    # tetapi praktik terbaik adalah mendefinisikan ini di `app/routes.py` dan mengimpornya.

    main = Blueprint('main', __name__)
    @main.route('/')
    def index():
        # Menggunakan <br> tag HTML untuk baris baru
        return "Project berjalan dan venv siap<br>" \
            "migration selesai dan db selesai"

    @main.route('/books')
    def books():
        # Contoh query menggunakan model Book dari SQLAlchemy
        from app.models import Book
        try:
            all_books = db.session.execute(db.select(Book)).scalars().all() # Cara baru Flask-SQLAlchemy 3.x
            # all_books = Book.query.all() # Cara lama, tapi masih kompatibel
            book_data = []
            for book in all_books:
                book_data.append({
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "year": book.year,
                    "category_id": book.category_id,
                    "status": book.status
                })
            return jsonify(book_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    app.register_blueprint(main) # Daftarkan blueprint 'main'

    return app