from flask import Blueprint, jsonify, request
from app import db
from app.models import Book

bp = Blueprint('routes', __name__)

@bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'author': b.author, 'year': b.year, 'status': b.status
    } for b in books])
