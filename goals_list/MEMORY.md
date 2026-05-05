# Goals & Plans App — Memory

## Overview
Single-table Flask app for tracking personal goals and plans.

## Stack
- Python / Flask
- SQLite3 (raw SQL)
- No JavaScript
- Jinja2 templates

## Data Model
**goals** table: id, title, description, category, priority, status, target_date, created_at, updated_at

## Field Options
- category: Personal, Work, Health, Finance, Education
- priority: High, Medium, Low
- status: Not Started, In Progress, Completed, On Hold

## Files
- app.py — routes and logic
- database.py — init_db(), get_db()
- goals.db — SQLite database (auto-created)
- static/style.css — all styles
- templates/ — base, index, add, edit, detail, confirm_delete

## Run
```
python app.py
```
Visit http://127.0.0.1:5000
