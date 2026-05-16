# AI Assistance Log

---

## Entry 1 — Initial Project Setup
- **Tool:** Claude (Anthropic)
- **Prompt:** "Help me set up VSCode, Python, Git, GitHub, and clone the stack_outline_app starter repo on Windows."
- **AI Output:** Claude provided step-by-step Windows installation walkthroughs for VSCode, Python 3.14.5, and Git 2.54. It helped me clone the starter repo into VSCode, create and activate a virtual environment, install requirements.txt dependencies, and verify the Flask app runs at http://127.0.0.1:5000.
- **My Modification:** I performed every installation myself on my own machine and verified each step worked before proceeding.

## Entry 2 — Choosing the Database
- **Tool:** Claude (Anthropic)
- **Prompt:** "I shared Project 1 (Library DB) and Project 2 (Book Club DB). Pick whichever suits the assignment."
- **AI Output:** Claude analyzed both databases and recommended Project 1 (Library Management) because it has 3 tables, a natural many-to-many relationship via the Loans junction table, and satisfies all assignment requirements with less code than the 7-table Book Club DB.
- **My Modification:** I reviewed the recommendation and agreed to use the Library database as the basis for Project 3.

## Entry 3 — Normalization Analysis and Report
- **Tool:** Claude (Anthropic)
- **Prompt:** "Walk me through normalizing my Library DB to 3NF and create the deliverables."
- **AI Output:** Claude identified update anomalies (Author/Genre duplication), insertion anomalies (cannot record an author without a book), deletion anomalies (deleting the last book by an author loses the author), and a transitive dependency (the Status column in Loans is calculated from ReturnDate and LoanDate). It proposed a 5-table 3NF schema (Authors, Genres, Books, Members, Loans) and generated the NORMALIZATION.md report and schema.sql file.
- **My Modification:** I reviewed the report for accuracy, added my name as the author of the report, and verified that the proposed schema preserves the original data semantics from Project 1.


## Entry 4 — Building the Data Layer and Books Listing Page (Stage 1)
- **Tool:** Claude (Anthropic)
- **Prompt:** "Ready for Part 2 — start building the Flask app on top of my 3NF schema."
- **AI Output:** Claude wrote replacement code for app/models.py (5 SQLAlchemy models for Authors, Genres, Books, Members, Loans with proper relationships and a computed `status` property that replaces the 3NF-violating Status column), app/__init__.py (Flask factory with a one-time seed function), app/routes.py (Blueprint with an index route), and updated base.html and index.html templates to display all 10 books with author/genre/status badges.
- **My Modification:** Replaced each file's contents in VSCode, deleted instance/app.db so a fresh database would be generated, restarted Flask, and verified the Books page renders correctly at http://127.0.0.1:5000 with proper relationships and computed availability.

---


## Entry 7 — Stage 3: Loans CRUD with Transaction Logic
- **Tool:** Claude (Anthropic)
- **Prompt:** "Stage 3B — Loans CRUD and the transaction."
- **AI Output:** Claude added Loans routes to app/routes.py: loans_list, loan_new (transactional), and loan_return. The loan_new view wraps multiple steps in a try/except/db.session.rollback() block: verify book exists, verify book is available, verify member exists, verify member is below the 3-active-loan limit, then insert the Loan row and commit atomically. Any failure rolls back the entire transaction. Created loans.html (table with status badges + Return button) and loan_form.html (Issue Loan form with disabled-option styling for unavailable books).
- **My Modification:** I replaced/created each file, tested issuing a loan to an available book (success), tested issuing a loan to an already-borrowed book (rejected by disabled UI), tested marking a loan as returned (status changes correctly), and verified the transaction rolls back cleanly on failure.

## Entry 8 — Stage 4: Dashboard with SQL Aggregates
- **Tool:** Claude (Anthropic)
- **Prompt:** "Stage 4 — build a dashboard with COUNT, SUM, AVG aggregates."
- **AI Output:** Claude added a /dashboard route to app/routes.py using sqlalchemy.func.count, func.avg, and func.sum: COUNT totals for books/authors/genres/members/loans/active loans; AVG loan duration via func.avg(julianday(ReturnDate) - julianday(LoanDate)); SUM total reading days; COUNT + GROUP BY + ORDER BY + LIMIT for top 5 most-borrowed books and top 5 most-active members; COUNT + GROUP BY for books-per-genre breakdown. Created dashboard.html with Bootstrap cards displaying each metric, and updated base.html to enable the Dashboard nav link.
- **My Modification:** I pasted both files into VSCode, verified the dashboard renders all stat cards with sensible values from the seeded data, and confirmed the Top Books / Top Members / Genre breakdown tables populate from the actual loan history.

## Notes
- Additional entries will be added as the project progresses through CRUD route implementation, dashboard development, validation logic, and final documentation.