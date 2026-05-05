# Inventory App — Memory

## Overview
Flask-based household inventory tracker with SQLite3 persistence.

## Stack
- Python / Flask
- SQLite3 (raw SQL, no ORM)
- No JavaScript
- Jinja2 templates + CSS

## Database
- File: `inventory.db` (auto-created on first run)
- Table: `items`
  - id, name, category, location, quantity, condition, purchase_date, purchase_price, notes

## Features
- Dashboard with stat cards (total, showing, categories, locations)
- Filter by: category, location, condition
- Sort by: any field (default: location, ascending)
- CRUD: add, edit, delete (with confirmation)

## Routes
| Method | Route | Purpose |
|--------|-------|---------|
| GET | / | Dashboard |
| GET/POST | /add | Add item |
| GET/POST | /edit/<id> | Edit item |
| GET/POST | /delete/<id> | Confirm + delete |

## Run
```
cd inventory_app
python app.py
```
App runs at http://127.0.0.1:5000
