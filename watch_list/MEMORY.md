# Watch List App — Memory

## Overview
Flask web app for tracking TV shows, movies, and live events.

## Stack
- Python / Flask
- SQLite3 (raw SQL, `watchlist.db` in app root)
- No JavaScript
- Jinja2 templates + CSS only

## Database
Table: `watchlist`
- id, title, type, genre, platform, status, rating, year, notes, date_added

## Key Features
- Dashboard with summary cards (totals by type and status)
- Filter by type, status, genre
- Sort by any field (asc/desc)
- CRUD: Add, View, Edit (confirmation on key field changes), Delete (confirmation page)

## Files
- app.py — Flask routes + DB init
- templates/base.html, index.html, add.html, edit.html, view.html, delete_confirm.html
- static/style.css — all styling (dark theme)
- watchlist.db — auto-created on first run

## Run
```
cd watchlist_app
python app.py
```
Visit http://127.0.0.1:5000
