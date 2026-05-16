"""Flask routes for the Library Management System.

Stage 4: Adds the /dashboard summary page that uses SQL aggregate functions
(COUNT, SUM, AVG) over the Library data.
"""
import re
from datetime import date, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func

from app.extensions import db
from app.models import Book, Author, Genre, Member, Loan

bp = Blueprint("main", __name__)


# ===========================================================================
# BOOKS
# ===========================================================================

@bp.route("/")
def index():
    books = Book.query.order_by(Book.Title.asc()).all()
    return render_template("index.html", books=books)


@bp.route("/books/new", methods=["GET", "POST"])
def book_new():
    authors = Author.query.order_by(Author.AuthorName.asc()).all()
    genres = Genre.query.order_by(Genre.GenreName.asc()).all()

    if request.method == "POST":
        title, author_id, genre_id, year, errors = _validate_book_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("book_form.html", book=None,
                                   authors=authors, genres=genres,
                                   form_data=request.form)

        new_book = Book(Title=title, AuthorID=author_id,
                        GenreID=genre_id, PublishedYear=year)
        db.session.add(new_book)
        db.session.commit()
        flash(f"Added '{new_book.Title}' to the library.", "success")
        return redirect(url_for("main.index"))

    return render_template("book_form.html", book=None,
                           authors=authors, genres=genres, form_data={})


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    authors = Author.query.order_by(Author.AuthorName.asc()).all()
    genres = Genre.query.order_by(Genre.GenreName.asc()).all()

    if request.method == "POST":
        title, author_id, genre_id, year, errors = _validate_book_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("book_form.html", book=book,
                                   authors=authors, genres=genres,
                                   form_data=request.form)

        book.Title = title
        book.AuthorID = author_id
        book.GenreID = genre_id
        book.PublishedYear = year
        db.session.commit()
        flash(f"Updated '{book.Title}'.", "success")
        return redirect(url_for("main.index"))

    return render_template("book_form.html", book=book,
                           authors=authors, genres=genres, form_data={})


@bp.route("/books/<int:book_id>/delete", methods=["POST"])
def book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.Title
    db.session.delete(book)
    db.session.commit()
    flash(f"Deleted '{title}' from the library.", "warning")
    return redirect(url_for("main.index"))


# ===========================================================================
# MEMBERS
# ===========================================================================

@bp.route("/members")
def members_list():
    members = Member.query.order_by(
        Member.LastName.asc(), Member.FirstName.asc()
    ).all()
    return render_template("members.html", members=members)


@bp.route("/members/<int:member_id>")
def member_detail(member_id):
    member = Member.query.get_or_404(member_id)
    loans = sorted(member.loans, key=lambda l: l.LoanDate, reverse=True)
    return render_template("member_detail.html", member=member, loans=loans)


@bp.route("/members/new", methods=["GET", "POST"])
def member_new():
    if request.method == "POST":
        fn, ln, email, jd, errors = _validate_member_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("member_form.html",
                                   member=None, form_data=request.form)

        new_member = Member(FirstName=fn, LastName=ln,
                            Email=email, JoinDate=jd)
        db.session.add(new_member)
        db.session.commit()
        flash(f"Added member '{new_member.full_name}'.", "success")
        return redirect(url_for("main.members_list"))

    return render_template("member_form.html", member=None, form_data={})


@bp.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
def member_edit(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == "POST":
        fn, ln, email, jd, errors = _validate_member_form(
            request.form, existing_member_id=member_id)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("member_form.html",
                                   member=member, form_data=request.form)

        member.FirstName = fn
        member.LastName = ln
        member.Email = email
        member.JoinDate = jd
        db.session.commit()
        flash(f"Updated '{member.full_name}'.", "success")
        return redirect(url_for("main.members_list"))

    return render_template("member_form.html", member=member, form_data={})


@bp.route("/members/<int:member_id>/delete", methods=["POST"])
def member_delete(member_id):
    member = Member.query.get_or_404(member_id)
    name = member.full_name
    db.session.delete(member)
    db.session.commit()
    flash(f"Deleted member '{name}'.", "warning")
    return redirect(url_for("main.members_list"))


# ===========================================================================
# LOANS  —  CRUD + Transactional "Issue Loan"
# ===========================================================================

ACTIVE_LOAN_LIMIT = 3


@bp.route("/loans")
def loans_list():
    loans = Loan.query.order_by(Loan.LoanDate.desc()).all()
    return render_template("loans.html", loans=loans)


@bp.route("/loans/new", methods=["GET", "POST"])
def loan_new():
    """Issue a new loan — DEMONSTRATES TRANSACTION LOGIC.
    Multiple steps must succeed atomically or the whole thing rolls back."""
    books = Book.query.order_by(Book.Title.asc()).all()
    members = Member.query.order_by(
        Member.LastName.asc(), Member.FirstName.asc()
    ).all()

    if request.method == "POST":
        book_id_raw = request.form.get("book_id") or ""
        member_id_raw = request.form.get("member_id") or ""

        errors = []
        try:
            book_id = int(book_id_raw)
        except ValueError:
            errors.append("Please select a book.")
            book_id = None

        try:
            member_id = int(member_id_raw)
        except ValueError:
            errors.append("Please select a member.")
            member_id = None

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("loan_form.html",
                                   books=books, members=members,
                                   form_data=request.form)

        try:
            book = Book.query.get(book_id)
            if not book:
                raise ValueError("Selected book does not exist.")
            if not book.is_available:
                raise ValueError(
                    f"'{book.Title}' is already on loan.")

            member = Member.query.get(member_id)
            if not member:
                raise ValueError("Selected member does not exist.")

            active = [l for l in member.loans if l.ReturnDate is None]
            if len(active) >= ACTIVE_LOAN_LIMIT:
                raise ValueError(
                    f"{member.full_name} already has {ACTIVE_LOAN_LIMIT} active loans.")

            new_loan = Loan(
                BookID=book.BookID,
                MemberID=member.MemberID,
                LoanDate=date.today(),
                ReturnDate=None,
            )
            db.session.add(new_loan)
            db.session.commit()

            flash(f"Loan issued: '{book.Title}' to {member.full_name}.",
                  "success")
            return redirect(url_for("main.loans_list"))

        except Exception as exc:
            db.session.rollback()
            flash(f"Loan could not be issued: {exc}", "danger")
            return render_template("loan_form.html",
                                   books=books, members=members,
                                   form_data=request.form)

    return render_template("loan_form.html",
                           books=books, members=members, form_data={})


@bp.route("/loans/<int:loan_id>/return", methods=["POST"])
def loan_return(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.ReturnDate is not None:
        flash("This loan has already been returned.", "info")
    else:
        loan.ReturnDate = date.today()
        db.session.commit()
        flash(f"Returned '{loan.book.Title}' from {loan.member.full_name}.",
              "success")
    return redirect(url_for("main.loans_list"))


# ===========================================================================
# DASHBOARD  —  uses SQL aggregate functions COUNT, SUM, AVG
# ===========================================================================

@bp.route("/dashboard")
def dashboard():
    """Summary dashboard using COUNT, SUM, and AVG aggregate queries."""

    # ----- COUNT aggregates -----
    total_books = db.session.query(func.count(Book.BookID)).scalar() or 0
    total_authors = db.session.query(func.count(Author.AuthorID)).scalar() or 0
    total_genres = db.session.query(func.count(Genre.GenreID)).scalar() or 0
    total_members = db.session.query(func.count(Member.MemberID)).scalar() or 0
    total_loans = db.session.query(func.count(Loan.LoanID)).scalar() or 0
    active_loans = db.session.query(
        func.count(Loan.LoanID)
    ).filter(Loan.ReturnDate.is_(None)).scalar() or 0
    returned_loans = total_loans - active_loans

    # ----- AVG aggregate: average loan duration (returned loans only) -----
    avg_days_raw = db.session.query(
        func.avg(func.julianday(Loan.ReturnDate) - func.julianday(Loan.LoanDate))
    ).filter(Loan.ReturnDate.isnot(None)).scalar()
    avg_loan_days = round(float(avg_days_raw), 1) if avg_days_raw else 0

    # ----- SUM aggregate: total reading days across all returned loans -----
    sum_days_raw = db.session.query(
        func.sum(func.julianday(Loan.ReturnDate) - func.julianday(Loan.LoanDate))
    ).filter(Loan.ReturnDate.isnot(None)).scalar()
    total_reading_days = int(float(sum_days_raw)) if sum_days_raw else 0

    # ----- COUNT + GROUP BY + ORDER BY + LIMIT: top borrowed books -----
    top_books = (
        db.session.query(
            Book.Title,
            Author.AuthorName,
            func.count(Loan.LoanID).label("loan_count"),
        )
        .join(Loan, Book.BookID == Loan.BookID)
        .join(Author, Book.AuthorID == Author.AuthorID)
        .group_by(Book.BookID, Book.Title, Author.AuthorName)
        .order_by(func.count(Loan.LoanID).desc())
        .limit(5)
        .all()
    )

    # ----- Most active members -----
    top_members = (
        db.session.query(
            Member.MemberID,
            Member.FirstName,
            Member.LastName,
            func.count(Loan.LoanID).label("loan_count"),
        )
        .join(Loan, Member.MemberID == Loan.MemberID)
        .group_by(Member.MemberID, Member.FirstName, Member.LastName)
        .order_by(func.count(Loan.LoanID).desc())
        .limit(5)
        .all()
    )

    # ----- Books per genre (COUNT + GROUP BY) -----
    genre_stats = (
        db.session.query(
            Genre.GenreName,
            func.count(Book.BookID).label("book_count"),
        )
        .outerjoin(Book, Genre.GenreID == Book.GenreID)
        .group_by(Genre.GenreID, Genre.GenreName)
        .order_by(func.count(Book.BookID).desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_authors=total_authors,
        total_genres=total_genres,
        total_members=total_members,
        total_loans=total_loans,
        active_loans=active_loans,
        returned_loans=returned_loans,
        avg_loan_days=avg_loan_days,
        total_reading_days=total_reading_days,
        top_books=top_books,
        top_members=top_members,
        genre_stats=genre_stats,
    )


# ===========================================================================
# VALIDATION HELPERS
# ===========================================================================

def _validate_book_form(form):
    errors = []

    title = (form.get("title") or "").strip()
    if not title:
        errors.append("Title is required and cannot be empty.")
    elif len(title) > 200:
        errors.append("Title cannot be longer than 200 characters.")

    author_id_raw = form.get("author_id") or ""
    author_id = None
    if not author_id_raw:
        errors.append("Author is required.")
    else:
        try:
            author_id = int(author_id_raw)
            if not Author.query.get(author_id):
                errors.append("Selected author does not exist.")
        except ValueError:
            errors.append("Invalid author selection.")

    genre_id_raw = form.get("genre_id") or ""
    genre_id = None
    if genre_id_raw:
        try:
            genre_id = int(genre_id_raw)
            if not Genre.query.get(genre_id):
                errors.append("Selected genre does not exist.")
        except ValueError:
            errors.append("Invalid genre selection.")

    year_raw = (form.get("published_year") or "").strip()
    year = None
    if year_raw:
        try:
            year = int(year_raw)
            if year <= 0:
                errors.append("Published year must be a positive number.")
        except ValueError:
            errors.append("Published year must be a number.")

    return title, author_id, genre_id, year, errors


def _validate_member_form(form, existing_member_id=None):
    errors = []

    first_name = (form.get("first_name") or "").strip()
    if not first_name:
        errors.append("First name is required.")
    elif len(first_name) > 50:
        errors.append("First name cannot exceed 50 characters.")

    last_name = (form.get("last_name") or "").strip()
    if not last_name:
        errors.append("Last name is required.")
    elif len(last_name) > 50:
        errors.append("Last name cannot exceed 50 characters.")

    email = (form.get("email") or "").strip().lower()
    if not email:
        errors.append("Email is required.")
    elif len(email) > 100:
        errors.append("Email cannot exceed 100 characters.")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("Email must be a valid email address.")
    else:
        existing = Member.query.filter_by(Email=email).first()
        if existing and existing.MemberID != existing_member_id:
            errors.append(f"Email '{email}' is already used by another member.")

    join_date_raw = (form.get("join_date") or "").strip()
    join_date = date.today()
    if join_date_raw:
        try:
            join_date = datetime.strptime(join_date_raw, "%Y-%m-%d").date()
            if join_date > date.today():
                errors.append("Join date cannot be in the future.")
        except ValueError:
            errors.append("Join date must be in YYYY-MM-DD format.")

    return first_name, last_name, email, join_date, errors