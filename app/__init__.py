"""Flask application factory for the Library Management System."""
from datetime import date

from flask import Flask

from config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Import models so SQLAlchemy registers them with `db.metadata`
    from app import models  # noqa: F401

    # Register routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Create tables and seed initial data on first run
    with app.app_context():
        db.create_all()
        _seed_if_empty()

    return app


def _seed_if_empty():
    """Populate the database with sample data the first time the app runs.

    Mirrors the INSERT statements in schema.sql so the data layer in Python
    matches the SQL deliverable for Part I of the project.
    """
    from app.models import Author, Genre, Book, Member, Loan

    # If any authors already exist, skip seeding
    if Author.query.first() is not None:
        return

    # --- Authors ---
    authors_data = [
        "F. Scott Fitzgerald", "George Orwell", "Stephen Hawking",
        "J.R.R. Tolkien", "Isaac Asimov", "Yuval Noah Harari",
        "Frank Herbert", "James Clear", "Agatha Christie", "Stephen King",
    ]
    for name in authors_data:
        db.session.add(Author(AuthorName=name))

    # --- Genres ---
    genres_data = ["Fiction", "Dystopian", "Science", "Fantasy", "Sci-Fi",
                   "History", "Self-Help", "Mystery", "Horror"]
    for name in genres_data:
        db.session.add(Genre(GenreName=name))

    db.session.commit()

    # --- Books ---
    books_data = [
        ("The Great Gatsby",              1, 1, 1925),
        ("1984",                          2, 2, 1949),
        ("A Brief History of Time",       3, 3, 1988),
        ("The Hobbit",                    4, 4, 1937),
        ("Foundation",                    5, 5, 1951),
        ("Sapiens",                       6, 6, 2011),
        ("Dune",                          7, 5, 1965),
        ("Atomic Habits",                 8, 7, 2018),
        ("Murder on the Orient Express", 9, 8, 1934),
        ("The Shining",                  10, 9, 1977),
    ]
    for title, author_id, genre_id, year in books_data:
        db.session.add(Book(
            Title=title, AuthorID=author_id,
            GenreID=genre_id, PublishedYear=year))

    # --- Members ---
    members_data = [
        ("Alice",   "Johnson", date(2024, 1, 15), "alice.johnson@example.com"),
        ("Bob",     "Smith",   date(2024, 2, 20), "b.smith78@provider.net"),
        ("Charlie", "Davis",   date(2024, 3, 10), "charlie.davis.edu@university.edu"),
        ("Diana",   "Prince",  date(2024, 5, 5),  "diana.prince.workspace@company.com"),
    ]
    for fn, ln, jd, em in members_data:
        db.session.add(Member(FirstName=fn, LastName=ln, JoinDate=jd, Email=em))

    db.session.commit()

    # --- Loans ---
    loans_data = [
        (1, 1, date(2026, 1, 1),  date(2026, 1, 10)),
        (2, 2, date(2026, 1, 5),  date(2026, 1, 20)),
        (1, 1, date(2026, 2, 1),  None),
        (3, 3, date(2026, 2, 2),  date(2026, 2, 10)),
        (4, 4, date(2026, 1, 10), date(2026, 1, 15)),
        (7, 1, date(2026, 2, 5),  None),
        (9, 2, date(2026, 2, 8),  None),
    ]
    for book_id, member_id, ld, rd in loans_data:
        db.session.add(Loan(
            BookID=book_id, MemberID=member_id,
            LoanDate=ld, ReturnDate=rd))

    db.session.commit()