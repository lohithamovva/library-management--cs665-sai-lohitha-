-- =====================================================
-- Library Management System — 3NF Schema
-- Project 3, CS665
-- Final normalized schema (5 tables)
-- Target database: SQLite (also compatible with MySQL/PostgreSQL with minor edits)
-- =====================================================

-- Drop tables in reverse dependency order to allow clean re-creation
DROP TABLE IF EXISTS Loans;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Members;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Authors;

-- =====================================================
-- Authors: extracted from original Books.Author column
-- =====================================================
CREATE TABLE Authors (
    AuthorID    INTEGER PRIMARY KEY AUTOINCREMENT,
    AuthorName  VARCHAR(150) NOT NULL UNIQUE
);

-- =====================================================
-- Genres: extracted from original Books.Genre column
-- =====================================================
CREATE TABLE Genres (
    GenreID    INTEGER PRIMARY KEY AUTOINCREMENT,
    GenreName  VARCHAR(50) NOT NULL UNIQUE
);

-- =====================================================
-- Books: now references Authors and Genres via FK
-- =====================================================
CREATE TABLE Books (
    BookID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Title          VARCHAR(200) NOT NULL,
    AuthorID       INTEGER NOT NULL,
    GenreID        INTEGER,
    PublishedYear  INTEGER CHECK (PublishedYear > 0),
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID),
    FOREIGN KEY (GenreID)  REFERENCES Genres(GenreID)
);

-- =====================================================
-- Members: unchanged from original (already in 3NF)
-- =====================================================
CREATE TABLE Members (
    MemberID   INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName  VARCHAR(50)  NOT NULL,
    LastName   VARCHAR(50)  NOT NULL,
    JoinDate   DATE         NOT NULL,
    Email      VARCHAR(100) NOT NULL UNIQUE
);

-- =====================================================
-- Loans: removed Status column (was a calculated value).
-- Status is now computed in the application layer.
-- Surrogate PK LoanID replaces the old composite PK.
-- =====================================================
CREATE TABLE Loans (
    LoanID      INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID      INTEGER NOT NULL,
    MemberID    INTEGER NOT NULL,
    LoanDate    DATE    NOT NULL,
    ReturnDate  DATE,
    FOREIGN KEY (BookID)   REFERENCES Books(BookID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    UNIQUE (BookID, MemberID, LoanDate)
);

-- =====================================================
-- Seed data — sample data for testing the app
-- =====================================================

INSERT INTO Authors (AuthorName) VALUES
('F. Scott Fitzgerald'),
('George Orwell'),
('Stephen Hawking'),
('J.R.R. Tolkien'),
('Isaac Asimov'),
('Yuval Noah Harari'),
('Frank Herbert'),
('James Clear'),
('Agatha Christie'),
('Stephen King');

INSERT INTO Genres (GenreName) VALUES
('Fiction'),
('Dystopian'),
('Science'),
('Fantasy'),
('Sci-Fi'),
('History'),
('Self-Help'),
('Mystery'),
('Horror');

INSERT INTO Books (Title, AuthorID, GenreID, PublishedYear) VALUES
('The Great Gatsby',              1, 1, 1925),
('1984',                          2, 2, 1949),
('A Brief History of Time',       3, 3, 1988),
('The Hobbit',                    4, 4, 1937),
('Foundation',                    5, 5, 1951),
('Sapiens',                       6, 6, 2011),
('Dune',                          7, 5, 1965),
('Atomic Habits',                 8, 7, 2018),
('Murder on the Orient Express',  9, 8, 1934),
('The Shining',                  10, 9, 1977);

INSERT INTO Members (FirstName, LastName, JoinDate, Email) VALUES
('Alice',   'Johnson', '2024-01-15', 'alice.johnson@example.com'),
('Bob',     'Smith',   '2024-02-20', 'b.smith78@provider.net'),
('Charlie', 'Davis',   '2024-03-10', 'charlie.davis.edu@university.edu'),
('Diana',   'Prince',  '2024-05-05', 'diana.prince.workspace@company.com');

INSERT INTO Loans (BookID, MemberID, LoanDate, ReturnDate) VALUES
(1, 1, '2026-01-01', '2026-01-10'),
(2, 2, '2026-01-05', '2026-01-20'),
(1, 1, '2026-02-01', NULL),
(3, 3, '2026-02-02', '2026-02-10'),
(4, 4, '2026-01-10', '2026-01-15'),
(7, 1, '2026-02-05', NULL),
(9, 2, '2026-02-08', NULL);