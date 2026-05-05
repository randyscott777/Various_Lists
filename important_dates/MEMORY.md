# Important Dates – Project Memory

## Purpose
Flask web app to track important dates (birthdays, anniversaries, holidays, etc.).

## Stack
- Python / Flask
- SQLite3 (raw SQL) — `important_dates.db`
- No JavaScript
- All CSS in `static/style.css`

## Schema
```sql
CREATE TABLE important_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    date DATE NOT NULL,
    category TEXT NOT NULL,   -- birthday | anniversary | holiday | other
    notes TEXT
);
```

## Routes
| Method | Route | Purpose |
|--------|-------|---------|
| GET/POST | `/` | Dashboard with filter & sort (persisted in session) |
| GET/POST | `/add` | Add new date |
| GET/POST | `/edit/<id>` | Edit existing date |
| GET/POST | `/delete/<id>` | Confirm & delete |

## Filter / Sort
- Filter by: category, month
- Sort by: date, title, category (asc/desc)
- State persisted in Flask session

## Running
```bash
python app.py
```
App runs at http://127.0.0.1:5000
