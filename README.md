# Workflow Management System (CLI)

A portfolio-ready **CRUD CLI app** that manages tasks using **SQLite** persistence.
Includes filtering, sorting, tags (many-to-many), and optional tests.

## Features
- Create / Read / Update / Delete tasks
- Status: `todo`, `in_progress`, `done`
- Priority 1–5
- Tags for tasks (many-to-many)
- Search + filter + sort
- SQLite persistence (`workflow.db` by default)
- Small test suite (pytest)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
