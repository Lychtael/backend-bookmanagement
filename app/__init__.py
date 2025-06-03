# app/__init__.py

from flask import Flask
from config import Config
from app.models import db, Book, Category, Member, Loan
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Remove the initial data seeding from here
    # with app.app_context():
    #     try:
    #         if not Category.query.first():
    #             # ... (all your initial data logic) ...
    #     except Exception as e:
    #         print(f"Error adding initial data: {e}")
    #         db.session.rollback()

    return app

# --- NEW: Create a separate function/script for seeding data ---
# You can put this in a new file, e.g., 'seed.py' or as a Flask CLI command.
# For simplicity, I'll show it as a function you'd call manually after migrations.

def seed_initial_data(app):
    with app.app_context():
        try:
            print("Checking and adding initial data...")
            if not Category.query.first():
                print("Adding initial category data...")
                initial_categories = [
                    Category(name="Fiction"),
                    Category(name="Science"),
                    Category(name="History")
                ]
                db.session.add_all(initial_categories)
                db.session.commit()
                print("Initial category data added.")
                fiction_cat = Category.query.filter_by(name="Fiction").first()
                science_cat = Category.query.filter_by(name="Science").first()
            else:
                fiction_cat = Category.query.filter_by(name="Fiction").first()
                science_cat = Category.query.filter_by(name="Science").first()

            if not Book.query.first():
                print("Adding initial book data...")
                initial_books = [
                    Book(title="The Lord of the Rings", author="J.R.R. Tolkien", year=1954, category_id=fiction_cat.id if fiction_cat else None, status='available'),
                    Book(title="Cosmos", author="Carl Sagan", year=1980, category_id=science_cat.id if science_cat else None, status='available')
                ]
                db.session.add_all(initial_books)
                db.session.commit()
                print("Initial book data added.")

            if not Member.query.first():
                print("Adding initial member data...")
                member1 = Member(name="Alice Smith", email="alice@example.com")
                member1.set_password("password123")
                member2 = Member(name="Bob Johnson", email="bob@example.com")
                member2.set_password("securepass")

                initial_members = [member1, member2]
                db.session.add_all(initial_members)
                db.session.commit()
                print("Initial member data added.")

            if not Loan.query.first() and Book.query.first() and Member.query.first():
                print("Adding initial loan data...")
                first_book = Book.query.first()
                first_member = Member.query.first()
                if first_book and first_member:
                    from datetime import date
                    initial_loan = Loan(
                        book_id=first_book.id,
                        member_id=first_member.id,
                        loan_date=date.today()
                    )
                    db.session.add(initial_loan)
                    first_book.status = 'borrowed'
                    db.session.commit()
                    print("Initial loan data added.")
            print("Initial data seeding complete (if tables were empty).")

        except Exception as e:
            print(f"Error during initial data seeding: {e}")
            db.session.rollback()