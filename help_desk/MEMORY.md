# Help Desk App — Memory

## Project Overview
A Flask-based help desk ticket management system with full CRUD operations.

## Stack
- **Backend**: Python / Flask
- **Database**: SQLite3 (`helpdesk.db`) via raw SQL
- **Frontend**: Jinja2 templates, no JavaScript
- **Styling**: `static/style.css`

## Data Model
**Table: `tickets`**
| Column      | Type    | Notes                              |
|-------------|---------|-------------------------------------|
| id          | INTEGER | PK, autoincrement                  |
| title       | TEXT    | Required                           |
| description | TEXT    |                                    |
| category    | TEXT    | Hardware / Software / Network / Account / Other |
| priority    | TEXT    | Low / Medium / High / Critical     |
| status      | TEXT    | Open / In Progress / Resolved / Closed |
| assigned_to | TEXT    |                                    |
| created_at  | TEXT    | YYYY-MM-DD HH:MM                   |
| updated_at  | TEXT    | YYYY-MM-DD HH:MM                   |

## Routes
| Route                      | Method   | Purpose              |
|----------------------------|----------|----------------------|
| `/`                        | GET      | Dashboard + ticket list (filterable) |
| `/ticket/new`              | GET/POST | Create ticket        |
| `/ticket/<id>`             | GET      | View ticket detail   |
| `/ticket/<id>/edit`        | GET/POST | Edit ticket          |
| `/ticket/<id>/delete`      | GET/POST | Confirm & delete     |

## Setup
```bash
cd helpdesk
python init_db.py
python app.py
```
Then open http://127.0.0.1:5000

## Files
- `app.py` — Flask app + routes
- `init_db.py` — DB schema initialization
- `templates/base.html` — Base layout
- `templates/index.html` — Dashboard
- `templates/new.html` — Create form
- `templates/view.html` — Ticket detail
- `templates/edit.html` — Edit form
- `templates/confirm_delete.html` — Delete confirmation
- `static/style.css` — All styles
