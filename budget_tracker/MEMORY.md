# Budget App - Memory

## Project Overview
Flask-based budget tracker for managing income and expense items.

## Stack
- Python / Flask
- SQLite3 (budget.db) with raw SQL
- No JavaScript — pure HTML/CSS

## Data Model
Table: `budget_items`
- id, name, amount, category, type (income/expense), date, notes

## Categories
Education, Entertainment, Food, Healthcare, Housing, Income, Transport, Utilities, Other

## Features
- Dashboard with summary cards (total income, total expense, balance)
- Filter by: category, type, date range
- Sort by: category (then date DESC within each category)
- CRUD: add, edit, delete (with confirmation)

## File Structure
```
budget_app/
├── app.py
├── budget.db          (auto-created on first run)
├── MEMORY.md
├── templates/
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   └── confirm_delete.html
└── static/
    └── style.css
```

## Run
```
cd budget_app
python app.py
```
Then open http://127.0.0.1:5000
