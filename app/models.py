"""SQLAlchemy models for the Library Management System.

This file defines the 5 tables in our 3NF schema:
    - Authors
    - Genres
    - Books      (FK to Authors and Genres)
    - Members
    - Loans      (junction table: many-to-many between Books and Members)

The old `Status` column from Project 1 was removed because it violated 3NF.
Status is now computed at runtime via the `status` property on the Loan model.
"""
from datetime import date
from app.extensions import db


class Author(db.Model):
    __tablename__ = "Authors"

    AuthorID = db.Column(db.Integer, primary_key=True)
    AuthorName = db.Column(db.String(150), nullable=False, unique=True)

    # One author can write many books
    books = db.relationship("Book", back_populates="author")

    def __repr__(self):
        return f"<Author {self.AuthorName}>"


class Genre(db.Model):
    __tablename__ = "Genres"

    GenreID = db.Column(db.Integer, primary_key=True)
    GenreName = db.Column(db.String(50), nullable=False, unique=True)

    # One genre categorizes many books
    books = db.relationship("Book", back_populates="genre")

    def __repr__(self):
        return f"<Genre {self.GenreName}>"


class Book(db.Model):
    __tablename__ = "Books"

    BookID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    AuthorID = db.Column(db.Integer, db.ForeignKey("Authors.AuthorID"), nullable=False)
    GenreID = db.Column(db.Integer, db.ForeignKey("Genres.GenreID"))
    PublishedYear = db.Column(db.Integer)

    # Relationships
    author = db.relationship("Author", back_populates="books")
    genre = db.relationship("Genre", back_populates="books")
    loans = db.relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint("PublishedYear > 0", name="check_year_positive"),
    )

    @property
    def is_available(self):
        """A book is available if it has no unreturned loans."""
        return not any(loan.ReturnDate is None for loan in self.loans)

    def __repr__(self):
        return f"<Book {self.Title}>"


class Member(db.Model):
    __tablename__ = "Members"

    MemberID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    JoinDate = db.Column(db.Date, nullable=False, default=date.today)
    Email = db.Column(db.String(100), nullable=False, unique=True)

    # One member can have many loans
    loans = db.relationship("Loan", back_populates="member", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.FirstName} {self.LastName}"

    def __repr__(self):
        return f"<Member {self.full_name}>"


class Loan(db.Model):
    __tablename__ = "Loans"

    LoanID = db.Column(db.Integer, primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey("Books.BookID"), nullable=False)
    MemberID = db.Column(db.Integer, db.ForeignKey("Members.MemberID"), nullable=False)
    LoanDate = db.Column(db.Date, nullable=False, default=date.today)
    ReturnDate = db.Column(db.Date, nullable=True)

    # Relationships
    book = db.relationship("Book", back_populates="loans")
    member = db.relationship("Member", back_populates="loans")

    __table_args__ = (
        db.UniqueConstraint("BookID", "MemberID", "LoanDate",
                            name="uq_loan_book_member_date"),
    )

    @property
    def is_returned(self):
        return self.ReturnDate is not None

    @property
    def days_kept(self):
        end = self.ReturnDate if self.ReturnDate else date.today()
        return (end - self.LoanDate).days

    @property
    def status(self):
        """Computed status that replaces the old (3NF-violating) Status column."""
        if not self.is_returned:
            return "ON LOAN"
        if self.days_kept > 14:
            return "LATE RETURNED"
        return "RETURNED ON TIME"

    def __repr__(self):
        return f"<Loan id={self.LoanID}>"