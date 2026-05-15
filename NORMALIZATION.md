# Database Normalization Report

**Project:** Library Management System (Project 3 Database)
**Author:** SAI LOHITHA MOVVA
**Course:** CS665 — Project 3
**Source:** Decomposition of the database originally designed in Project 1.

This document describes the normalization audit of the original Library Management database designed in Project 1, the anomalies discovered in its structure, the step-by-step decomposition into Third Normal Form (3NF), and the final relational schema used by the Flask application.

---

## 1. Original Schema (Before Normalization)

The original database from Project 1 contained three tables:

### `Books`
| Column | Type | Notes |
|---|---|---|
| BookID | INT | Primary Key |
| Title | VARCHAR(100) | |
| Author | VARCHAR(100) | Stored as free-text string |
| Genre | VARCHAR(50) | Stored as free-text string |
| PublishedYear | INT | |

### `Members`
| Column | Type | Notes |
|---|---|---|
| MemberID | INT | Primary Key |
| FirstName | VARCHAR(50) | |
| LastName | VARCHAR(50) | |
| JoinDate | DATE | |
| Email | VARCHAR(100) | UNIQUE constraint |

### `Loans`
| Column | Type | Notes |
|---|---|---|
| BookID | INT | Composite PK + FK → Books |
| MemberID | INT | Composite PK + FK → Members |
| LoanDate | DATE | Composite PK |
| ReturnDate | DATE | Nullable |
| Status | VARCHAR(20) | Added via ALTER; "LATE RETURNED" when DATEDIFF(ReturnDate, LoanDate) > 14 |

---

## 2. Original Functional Dependencies

A functional dependency `X → Y` means "if you know X, you can uniquely determine Y."

### Books
- `BookID → Title, Author, Genre, PublishedYear`

### Members
- `MemberID → FirstName, LastName, JoinDate, Email`
- `Email → MemberID` (because Email is UNIQUE — it also uniquely identifies a member)

### Loans
- `(BookID, MemberID, LoanDate) → ReturnDate, Status`
- `(LoanDate, ReturnDate) → Status` ⚠️ Transitive dependency — Status depends on non-key columns.

---

## 3. Anomaly Identification

### 3.1 Update Anomaly
- Author "J.R.R. Tolkien" would be duplicated across every book he wrote. Correcting a typo requires updating every row; missing one creates inconsistent data.
- The same problem applies to Genre: the string "Sci-Fi" appears in multiple rows and any typo introduces inconsistency.
- For Loans.Status: if a librarian corrects ReturnDate later, the Status column may not be re-evaluated, causing it to disagree with the calculated value.

### 3.2 Insertion Anomaly
- A new author cannot be recorded in the database unless at least one book by that author is added. Authors only exist as a column inside Books rows.
- The same applies to Genre: a genre such as "Graphic Novel" cannot exist until a book in that genre is acquired.

### 3.3 Deletion Anomaly
- Removing the last book by a given author from Books accidentally destroys all record of that author.
- Removing the last book of a given genre destroys all record of that genre.

### 3.4 Transitive Dependency (3NF Violation)
- Loans.Status is derived from Loans.ReturnDate and Loans.LoanDate via DATEDIFF. This is a textbook 3NF violation: Status is functionally dependent on non-key attributes.

---

## 4. Decomposition Steps

### Step 4.1 — Extract Author into its own table
Create a new Authors table and replace Books.Author (VARCHAR) with Books.AuthorID (foreign key).
### Step 4.2 — Extract Genre into its own table
Create a new Genres table and replace Books.Genre (VARCHAR) with Books.GenreID (foreign key).



### Step 4.3 — Remove the calculated Status column from Loans
Drop the Status column. Replace the composite primary key with a surrogate primary key LoanID for cleaner ORM modeling, while preserving uniqueness via a UNIQUE constraint on (BookID, MemberID, LoanDate).


### Step 4.4 — Confirm Members is already in 3NF
The Members table has no transitive dependencies and remains unchanged.

---

## 5. Final Relational Schema (3NF)

### Authors
| Column | Type | Constraints |
|---|---|---|
| AuthorID | INTEGER | PRIMARY KEY |
| AuthorName | VARCHAR(150) | NOT NULL, UNIQUE |

### Genres
| Column | Type | Constraints |
|---|---|---|
| GenreID | INTEGER | PRIMARY KEY |
| GenreName | VARCHAR(50) | NOT NULL, UNIQUE |

### Books
| Column | Type | Constraints |
|---|---|---|
| BookID | INTEGER | PRIMARY KEY |
| Title | VARCHAR(200) | NOT NULL |
| AuthorID | INTEGER | NOT NULL, FOREIGN KEY → Authors(AuthorID) |
| GenreID | INTEGER | FOREIGN KEY → Genres(GenreID) |
| PublishedYear | INTEGER | CHECK (PublishedYear > 0) |

### Members
| Column | Type | Constraints |
|---|---|---|
| MemberID | INTEGER | PRIMARY KEY |
| FirstName | VARCHAR(50) | NOT NULL |
| LastName | VARCHAR(50) | NOT NULL |
| JoinDate | DATE | NOT NULL |
| Email | VARCHAR(100) | NOT NULL, UNIQUE |

### Loans
| Column | Type | Constraints |
|---|---|---|
| LoanID | INTEGER | PRIMARY KEY |
| BookID | INTEGER | NOT NULL, FOREIGN KEY → Books(BookID) |
| MemberID | INTEGER | NOT NULL, FOREIGN KEY → Members(MemberID) |
| LoanDate | DATE | NOT NULL |
| ReturnDate | DATE | NULL allowed (NULL = still on loan) |

Additional constraint: UNIQUE(BookID, MemberID, LoanDate) on Loans.

### Relationships
- **Authors → Books**: One-to-many. One author can write many books.
- **Genres → Books**: One-to-many. One genre can categorize many books.
- **Books ↔ Members**: Many-to-many via the Loans junction table.

---

## 6. Verification — Why this is in 3NF

A relation is in 3NF if every non-trivial functional dependency X → A has X as a superkey or A as a prime attribute. All five tables satisfy this condition; the transitive dependency on Status has been eliminated, and Author and Genre duplication has been resolved by extracting them into their own tables.
