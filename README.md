# Workflow Management System (CLI)

A modular command-line application for managing tasks and workflows, built in Python with SQLite persistence.  
This project emphasizes **software engineering fundamentals**, including clean architecture, relational data modeling, and maintainable design.

---

## Project Overview

The Workflow Management System provides a structured CLI for creating, managing, and querying tasks.  
All data is persisted locally using SQLite, enabling reliable state management across sessions.

The application is implemented as a **multi-module Python package**, reflecting real-world engineering practices rather than a single-script approach.

---

## Engineering Focus

This project demonstrates competency in:

- Translating functional requirements into a working software system
- Designing and implementing a relational database schema
- Applying separation of concerns across application layers
- Building robust command-line interfaces with input validation
- Writing readable, testable, and maintainable Python code

---

## Architecture & Design

The codebase is organized into clearly defined layers:

- **CLI Layer (`cli.py`)**  
  Handles argument parsing, command routing, and user-facing output

- **Service Layer (`services.py`)**  
  Encapsulates business logic and task operations

- **Data Layer (`db.py`)**  
  Manages SQLite connections, schema initialization, and transactions

- **Models (`models.py`)**  
  Defines typed representations of domain entities

- **Utilities (`utils.py`)**  
  Centralizes validation, normalization, and helper functions

This structure improves extensibility and mirrors patterns used in production Python tooling.

---

## Data Modeling

The application uses a normalized SQLite schema:

- Tasks stored in a primary table
- Tags stored independently
- A join table enabling **many-to-many relationships** between tasks and tags

Additional considerations:

- Foreign key constraints with cascading deletes
- Indexed columns for efficient filtering and sorting
- Explicit validation for task status and priority values

---

## Features

- Create, view, update, and delete tasks
- Task statuses: `todo`, `in_progress`, `done`
- Priority levels (1–5)
- Many-to-many task tagging
- Search, filter, and sort functionality
- Persistent local storage using SQLite
- Automated tests using `pytest`

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
