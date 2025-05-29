from flask import Blueprint, jsonify
from . import mysql

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello from Flask + MySQL!"

@main.route('/books')
def books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    result = cur.fetchall()
    return jsonify(result)
