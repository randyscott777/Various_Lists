# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A collection of independent Flask web applications, each in its own subdirectory. Every app follows the same pattern: Python + Flask + SQLite3 + Jinja2 templates, no JavaScript.

## Running Any App

```bash
cd <app_directory>
python app.py
```

Then open http://127.0.0.1:5000. Each app runs independently on port 5000 — only one can run at a time unless ports are changed.

## Common Architecture Pattern

Every app in this repo follows this structure:

- **`app.py`** — Flask app, route handlers, DB init, and `if __name__ == '__main__': app.run(debug=True)`
- **`<name>.db`** — SQLite3 database (created automatically on first run via `init_db()`)
- **`templates/`** — Jinja2 HTML templates; most apps have `base.html`, `index.html`, `add.html`, `edit.html`, `confirm_delete.html`
- **`static/style.css`** — App-specific CSS (no JS)
- **`MEMORY.md`** — Per-app memory file documenting schema, routes, and features

### DB Connection Pattern

Two patterns are used across apps:

**Flask `g` object pattern** (preferred for new apps):
```python
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
```

**Simple per-request connection** (used in some apps):
```python
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

Use `conn.row_factory = sqlite3.Row` so template code can access columns by name.

### DB Path Convention

Prefer `os.path.join(os.path.dirname(os.path.abspath(__file__)), '<name>.db')` over hardcoded absolute paths — some older apps use hardcoded paths that should be updated when touched.

### Delete Confirmation Pattern

All delete routes show a confirmation page before executing. Typically:
- `GET /delete/<id>` → renders `confirm_delete.html`
- `POST /delete/<id>/confirm` → executes delete and redirects

### Filter & Sort Pattern

Index routes accept query params (`filter_*`, `sort_by`, `sort_dir`) and build queries dynamically using a whitelist of valid sort fields. Some apps persist filter/sort state in Flask session.

## Apps in This Repo

| Directory | Purpose | Notable Features |
|---|---|---|
| `grocery_list` | Shopping list | Toggle bought status, category filter, bulk clear |
| `todos_list` | Personal to-dos | Status/priority badges, session-persisted filters |
| `budget_tracker` | Expense tracking | Categories, chart of accounts integration |
| `project_manager` | Projects + tasks | Two-table schema with FK, `database.py` + `schema.sql` split |
| `help_desk` | Support tickets | `init_db.py` separate from `app.py` |
| `family_tree` | Family relationships | Self-referencing table (father_id, mother_id, spouse_id) |
| `spiritual_journal` | Journal entries | Category color-coding, session filters |
| `goals_list` | Goal tracking | |
| `meals_list` | Meal planning | |
| `passwords_list` | Password storage | |
| `prescriptions_list` | Medication tracking | |
| `household_inventory` | Home inventory | |
| `important_dates` | Date reminders | |
| `travel_list` | Trip planning | |
| `watch_list` | Watch/media list | |
| `images_list` | Image catalog | |
| `contacts_list` | Contact tracking | |
| `chart_of_accounts` | Account definitions | |
| `bucket_list` | Bucket list items | |
| `projects_3levels` | 3-tier project hierarchy | |

## When Creating a New App

1. Propose a plan before building
2. Create the subdirectory under `Various_Lists/`
3. Use `os.path.join(os.path.dirname(os.path.abspath(__file__)), ...)` for DB path
4. Enable `PRAGMA foreign_keys = ON` if using related tables
5. Create `MEMORY.md` in the app directory documenting schema and routes
6. Include filter and sort on the index route
7. Require confirmation before any delete
