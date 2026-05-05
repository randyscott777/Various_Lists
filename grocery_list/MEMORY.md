# Grocery List App — Memory

## Overview
Flask-based grocery shopping list with full CRUD, SQLite3 persistence, and no JavaScript.

## Stack
- **Backend:** Python / Flask
- **Database:** SQLite3 (`grocery.db`) with raw SQL
- **Frontend:** Jinja2 templates, no JavaScript
- **Styles:** `static/style.css`

## Database
Table: `items`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | autoincrement |
| name | TEXT | required |
| category | TEXT | one of 10 categories |
| quantity | REAL | default 1 |
| unit | TEXT | e.g. lbs, ea, pkg |
| is_bought | INTEGER | 0=needed, 1=in cart |
| notes | TEXT | optional |
| created_at | DATETIME | auto |

## Routes
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Dashboard with filter & sort |
| `/add` | GET/POST | Add item |
| `/edit/<id>` | GET/POST | Edit item |
| `/toggle/<id>` | POST | Toggle bought status |
| `/delete/<id>` | GET | Delete confirmation |
| `/delete/<id>/confirm` | POST | Execute delete |
| `/clear_bought` | POST | Remove all bought items |

## Categories
Produce, Dairy, Meat, Bakery, Frozen, Beverages, Snacks, Pantry, Household, Other

## Running
```
cd grocery_app
python app.py
```
Then open http://127.0.0.1:5000
