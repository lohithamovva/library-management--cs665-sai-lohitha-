# Library Management System

A full-stack Python web application for managing a small library — its books, members, and loan transactions. Built as Project 3 for CS665 (Wichita State University).

**Author:** Sai Lohitha Movva
**Course:** CS665 — Project 3

---

## What this app does

The Library Management System lets a librarian:

- **Manage the book catalog** — add, edit, and delete books, with each book tied to an Author and a Genre.
- **Manage members** — register members, edit their profiles, and view each member's complete loan history.
- **Issue and return loans** — issuing a loan runs as a single SQL transaction that verifies the book is available and the member is below the active-loan limit. If any check fails, the whole operation is rolled back.
- **View a dashboard** — see real-time aggregate statistics computed in SQL: total books, members, and loans; average loan duration; total cumulative reading days; the top 5 most-borrowed books; the most active members; and the distribution of books per genre.

---

## Tech Stack

- **Python 3** (tested on 3.14.5)
- **Flask** — backend web framework
- **SQLAlchemy** — ORM for the relational database
- **SQLite** — default development database (the schema is portable to MySQL or PostgreSQL with minimal changes)
- **HTML5 + Bootstrap 5** — frontend
- **Jinja2** — Flask's templating engine
- **Git** — version control

---

## Database Design

The database is in **3rd Normal Form (3NF)** with 5 tables. The original Project 1 design had 3 tables (Books, Members, Loans) and contained several anomalies and a transitive dependency in the Loans.Status column. The full normalization audit is in [NORMALIZATION.md](NORMALIZATION.md). The final tables are:

| Table | Purpose |
|---|---|
| `Authors` | One row per author (extracted from the old Books.Author column) |
| `Genres` | One row per genre (extracted from the old Books.Genre column) |
| `Books` | Title, year, plus foreign keys to Authors and Genres |
| `Members` | First name, last name, email (UNIQUE), join date |
| `Loans` | Junction table between Books and Members with LoanDate and ReturnDate |

The full SQL schema (CREATE TABLE statements + sample seed data) is in [schema.sql](schema.sql).

---

## Installation

### Prerequisites
- Python 3 (3.10 or later recommended)
- Git
- A modern web browser

### 1. Clone the repository
```bash
git clone <YOUR-REPO-URL>
cd stack_outline_app
```

### 2. Create and activate a virtual environment

On Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Database Setup

There are two equivalent ways to create the database:

**Option A — automatic (default).** Just run the app. SQLAlchemy will create the SQLite database file at `instance/app.db` from the models, and the seed function in `app/__init__.py` will populate it with sample data on first launch.

**Option B — explicit SQL.** If you prefer to use the raw SQL schema (for example, when grading the normalization deliverable), run `schema.sql` against your database of choice:

```bash
# SQLite
sqlite3 instance/app.db < schema.sql
```

The `schema.sql` file contains the `CREATE TABLE` statements and a small set of `INSERT` statements that mirror the Python seed function.

---

## Running the app

With the virtual environment activated:

```bash
python run.py
```

Open your browser to: **http://127.0.0.1:5000**

### Main pages
- `/` — **Books** catalog with Add / Edit / Delete buttons
- `/members` — **Members** list (click a member to view their loan history)
- `/loans` — **Loans** list with Return button; "+ Issue Loan" runs the transaction
- `/dashboard` — **Summary statistics** computed with COUNT, SUM, and AVG

### To stop the server
Press `Ctrl + C` in the terminal.

---

## Project structure



---

## Assignment Requirements — Checklist

| Requirement | Where it lives |
|---|---|
| Multi-table CRUD (≥ 2 tables) | `routes.py` — Books and Members both have full CRUD; Loans support create / return / list |
| Many-to-Many relationship displayed | Member detail page (`member_detail.html`) shows each member's full loan history |
| Transaction logic | `loan_new` in `routes.py` — multi-step verification + insert wrapped in try/except with `db.session.rollback()` on failure |
| Server-side validation | `_validate_book_form` and `_validate_member_form` in `routes.py` |
| Summary dashboard with COUNT/SUM/AVG | `/dashboard` route + `dashboard.html`; uses `func.count`, `func.avg`, `func.sum` |
| 5+ incremental Git commits | See `git log` |
| `.gitignore` excludes venv/, __pycache__/, .env | Yes |
| `README.md` | This file |
| `NORMALIZATION.md` | Present |
| `AI_LOG.md` | Present |
| `.sql` schema file | `schema.sql` |