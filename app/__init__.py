# app/__init__.py (Tidak ada perubahan yang diperlukan)

from flask import Flask
from config import Config

# Import all your new models
from app.models import db, Book, Category, User, Borrow, Role, Session


from app.models import db, Book, Category, Member, Loan # Pastikan ini mengimpor semua model Anda

from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    from app.routes import api_bp # Ini akan mengimpor blueprint yang benar
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

# --- NEW: Create a separate function/script for seeding data ---

def seed_initial_data(app):
    with app.app_context():
        try:
            print("Checking and adding initial data...")

            # 1. Seed Roles
            if not Role.query.first():
                print("Adding initial role data...")
                admin_role = Role(id=1, name="Admin")
                user_role = Role(id=2, name="User")
                db.session.add_all([admin_role, user_role])
                db.session.commit()
                print("Initial role data added.")
            else:
                admin_role = Role.query.filter_by(name="Admin").first()
                user_role = Role.query.filter_by(name="User").first()

            # 2. Seed Categories
            if not Category.query.first():
                print("Adding initial category data...")
                initial_categories = [
                    Category(id=1, name="Self-Improvement"),
                    Category(id=2, name="Science"),
                    Category(id=3, name="Classic Fiction"),
                    Category(id=4, name="Dystopian")
                ]
                db.session.add_all(initial_categories)
                db.session.commit()
                print("Initial category data added.")
                self_improvement_cat = Category.query.filter_by(name="Self-Improvement").first()
                science_cat = Category.query.filter_by(name="Science").first()
                classic_fiction_cat = Category.query.filter_by(name="Classic Fiction").first()
                dystopian_cat = Category.query.filter_by(name="Dystopian").first()
            else:
                self_improvement_cat = Category.query.filter_by(name="Self-Improvement").first()
                science_cat = Category.query.filter_by(name="Science").first()
                classic_fiction_cat = Category.query.filter_by(name="Classic Fiction").first()
                dystopian_cat = Category.query.filter_by(name="Dystopian").first()


            # 3. Seed Users
            if not User.query.first():
                print("Adding initial user data...")
                from werkzeug.security import generate_password_hash
                user1 = User(id='admin01', name="Alice Johnson", email="alice@example.com", role_id=admin_role.id)
                user1.set_password("password123")
                user2 = User(id='user01', name="Bob Williams", email="bob@example.com", role_id=user_role.id)
                user2.set_password("securepass")
                user3 = User(id='user02', name="Charlie Brown", email="charlie@example.com", role_id=user_role.id)
                user3.set_password("securepass")
                user4 = User(id='user03', name="Diana Prince", email="diana@example.com", role_id=user_role.id)
                user4.set_password("securepass")
                user5 = User(id='user04', name="John Doe", email="john.doe@example.com", role_id=user_role.id)
                user5.set_password("securepass")

                initial_users = [user1, user2, user3, user4, user5]
                db.session.add_all(initial_users)
                db.session.commit()
                print("Initial user data added.")
            else:
                user_john = User.query.filter_by(email="john.doe@example.com").first()
                user_charlie = User.query.filter_by(email="charlie@example.com").first()


            # 4. Seed Books
            if not Book.query.first():
                print("Adding initial book data...")
                initial_books = [
                    Book(id='1', title="Atomic Habits", author="James Clear", year=2018,
                         description='An easy and proven way to build good habits and break bad ones.',
                         imageUrl='https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1655988385l/40121378.jpg',
                         isAvailable=True, category_id=self_improvement_cat.id if self_improvement_cat else None),
                    Book(id='2', title="Sapiens: A Brief History of Humankind", author="Yuval Noah Harari", year=2011,
                         description='A groundbreaking narrative of humanity\'s creation and evolution.',
                         imageUrl='https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1420585954l/23692271.jpg',
                         isAvailable=True, category_id=science_cat.id if science_cat else None),
                    Book(id='3', title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925,
                         description='The story of the fabulously wealthy Jay Gatsby and his new love for the beautiful Daisy Buchanan.',
                         imageUrl='https://upload.wikimedia.org/wikipedia/commons/7/7a/The_Great_Gatsby_Cover_1925_Retouched.jpg',
                         isAvailable=False, category_id=classic_fiction_cat.id if classic_fiction_cat else None),
                    Book(id='4', title="To Kill a Mockingbird", author="Harper Lee", year=1960,
                         description='A novel about the serious issues of rape and racial inequality.',
                         imageUrl='https://upload.wikimedia.org/wikipedia/commons/4/4f/To_Kill_a_Mockingbird_%28first_edition_cover%29.jpg',
                         isAvailable=False, category_id=classic_fiction_cat.id if classic_fiction_cat else None),
                    Book(id='5', title="1984", author="George Orwell", year=1949,
                         description='A dystopian social science fiction novel and cautionary tale.',
                         imageUrl='https://upload.wikimedia.org/wikipedia/commons/c/c3/1984first.jpg',
                         isAvailable=False, category_id=dystopian_cat.id if dystopian_cat else None)
                ]
                db.session.add_all(initial_books)
                db.session.commit()
                print("Initial book data added.")
            else:
                book3 = Book.query.get('3')
                book4 = Book.query.get('4')
                book5 = Book.query.get('5')


            # 5. Seed Borrows
            if not Borrow.query.first():
                print("Adding initial borrow data...")
                from datetime import date, timedelta
                
                # Borrow 1: Overdue
                if book3 and user_john:
                    borrow1_date = date(2025, 6, 1)
                    borrow1_due_date = date(2025, 6, 8)
                    initial_borrow1 = Borrow(
                        id='borrow_001',
                        book_id=book3.id,
                        user_id=user_john.id,
                        loan_date=borrow1_date,
                        due_date=borrow1_due_date,
                        status='OVERDUE' if date.today() > borrow1_due_date else 'BORROWED'
                    )
                    db.session.add(initial_borrow1)
                    book3.isAvailable = False

                # Borrow 2: Borrowed
                if book4 and user_john:
                    borrow2_date = date(2025, 6, 5)
                    borrow2_due_date = date(2025, 6, 12)
                    initial_borrow2 = Borrow(
                        id='borrow_002',
                        book_id=book4.id,
                        user_id=user_john.id,
                        loan_date=borrow2_date,
                        due_date=borrow2_due_date,
                        status='BORROWED'
                    )
                    db.session.add(initial_borrow2)
                    book4.isAvailable = False

                # Borrow 3: Borrowed
                if book5 and user_charlie:
                    borrow3_date = date(2025, 6, 7)
                    borrow3_due_date = date(2025, 6, 14)
                    initial_borrow3 = Borrow(
                        id='borrow_003',
                        book_id=book5.id,
                        user_id=user_charlie.id,
                        loan_date=borrow3_date,
                        due_date=borrow3_due_date,
                        status='BORROWED'
                    )
                    db.session.add(initial_borrow3)
                    book5.isAvailable = False

                db.session.commit()
                print("Initial borrow data added.")

            print("Initial data seeding complete (if tables were empty).")

        except Exception as e:
            print(f"Error during initial data seeding: {e}")
            db.session.rollback()