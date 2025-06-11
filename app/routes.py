# app/routes.py (Corrected and Cleaned)

from flask import Blueprint
from app.controllers import (
    # Authentication Controllers
    register_user_controller,
    login_user_controller,
    # Book Controllers
    get_all_books_controller, 
    get_book_by_id_controller,
    create_book_controller, 
    update_book_controller, 
    delete_book_controller,
    # Category Controllers
    get_all_categories_controller, 
    get_category_by_id_controller,
    create_category_controller, 
    update_category_controller, 
    delete_category_controller,
    # User Controllers
    get_all_users_controller, 
    get_user_by_id_controller,
    update_user_controller, 
    delete_user_controller,
    # Borrow Controllers
    get_all_borrows_controller, 
    get_borrow_by_id_controller,
    create_borrow_controller, 
    return_book_controller, 
    delete_borrow_controller
)
from flask_jwt_extended import jwt_required

api_bp = Blueprint('api', __name__)

# --- Authentication Routes ---
@api_bp.route('/register', methods=['POST'])
def register_user_route():
    return register_user_controller()

@api_bp.route('/login', methods=['POST'])
def login_user_route():
    return login_user_controller()

# --- Book Routes ---
@api_bp.route('/books', methods=['GET'])
def get_books():
    return get_all_books_controller()

@api_bp.route('/books/<string:book_id>', methods=['GET'])
def get_single_book(book_id):
    return get_book_by_id_controller(book_id)

@api_bp.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    return create_book_controller()

@api_bp.route('/books/<string:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    return update_book_controller(book_id)

@api_bp.route('/books/<string:book_id>', methods=['DELETE'])
@jwt_required()
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
@jwt_required()
def create_category():
    return create_category_controller()

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    return update_category_controller(category_id)

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    return delete_category_controller(category_id)

# --- User Routes ---
@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    return get_all_users_controller()

@api_bp.route('/users/<string:user_id>', methods=['GET'])
@jwt_required()
def get_single_user(user_id):
    return get_user_by_id_controller(user_id)

@api_bp.route('/users/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    return update_user_controller(user_id)

@api_bp.route('/users/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    return delete_user_controller(user_id)

# --- Borrow Routes ---
@api_bp.route('/borrows', methods=['GET'])
@jwt_required()
def get_borrows():
    return get_all_borrows_controller()

@api_bp.route('/borrows/<string:borrow_id>', methods=['GET'])
@jwt_required()
def get_single_borrow(borrow_id):
    return get_borrow_by_id_controller(borrow_id)

@api_bp.route('/borrows', methods=['POST'])
@jwt_required()
def create_borrow():
    return create_borrow_controller()

@api_bp.route('/borrows/<string:borrow_id>/return', methods=['PUT'])
@jwt_required()
def return_book(borrow_id):
    return return_book_controller(borrow_id)

@api_bp.route('/borrows/<string:borrow_id>', methods=['DELETE'])
@jwt_required()
def delete_borrow(borrow_id):
    return delete_borrow_controller(borrow_id)