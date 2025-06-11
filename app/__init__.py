# app/__init__.py (Corrected)

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Define the database object here, to be imported by other parts of the app
db = SQLAlchemy()

def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Import and register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

def seed_initial_data(app):
    """Seeds the database with initial data."""
    with app.app_context():
        # Import models here to avoid circular import issues
        from app.models import Role, Category, User, Book, Borrow
        from werkzeug.security import generate_password_hash
        from datetime import date

        try:
            print("Checking and adding initial data...")

            # --- Step 1: Seed Roles ---
            if not Role.query.first():
                print("Adding initial role data...")
                db.session.add_all([Role(id=1, name="Admin"), Role(id=2, name="User")])
                db.session.commit()
                print("Initial role data added.")

            # --- Step 2: Seed Categories ---
            if not Category.query.first():
                print("Adding initial category data...")
                db.session.add_all([
                    Category(id=1, name="Self-Improvement"), Category(id=2, name="Science"),
                    Category(id=3, name="Classic Fiction"), Category(id=4, name="Dystopian")
                ])
                db.session.commit()
                print("Initial category data added.")

            # --- Step 3: Seed Users ---
            if not User.query.first():
                print("Adding initial user data...")
                admin_role = Role.query.get(1)
                user_role = Role.query.get(2)
                if admin_role and user_role:
                    db.session.add_all([
                        User(id='admin01', name="Alice Johnson", email="alice@example.com", role_id=admin_role.id, password_hash=generate_password_hash("password123")),
                        User(id='user01', name="Bob Williams", email="bob@example.com", role_id=user_role.id, password_hash=generate_password_hash("securepass")),
                        User(id='user02', name="Charlie Brown", email="charlie@example.com", role_id=user_role.id, password_hash=generate_password_hash("securepass")),
                        User(id='user03', name="Diana Prince", email="diana@example.com", role_id=user_role.id, password_hash=generate_password_hash("securepass")),
                        User(id='user04', name="John Doe", email="john.doe@example.com", role_id=user_role.id, password_hash=generate_password_hash("securepass"))
                    ])
                    db.session.commit()
                    print("Initial user data added.")

            # --- Step 4: Seed Books ---
            if not Book.query.first():
                print("Adding initial book data...")
                cat1, cat2, cat3, cat4 = Category.query.get(1), Category.query.get(2), Category.query.get(3), Category.query.get(4)
                if all([cat1, cat2, cat3, cat4]):
                    db.session.add_all([
                        Book(id='1', title="Atomic Habits", author="James Clear", year=2018, description='An easy and proven way to build good habits and break bad ones.', imageUrl='https://example.com/image.jpg', isAvailable=True, category_id=cat1.id),
                        Book(id='2', title="Sapiens: A Brief History of Humankind", author="Yuval Noah Harari", year=2011, description='A groundbreaking narrative.', imageUrl='https://example.com/image.jpg', isAvailable=True, category_id=cat2.id),
                        Book(id='3', title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925, description='The story of the fabulously wealthy Jay Gatsby.', imageUrl='https://example.com/image.jpg', isAvailable=False, category_id=cat3.id),
                        Book(id='4', title="To Kill a Mockingbird", author="Harper Lee", year=1960, description='A novel about serious issues.', imageUrl='https://example.com/image.jpg', isAvailable=False, category_id=cat3.id),
                        Book(id='5', title="1984", author="George Orwell", year=1949, description='A dystopian social science fiction novel.', imageUrl='https://example.com/image.jpg', isAvailable=False, category_id=cat4.id)
                    ])
                    db.session.commit()
                    print("Initial book data added.")

            # --- Step 5: Seed Borrows ---
            if not Borrow.query.first():
                print("Adding initial borrow data...")
                user_john = User.query.filter_by(email="john.doe@example.com").first()
                user_charlie = User.query.filter_by(email="charlie@example.com").first()
                book3, book4, book5 = Book.query.get('3'), Book.query.get('4'), Book.query.get('5')
                if all([user_john, user_charlie, book3, book4, book5]):
                    db.session.add_all([
                        Borrow(id='borrow_001', book_id=book3.id, user_id=user_john.id, loan_date=date(2025, 6, 1), due_date=date(2025, 6, 8), status='OVERDUE' if date.today() > date(2025, 6, 8) else 'BORROWED'),
                        Borrow(id='borrow_002', book_id=book4.id, user_id=user_john.id, loan_date=date(2025, 6, 5), due_date=date(2025, 6, 12), status='BORROWED'),
                        Borrow(id='borrow_003', book_id=book5.id, user_id=user_charlie.id, loan_date=date(2025, 6, 7), due_date=date(2025, 6, 14), status='BORROWED')
                    ])
                    db.session.commit()
                    print("Initial borrow data added.")
            
            print("Initial data seeding complete (if tables were empty).")

        except Exception as e:
            print(f"Error during initial data seeding: {e}")
            db.session.rollback()