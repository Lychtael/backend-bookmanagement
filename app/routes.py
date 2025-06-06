
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