# To-Do List App — Memory

## Overview
Flask web app for managing a personal to-do list. No JavaScript. SQLite3 for persistence.

## Created
2026-04-06

## Tech Stack
- Python / Flask
- SQLite3 (raw SQL, no ORM)
- Jinja2 templates
- CSS only (no JavaScript)

## Database
- Path: `C:\Users\randy\OneDrive\VisualStudioCode\Various_Lists\todos_app\todos.db`
- Table: `todos`
  - id (INTEGER PK AUTOINCREMENT)
  - title (TEXT NOT NULL)
  - description (TEXT)
  - status (TEXT) — Not Started, In Progress, Completed, On Hold
  - priority (TEXT) — Low, Medium, High, Critical
  - due_date (TEXT)
  - created_at (TEXT, localtime default)

## Routes
| Route | Method | Purpose |
|---|---|---|
| / | GET | Dashboard — filter/sort to-dos |
| /add | GET/POST | Add new to-do |
| /edit/<id> | GET/POST | Edit existing to-do |
| /delete/<id> | GET/POST | Delete confirmation + delete |

## Features
- Summary cards showing count per status
- Filter by status and/or priority (persisted in session)
- Sort by any field, ascending/descending (persisted in session)
- Monday.com-style color-coded status and priority badges
- Delete requires confirmation page

## Run
```
cd todos_app
python app.py
```
Visit http://127.0.0.1:5000
