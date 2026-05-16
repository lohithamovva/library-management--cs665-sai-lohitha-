"""Flask routes for the Library Management System.

Stage 1: just the home page showing all books.
Later stages will add CRUD pages for Books, Members, Loans, and a Dashboard.
"""
from flask import Blueprint, render_template

from app.extensions import db
from app.models import Book

# A Blueprint groups related routes together. The `main` blueprint
# is registered in app/__init__.py.
bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page — shows a list of all books in the library."""
    books = Book.query.order_by(Book.Title.asc()).all()
    return render_template("index.html", books=books)